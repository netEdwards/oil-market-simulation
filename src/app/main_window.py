from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
)
from PySide6.QtCore import QSize, Qt, QThread

from app.screens.new_experiment import NewExperimentScreen
from app.screens.view_experiments import ViewExperimentsScreen
from app.screens.experiment_viewer import ExperimentViewerScreen
from app.screens.experiment_running import ExperimentRunnningScreen
from app.experiment_runner_controller import ExecutionWorker
from experiments.experiment_executer import ExecutionResult
from app.screens.experiment_results import ExperimentResultsScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oil Market Simulation Experiments")
        self.resize(QSize(800, 600))
        self.setMinimumSize(QSize(800, 600))

        self._set_central_widget()
        self._connect_signals()
        self.show_home_screen()

    def _set_central_widget(self):
        self.stack = QStackedWidget()

        self.home_page = self._build_home_screen()
        self.new_experiment_page = NewExperimentScreen(
            on_cancel=self.show_home_screen,
            on_saved=self.show_home_screen,
        )
        self.experiment_view_page = ExperimentViewerScreen(
            on_back=self.show_view_experiments_screen,
            on_run=self._on_run_experiment_requested,
        )

        self.view_experiments_page = ViewExperimentsScreen(
            on_back=self.show_home_screen,
            on_view=self._on_view_experiment_requested,
            on_edit=self._on_edit_experiment_requested,
        )
        
        self.experiment_running_page = ExperimentRunnningScreen(
            on_back=self.show_experiment_viewer,
        )
        
        self.experiment_results_page = ExperimentResultsScreen(
            on_back     = self.show_view_experiments_screen,
            experiment  = None
        )
        
        
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.new_experiment_page)
        self.stack.addWidget(self.view_experiments_page)
        self.stack.addWidget(self.experiment_view_page)
        self.stack.addWidget(self.experiment_running_page)
        self.stack.addWidget(self.experiment_results_page)
    
        self.setCentralWidget(self.stack)

    def _build_home_screen(self) -> QWidget:
        page = QWidget()
        outer_layout = QVBoxLayout()
        page.setLayout(outer_layout)

        menu_container = QWidget()
        menu_container.setFixedWidth(400)
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(12)
        menu_container.setLayout(menu_layout)

        title_label = QLabel("Market Experiments")
        title_label.setAlignment(Qt.AlignCenter)

        font = title_label.font()
        font.setPointSize(20)
        font.setBold(True)
        title_label.setFont(font)

        self.new_experiment_button = QPushButton("New Experiment")
        self.view_experiments_button = QPushButton("View Experiments")
        self.new_baseline_button = QPushButton("New Baseline")
        self.exit_button = QPushButton("Exit")

        self.new_experiment_button.setMinimumHeight(40)
        self.view_experiments_button.setMinimumHeight(40)
        self.exit_button.setMinimumHeight(40)

        menu_layout.addWidget(title_label)
        menu_layout.addWidget(self.new_experiment_button)
        menu_layout.addWidget(self.view_experiments_button)
        menu_layout.addWidget(self.exit_button)

        outer_layout.addStretch()
        outer_layout.addWidget(menu_container, alignment=Qt.AlignmentFlag.AlignCenter)
        outer_layout.addStretch()

        return page

    def _connect_signals(self):
        self.new_experiment_button.clicked.connect(
            self._on_new_experiment_button_clicked
        )
        self.view_experiments_button.clicked.connect(
            self._on_view_experiments_button_clicked
        )
        self.new_baseline_button.clicked.connect(
            self._on_new_baseline_button_clicked
        )
        self.exit_button.clicked.connect(self._on_exit_button_clicked)

    def show_home_screen(self):
        self.stack.setCurrentWidget(self.home_page)

    def show_view_experiments_screen(self):
        self.view_experiments_page.refresh()
        self.stack.setCurrentWidget(self.view_experiments_page)
        
    def show_new_experiment_screen(self):
        self.stack.setCurrentWidget(self.new_experiment_page)
        
    def show_experiment_viewer(self, experiment: dict):
        self.experiment_view_page.set_experiment(experiment)
        self.stack.setCurrentWidget(self.experiment_view_page)
        
    def show_experiment_results_page(self, experiment: dict) -> None:
        self.stack.setCurrentWidget(self.experiment_results_page)
        self.experiment_results_page.set_experiment(experiment)
        
    def show_experiment_running_screen(self):
        self.stack.setCurrentWidget(self.experiment_running_page)

    def _on_new_experiment_button_clicked(self):
        self.show_new_experiment_screen()

    def _on_view_experiments_button_clicked(self):
        self.show_view_experiments_screen()
        
    def _on_view_experiment_requested(self, experiment: dict):
        if not experiment:
            print("No experiment passed...")
        self.show_experiment_viewer(experiment)

    def _on_edit_experiment_requested(self, experiment: dict):
        print(f'Edit requested for: {experiment.get("name")}')

    def _on_exit_button_clicked(self):
        self.close()
        
    def _on_run_experiment_requested(self, experiment: dict) -> None:
        self.stack.setCurrentWidget(self.experiment_running_page)
        self._execute_experiment(experiment)
        
    def _on_progress_emitted(self, progress: int) -> None:
        self.experiment_running_page.set_percent_progress(progress)
    
    def _on_finished_emitted(self, experiment_result: ExecutionResult) -> None:
        self.experiment_running_page.set_complete_state()
        self.execution_thread.quit()
        self.execution_thread.wait()
        self.execution_thread = None
        self.execution_worker = None
    
    def _on_failed_emitted(self, error: str) -> None:
        self.experiment_running_page.set_failed_state()
        print("Emitted Error: ", error)
         
    def _execute_experiment(self, experiment: dict) -> None:
        
        if not experiment:
            return
        
        worker = ExecutionWorker(experiment)
        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        
        self.execution_worker = worker
        self.execution_thread = thread
        
        worker.progress.connect(self._on_progress_emitted)
        worker.finished.connect(self._on_finished_emitted)
        worker.failed.connect(self._on_failed_emitted)
        
        thread.start()
        
    def _on_view_results_clicked(self, experiment: dict) -> None:
        self.show_experiment_results_page(experiment)
        