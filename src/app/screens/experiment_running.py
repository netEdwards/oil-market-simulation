from turtle import st, title
from typing import Callable

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QProgressBar,
)


class ExperimentRunnningScreen(QWidget):
    def __init__(
        self,
        on_back: Callable[[dict], None] | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__()
        
        self.on_back = on_back
        self.experiment: dict | None = None
        
        self._build_ui()
        self._connect_signals()
        
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)
        
        self.title_label = QLabel("Experiment Running")
        title_font = self.title_label.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        root.addWidget(self.title_label)
        
        self.details_card = QFrame()
        self.details_card.setFrameShape(QFrame.Shape.StyledPanel)
        
        details_layout = QVBoxLayout(self.details_card)
        details_layout.setContentsMargins(16, 16, 16, 16)
        details_layout.setSpacing(16)
        
        self.name_label = QLabel("Name: ")
        self.description_label = QLabel("Description: ")
        self.description_label.setWordWrap(True)
        
        self.status_label = QLabel("Status: Idle")
        status_font = self.status_label.font()
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        
        self.phase_label = QLabel("Phase: ")
        
        self.tick_progress_label = QLabel("Tick: ")
        
        self.progress_bar = QProgressBar()
        # 0,0 puts progress ar into "busy" mode
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        
        details_layout.addWidget(self.name_label)
        details_layout.addWidget(self.description_label)
        details_layout.addSpacing(8)
        details_layout.addWidget(self.status_label)
        details_layout.addWidget(self.progress_bar)
        details_layout.addWidget(self.phase_label)
        details_layout.addWidget(self.tick_progress_label)
        
        root.addWidget(self.details_card)
        
        root.addStretch()
        
        button_row = QHBoxLayout()
        button_row.addStretch()
        
        self.back_button = QPushButton("Back")
        button_row.addWidget(self.back_button)
        
        root.addLayout(button_row)
        
    def _connect_signals(self) -> None:
        self.back_button.clicked.connect(self._handle_back)
        
    def set_experiment(self, experiment: dict) -> None:
        self.experiment = experiment
        self._populate_experiment_details()
        
    def _populate_experiment_details(self) -> None:
        if not self.experiment:
            self.name_label.setText("Name: ")
            self.description_label.setText("Description: ")
            return
        
        self.name_label.setText(
            f'Name: {self.experiment.get("name", "Unnamed Experiment")}'
        )
        description = str(self.experiment.get("description", "")).strip()
        self.description_label.setText(
            f'Description: {description or "No Description provided."}'
        )
        
    def set_status(self, status: str) -> None:
        self.status_label.setText(f'Status: {status}')
        
    def set_running_state(self) -> None:
        self.set_status("Running...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.back_button.setEnabled(False)
        
    def set_tick_progress(self, current_tick: int, total_ticks: int):
        ...
        
    def set_phase(self, text):
        ...
        
    def set_percent_progress(self, percent):
        self.progress_bar.setValue(percent) #not proper use?
        
    def set_complete_state(self) -> None:
        self.set_status("complete")
        self.progress_bar.setVisible(False)
        self.back_button.setEnabled(True)
        
    def set_failed_state(self, message: str | None = None) -> None:
        if message:
            self.set_status(f"Failed - {message}")
        else:
            self.set_status("Failed")
        self.progress_bar.setVisible(False)
        self.back_button.setEnabled(True)

    def _handle_back(self) -> None:
        if self.on_back:
            self.on_back(self.experiment)