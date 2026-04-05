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
    QSpinBox,
    QSlider,
)
from PySide6.QtCore import Qt



class ExperimentRunnningScreen(QWidget):
    def __init__(
        self,
        on_back: Callable[[dict], None] | None = None,
        on_delay_update: Callable[[int], None] | None = None,
        on_skip_requested: Callable[[], None] | None = None,
        on_cancel_request: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__()
        
        self.on_back = on_back
        self.cancel_request = on_cancel_request
        self.skip_request = on_skip_requested
        self.delay_update = on_delay_update
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
        
        self.tick_progress_label = QLabel("Tick: 0 / 0")
        
        self.progress_bar = QProgressBar()
        # 0,0 puts progress ar into "busy" mode
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(True)
        
        self.cancel_button = QPushButton("Cancel")
        cancel_button_font = self.cancel_button.font()
        cancel_button_font.setItalic(True)
        self.cancel_button.setFont(cancel_button_font)
        
        self.skip_button = QPushButton("Skip")
        self.delay_spinbox = QSpinBox()
        self.delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.delay_slider.setRange(0, 500)
        self.delay_slider.setSingleStep(5)
        self.delay_slider.setPageStep(25)
        self.delay_slider.setValue(25)
        self.delay_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.delay_slider.setTickInterval(25)
        self.delay_value_label = QLabel("25 ms")
        
        self.run_controls = QFrame()
        self.run_controls.setFrameShape(QFrame.Shape.Panel)
        self.run_controls_layout = QHBoxLayout(self.run_controls)
        self.run_controls_layout.setContentsMargins(12, 12, 12, 12)
        self.run_controls_layout.setSpacing(12)
        
        self.run_controls_layout.addWidget(self.skip_button)
        self.run_controls_layout.addWidget(self.cancel_button)
        self.run_controls_layout.addWidget(self.delay_slider)
        self.run_controls_layout.addWidget(self.delay_value_label)
        
        details_layout.addWidget(self.name_label)
        details_layout.addWidget(self.description_label)
        details_layout.addSpacing(8)
        details_layout.addWidget(self.status_label)
        details_layout.addWidget(self.progress_bar)
        details_layout.addWidget(self.phase_label)
        details_layout.addWidget(self.tick_progress_label)
        details_layout.addWidget(self.run_controls)
        
        root.addWidget(self.details_card)
        
        root.addStretch()
        
        button_row = QHBoxLayout()
        button_row.addStretch()
        
        self.back_button = QPushButton("Back")
        button_row.addWidget(self.back_button)
        
        root.addLayout(button_row)
        
    def _connect_signals(self) -> None:
        self.back_button.clicked.connect(self._handle_back)
        self.cancel_button.clicked.connect(self._handle_cancel_request)
        self.skip_button.clicked.connect(self._handle_skip_request)
        self.delay_slider.valueChanged.connect(self._handle_delay_update)
        self.delay_slider.valueChanged.connect(
            lambda value: self.delay_value_label.setText(f"{value} ms")
        )
        
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
        tick_string = f"Ticks: {current_tick} / {total_ticks}"
        self.tick_progress_label.setText(tick_string)
        
    def set_phase(self, text):
        self.phase_label.setText(f'Phase: {text}')
        
    def set_percent_progress(self, percent):
        self.progress_bar.setValue(percent) #not proper use?
        
    def set_complete_state(self) -> None:
        self.set_status("complete")
        self.progress_bar.setVisible(False)
        self.back_button.setEnabled(True)
        self.tick_progress_label.setText("Ticks: ")
        self.phase_label.setText("Phase: None")
        
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
            
    def _handle_delay_update(self, delay: int) -> None:
        if delay > 0 and self.delay_update:
            self.delay_update(delay)
        else: return
        
    def _handle_cancel_request(self) -> None:
        if self.cancel_request:
            self.cancel_request()
       
    def _handle_skip_request(self) -> None:
        if self.skip_request:
            self.skip_request()