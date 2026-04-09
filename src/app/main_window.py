from math import exp
from typing import List

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
from experiments.experiment import Experiment
from experiments.experiment_analyzer import ExperimentAnalyzer
from experiments.experiment_executer import ExecutionResult
from app.screens.experiment_results import ExperimentResultsScreen
from oilmarket.data.state import TimestepState


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oil Market Simulation Experiments")
        self.resize(QSize(800, 600))
        self.setMinimumSize(QSize(800, 600))
        
        self.current_experiment_instance: Experiment = None
        self.current_experiment_exec_result: ExecutionResult | dict = None
        self.experiments_list: List[Experiment] = []
        self.execution_thread: QThread = None
        self.execution_worker: ExecutionWorker = None

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
            on_results=self._on_view_results_clicked,
        )
        
        self.experiment_running_page = ExperimentRunnningScreen(
            on_back=self.show_experiment_viewer,
            on_cancel_request=self._on_run_cancel_requested,
            on_delay_update=self._on_run_update_delay_requested,
            on_skip_requested=self._on_run_skip_requested,
        )
        
        self.experiment_results_page = ExperimentResultsScreen(
            on_back     = self.show_view_experiments_screen,
            on_analysis = self.handle_experiment_analysis,
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
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        
        self.exit_button.clicked.connect(self._on_exit_button_clicked)




    def show_home_screen(self):
        self.stack.setCurrentWidget(self.home_page)

    def show_view_experiments_screen(self):
        self.view_experiments_page.refresh()
        self.stack.setCurrentWidget(self.view_experiments_page)
        
    def show_new_experiment_screen(self):
        self.stack.setCurrentWidget(self.new_experiment_page)
        
    def show_experiment_viewer(self, experiment: dict):
        print(f"Main window experiment button handler: {experiment}")
        self.experiment_view_page.set_experiment(experiment)
        self.stack.setCurrentWidget(self.experiment_view_page)
        
    def show_experiment_results_page(self, experiment: Experiment | dict, analysis: dict = None) -> None:
        """Experiment results page requires an `Experiment` and `ExectutionResult` instance for methods attached!"""
        self.current_experiment_instance = self._coerce_experiment(experiment)
        
        has_a = self.current_experiment_instance.has_analysis()    
        if not has_a:
            self.experiment_results_page.show_no_analysis(experiment=self.current_experiment_instance)
            self.experiment_results_page.refresh_analysis()
        else:
            if not analysis:
                analysis = self.current_experiment_instance.load_analysis()
            self.experiment_results_page.show_analysis(self.current_experiment_instance, analysis)
            self.experiment_results_page.refresh_analysis()
        
        self.stack.setCurrentWidget(self.experiment_results_page)
        
        
    def show_experiment_running_screen(self):
        self.stack.setCurrentWidget(self.experiment_running_page)

    def _on_new_experiment_button_clicked(self):
        self.show_new_experiment_screen()

    def _on_view_experiments_button_clicked(self):
        self.show_view_experiments_screen()
        
    def _on_view_experiment_requested(self, experiment: dict):
        if not experiment:
            print("No experiment passed...")
            
        self.current_experiment_instance = self._coerce_experiment(experiment)
        self.show_experiment_viewer(experiment)

    def _on_edit_experiment_requested(self, experiment: dict):
        print(f'Edit requested for: {experiment.get("name")}')

    def _on_view_results_clicked(self, experiment: dict) -> None:
        if not experiment:
            print("No experiment passed.")
            return
        self.show_experiment_results_page(experiment)
    
    def _on_run_experiment_requested(self, experiment: dict) -> None:
        if not self.current_experiment_instance:
            self.current_experiment_instance = self._coerce_experiment(experiment)
        
        self.stack.setCurrentWidget(self.experiment_running_page)
        self.experiment_running_page.set_experiment(experiment)
        self._execute_experiment(experiment)
        

    def _on_exit_button_clicked(self):
        self.close()
        
        
    def _on_execution_update(self, update: dict):
        phase_text = update.get("current_execution", "")
        self.experiment_running_page.set_phase(phase_text)
        
    def _on_timestep_emitted(self, t: dict):
        self.experiment_running_page.set_tick_progress(
            current_tick=t.get("timestep", 0),
            total_ticks=t.get("ticks", 0)
        )
        
    def _on_progress_emitted(self, progress: int) -> None:
        self.experiment_running_page.set_percent_progress(progress)
    
    def _on_finished_emitted(self, experiment_result: ExecutionResult) -> None:
        self.experiment_running_page.set_complete_state()
        
        self.current_experiment_exec_result = experiment_result
           
    def _on_failed_emitted(self, error: str) -> None:
        self.experiment_running_page.set_failed_state()
        print("Emitted Error: ", error)
        
    def _on_analysis_complete_emitted(self, analysis: dict) -> None:
        self.show_experiment_results_page(experiment=self.current_experiment_instance, analysis=analysis)
        
    def _handle_analysis_failed(self, error: str) -> None:
        print(f"Error creating analysis: {error}")
         
    def _on_run_skip_requested(self) -> None:
        worker = self.execution_worker
        if worker:
            worker.request_skip()
    
    def _on_run_update_delay_requested(self, delay: int) -> None:
        worker = self.execution_worker
        if worker:
            worker.update_controller_delay(delay=delay)
    
    def _on_run_cancel_requested(self) -> None:
        worker = self.execution_worker
        if worker:
            worker.request_cancel()
    
    def _execute_experiment(self, experiment: dict) -> None:
        if not experiment:
            return

        # fresh worker + fresh thread every run
        self.execution_worker = ExecutionWorker(experiment)
        self.execution_thread = QThread()

        worker = self.execution_worker
        thread = self.execution_thread

        worker.moveToThread(thread)

        # start the worker when thread starts
        thread.started.connect(worker.run)

        # original UI / progress functionality
        worker.progress.connect(self._on_progress_emitted)
        worker.finished.connect(self._on_finished_emitted)
        worker.failed.connect(self._on_failed_emitted)
        worker.timestep_update.connect(self._on_timestep_emitted)
        worker.execution_update.connect(self._on_execution_update)

        # proper thread shutdown
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)

        worker.finished.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)

        thread.start()
        
    def _coerce_experiment(self, experiment: dict | Experiment) -> Experiment:
        if isinstance(experiment, Experiment):
            return experiment
        if isinstance(experiment, dict):
            return Experiment.load(experiment["folder_path"])
        raise TypeError("Experiment must be a dict or Experiment instance.")
    
    def _get_current_experiment_analysis(self) -> dict | None:
        
        if not self.current_experiment_instance:
            return None
        
        if not self.current_experiment_instance.has_analysis():
            return None
        
        return self.current_experiment_instance.load_analysis()
    
    def handle_experiment_analysis(self) -> None:
        if not self.current_experiment_instance:
            raise Exception("There is no current experiment set.")

        if not self.current_experiment_instance.has_execution():
            print("No execution for this experiment has been completed.")
            return

        if not self.current_experiment_exec_result:
            print("Execution result exists, but not loaded - attempting to load...")
            self.current_experiment_exec_result = self.current_experiment_instance.load_execution()
            print("Execution result loaded!")

        # fresh worker + fresh thread every analysis
        self.execution_worker = ExecutionWorker(
            experiment=self.current_experiment_instance,
            execution_result=self.current_experiment_exec_result,
        )
        self.execution_thread = QThread()

        worker = self.execution_worker
        thread = self.execution_thread

        worker.moveToThread(thread)

        # start analysis when thread starts
        thread.started.connect(worker.run_analysis)

        # original result / error handling
        worker.analysis_complete.connect(self._on_analysis_complete_emitted)
        worker.failed.connect(self._handle_analysis_failed)

        # proper thread shutdown
        worker.analysis_complete.connect(thread.quit)
        worker.failed.connect(thread.quit)

        worker.analysis_complete.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)

        thread.start()
        
    