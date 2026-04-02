from re import S
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
)

from PySide6.QtCore import Qt


class ExperimentResultsScreen(QWidget):
    def __init__(
        self, 
        experiment: dict | None,
        on_back: Callable[[], None] | None,
    ) -> None:
        super().__init__()
        
        self.experiment = experiment
        
        self._build_ui()
        self._connect_signals()
        
    def _build_ui(self) -> None:
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)
        
        self.title_label = QLabel("Experiment Results")
        title_font = self.title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(18)
        self.title_label.setFont(title_font)
        root.addWidget(self.title_label)
        
        self.details_card = QFrame()
        self.details_card.setFrameShape(QFrame.Shape.StyledPanel)
        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(16, 16, 16, 16)
        details_layout.setSpacing(16)
        
        self.name_label = QLabel("Name: ")
        self.descritption_label = QLabel("Description: ")
        self.descritption_label.setWordWrap(True)
        
        details_layout.addWidget(self.name_label)
        details_layout.addWidget(self.descritption_label)
        root.addWidget(self.details_card)
        
        
        
    def _connect_signals(self) -> None:
        ...
        
    def set_experiment(self, experiment: dict) -> None:
        
        self.experiment = experiment if experiment else None