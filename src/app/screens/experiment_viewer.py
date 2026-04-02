from logging import root
from pathlib import Path
from typing import Callable


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
)

class ExperimentViewerScreen(QWidget):
    def __init__(self,
        on_back: Callable[[], None] | None = None,
        on_run: Callable[[dict], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.on_back = on_back
        self.on_run = on_run
        self.experiment: dict | None = None
        
        self.name_label = QLabel("")
        self.description_label = QLabel("")
        
        self._build_ui()
        self._connect_signals()
        
    def _populate(self) -> None:
        if not self.experiment:
            return
        
        self.name_label.setText(
            f'Name: {self.experiment.get("name", "Unamed Exeriment")}'
        )
        
        description = self.experiment.get("description", "No Description Provided.")
        self.description_label.setText(
            f'Description: {description or "No Description Provided."}'
        )

    def _build_ui(self) -> None:
        print("Building Experiment Viewer Screen")
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)
        self.title = QLabel("Experiment Viewer")
        title_font = self.title.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title.setFont(title_font)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(self.title)
        
        #Details card
        self.details_card = QFrame()
        self.details_card.setFrameShape(QFrame.Shape.StyledPanel)
        self.details_layout = QVBoxLayout(self.details_card)
        self.details_layout.setContentsMargins(16, 16, 16, 16)
        self.details_layout.setSpacing(16)
        
        
        self.name_label = QLabel("Name: ")
        self.description_label = QLabel("Description:")
        self.description_label.setWordWrap(True)
        
        self.details_layout.addWidget(self.name_label)
        self.details_layout.addWidget(self.description_label)
        
        root_layout.addWidget(self.details_card)
        
        root_layout.addStretch()
        
        button_row = QHBoxLayout()
        button_row.addStretch()
        
        self.run_button = QPushButton("Run Experiment")
        self.back_button = QPushButton("Back")
        
        button_row.addWidget(self.run_button)
        button_row.addWidget(self.back_button)
        
        root_layout.addLayout(button_row)
        
        
    def _connect_signals(self)-> None:
        self.back_button.clicked.connect(self._handle_back)
        self.run_button.clicked.connect(self._handle_run)
        
    def set_experiment(self, experiment: dict) -> None:
        self.experiment = experiment
        if not self.experiment:
            print("No experiment passed.")
            self.name_label.setText("Name: ")
            self.description_label.setText("Description: ")
            return
            
        self._populate()
        
    def _handle_back(self) -> None:
        if self.on_back:
            self.on_back()
        
    def _handle_run(self) -> None:
        if self.on_run and self.experiment:
            self.on_run(self.experiment)
        
        
        
        