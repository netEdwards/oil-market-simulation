from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QMessageBox,
    QFrame,
)

from experiments.experiment import EXPERIMENTS_ROOT


class ViewExperimentsScreen(QWidget):
    def __init__(
        self,
        on_back: Callable[[], None] | None = None,
        on_view: Callable[[dict], None] | None = None,
        on_edit: Callable[[dict], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.on_back = on_back
        self.on_view = on_view
        self.on_edit = on_edit

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("Experiments Browser")
        title_font = title.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setSpacing(12)
        self.list_layout.setContentsMargins(8, 8, 8, 8)

        self.scroll.setWidget(self.list_container)
        root.addWidget(self.scroll)

        bottom_row = QHBoxLayout()
        bottom_row.addStretch()

        self.back_button = QPushButton("Back")
        self.refresh_button = QPushButton("Refresh")

        bottom_row.addWidget(self.refresh_button)
        bottom_row.addWidget(self.back_button)

        root.addLayout(bottom_row)

        self.back_button.clicked.connect(self._handle_back)
        self.refresh_button.clicked.connect(self.refresh)

    def refresh(self) -> None:
        self._clear_list()

        experiments = self._load_experiments()

        if not experiments:
            empty_label = QLabel("No experiments found.")
            empty_label.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(empty_label)
            self.list_layout.addStretch()
            return

        for experiment in experiments:
            card = self._build_experiment_card(experiment)
            self.list_layout.addWidget(card)

        self.list_layout.addStretch()

    def _clear_list(self) -> None:
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _load_experiments(self) -> list[dict]:
        """
        Scan experiments root for folders containing experiment.json.
        """
        results: list[dict] = []

        if not EXPERIMENTS_ROOT.exists():
            return results

        for folder in sorted(EXPERIMENTS_ROOT.iterdir()):
            if not folder.is_dir():
                continue

            metadata_path = folder / "experiment.json"
            if not metadata_path.exists():
                continue

            try:
                with metadata_path.open("r", encoding="utf-8") as f:
                    metadata = json.load(f)

                metadata["folder_path"] = str(folder)
                results.append(metadata)
            except Exception:
                continue

        return results

    def _build_experiment_card(self, experiment: dict) -> QWidget:
        if not experiment:
            print("No experiment in the card builder..")
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setFrameShadow(QFrame.Shadow.Raised)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        name_label = QLabel(experiment.get("name", "Unnamed Experiment"))
        name_font = name_label.font()
        name_font.setPointSize(13)
        name_font.setBold(True)
        name_label.setFont(name_font)

        description = experiment.get("description", "").strip()
        description_label = QLabel(description or "No description provided.")
        description_label.setWordWrap(True)

        layout.addWidget(name_label)
        layout.addWidget(description_label)

        action_row = QHBoxLayout()
        action_row.addStretch()

        view_button = QPushButton("View")
        edit_button = QPushButton("Edit")
        delete_button = QPushButton("Delete")

        view_button.clicked.connect(lambda: self._handle_view(experiment))
        edit_button.clicked.connect(lambda: self._handle_edit(experiment))
        delete_button.clicked.connect(lambda: self._handle_delete(experiment))

        action_row.addWidget(view_button)
        action_row.addWidget(edit_button)
        action_row.addWidget(delete_button)

        layout.addLayout(action_row)

        return card

    def _handle_back(self) -> None:
        if self.on_back:
            self.on_back()

    def _handle_view(self, experiment: dict) -> None:
        if not experiment:
            print("There is no experiment loaded.")
        if self.on_view:
            self.on_view(experiment)
            return

        QMessageBox.information(
            self,
            "Not Implemented",
            f'View is not implemented yet for "{experiment.get("name", "Experiment")}".',
        )

    def _handle_edit(self, experiment: dict) -> None:
        if self.on_edit:
            self.on_edit(experiment)
            return

        QMessageBox.information(
            self,
            "Not Implemented",
            f'Edit is not implemented yet for "{experiment.get("name", "Experiment")}".',
        )

    def _handle_delete(self, experiment: dict) -> None:
        experiment_name = experiment.get("name", "Experiment")
        folder_path = experiment.get("folder_path")

        if not folder_path:
            QMessageBox.critical(self, "Delete Failed", "Experiment folder path is missing.")
            return

        confirm = QMessageBox.question(
            self,
            "Delete Experiment",
            f'Are you sure you want to delete "{experiment_name}"?\n\nThis cannot be undone.',
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            shutil.rmtree(folder_path)
        except Exception as exc:
            QMessageBox.critical(self, "Delete Failed", str(exc))
            return

        self.refresh()