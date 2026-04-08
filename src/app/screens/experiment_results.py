from ast import alias
from re import S
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QScrollArea,
    QPushButton,
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QPicture, QPixmap
from pkg_resources import non_empty_lines

from experiments.experiment import Experiment
from experiments.experiment_executer import ExecutionResult


class ExperimentResultsScreen(QWidget):
    def __init__(
        self, 
        on_back: Callable[[], None] | None,
        on_analysis: Callable[[], None] | None,
    ) -> None:
        super().__init__()
        
        # ------- DATA -------
        self.experiment: Experiment | dict = None
        self.execution_result: ExecutionResult = None
        
        self.analysis: dict = None
        
        
        # ------- UI -------
        
        self.on_back = on_back
        self.on_run_analysis = on_analysis
        self.outer_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(16)
        
        self.scroll_area.setWidget(self.content)
        
        self.outer_layout.addWidget(self.scroll_area)
        
        if not self.analysis:
            print(f"No analysis: {self.analysis}")
            self.content_layout.addWidget(self._build_no_results_screen())
        else:
            self._build_header()
            self._build_graph_card()
            self._connect_signals()
            
        self._connect_init_signals()
        
        
    def _build_no_results_screen(self) -> QWidget:
        
        root = QWidget()
        root_layout = QVBoxLayout(root)
        
        title_label = QLabel("Experiment Analysis")
        title_label_font = title_label.font()
        title_label_font.setBold(True)
        title_label_font.setPointSize(16)
        title_label.setFont(title_label_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_text = QLabel("There is no experiment analysis for this experiment")
        self.run_a_button = QPushButton("Run Analysis")
        self.nr_back_button = QPushButton("Back")
        
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.addWidget(title_label)
        root_layout.addWidget(main_text)
        root_layout.addWidget(self.run_a_button)
        root_layout.addWidget(self.nr_back_button)
        root_layout.addStretch()
        
        return root
        
        
        
    def _build_header(self) -> None:
        
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)
        
        self.title_label = QLabel("Experiment Results")
        title_font = self.title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(18)
        self.title_label.setFont(title_font)
        
        self.back_button = QPushButton("Back")
        
        root_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        root_layout.addWidget(self.title_label)
        
        self.cards = QWidget()
        self.cards_layout = QVBoxLayout(self.cards)
        self.details_card = QFrame()
        self.details_card.setFrameShape(QFrame.Shape.StyledPanel)
        details_layout = QVBoxLayout(self.details_card)
        details_layout.setContentsMargins(16, 16, 16, 16)
        details_layout.setSpacing(16)
        
        self.name_label = QLabel("Name: ")
        name_label_font = self.name_label.font()
        name_label_font.setBold(True)
        self.name_label.setFont(name_label_font)
        
        self.descritption_label = QLabel("Description: ")
        self.descritption_label.setWordWrap(True)
        
        
        
        self.cards_layout.addWidget(self.name_label)
        self.cards_layout.addWidget(self.descritption_label)
        
        
        
        self.config_sum = QFrame()
        self.config_sum.setFrameShape(QFrame.Shape.StyledPanel)
        self.config_sum_layout = QVBoxLayout(self.config_sum)
        self.config_sum_layout.setContentsMargins(12, 12, 12, 12)
        self.config_sum_layout.setSpacing(12)
        self.config_name_label = QLabel("Config Name: ")
        self.ticks_label = QLabel("Ticks: ")
        self.num_buyers_label = QLabel("Number of Buyers: ")
        self.num_sellers_label = QLabel("Number of Sellers: ")
        
        self.config_sum_layout.addWidget(self.config_name_label)
        self.config_sum_layout.addWidget(self.ticks_label)
        self.config_sum_layout.addWidget(self.num_buyers_label)
        self.config_sum_layout.addWidget(self.num_sellers_label)
        
        self.cards_layout.addWidget(self.config_sum)
        
        #self.cards.setLayout(self.cards_layout)
        root_layout.addWidget(self.cards)
        root_layout.addStretch()
        
        root.setLayout(root_layout)
        self.content_layout.addWidget(root)
    
    def _buid_shockless_frame(self):
        ...
        
        
    def _build_shocked_frame(self):
        ...
        

        
    def _build_graph_card(self) -> None:
        root = QFrame()
        root.setFrameShape(QFrame.Shape.StyledPanel)
        root_layout = QVBoxLayout(root)
        path = "../../../experiments/exp-c7521630-building-multi-run/runs/run-208abe2f-ef54-441e-a022-660b7713e47e/avg_price-208abe2f-ef54-441e-a022-660b7713e47e.png"
        pic = QPixmap()
        
        print("loaded?", not pic.isNull(), path)
        print("size:", pic.size())
        
        pic_label = QLabel()
        test_label = QLabel("test")
        pic_label.setPixmap(pic)
        
        root_layout.addWidget(pic_label)
        root_layout.addWidget(test_label)
        root.resize(pic.height(), pic.width())
        self.content_layout.addWidget(root)
        
        
        
    def _connect_init_signals(self)  -> None:
        self.nr_back_button.clicked.connect(lambda: self._handle_back())
        self.run_a_button.clicked.connect(lambda: self._handle_run_analysis())
        
    def _connect_signals(self) -> None:
        self.back_button.clicked.connect(lambda: self._handle_back())
        
        
    def _populate_header(self) -> None:
        if not self.analysis:
            return
        
        
        self.name_label.setText(f"Name: {self.experiment.name}")
        self.descritption_label.setText(f"Description: {self.experiment.description}")
        
    def _populate_details(self)-> None:
        if not self.experiment:
            return

        self.name_label.setText(f'Name: {self.experiment.get("name", "Unnamed Experiment")}')
        description = self.experiment.get("description", "No Description").strip()
        self.descritption_label.setText(f'Description: {description or ""}')
    
    def set_experiment_and_result(self, experiment: Experiment, execution_result: ExecutionResult) -> None:
        self.experiment = experiment if isinstance(experiment, Experiment) else None #sometimes passed as dict, need to handle properly.
        self.execution_result = execution_result #never passed as anything other than class instance.
        
        if self.experiment is None:
            return
        
        
    def set_experiment_analysis(self, analysis: dict) -> None:
        if not self.analysis:
            self.analysis = analysis
            print(f"Analysis set: {analysis.keys()}")
    
    def _create_experiment_vars(self) -> None:
        if not self.experiment:
            return
        
        print(self.experiment)
        
    
        
    def _handle_back(self) -> None:
        if self.on_back:
            self.on_back()
            
    def _handle_run_analysis(self) -> None:
        if self.on_run_analysis:
            self.on_run_analysis()