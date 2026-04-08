from numpy import isin

from experiments.experiment import Experiment
from experiments.experiment_analyzer import ExperimentAnalyzer
from experiments.experiment_executer import ExperimentExecuter, ExecutionResult
from PySide6.QtCore import QObject, Signal, QThread, Slot

from oilmarket.data.state import TimestepState
from oilmarket.simulation import RunController



class ExecutionWorker(QObject):
    
    finished = Signal(object)
    progress = Signal(int)
    failed = Signal(str)
    timestep_update = Signal(dict)
    execution_update = Signal(dict)
    analysis_complete = Signal(dict)
    
    def __init__(self, experiment: dict | Experiment, execution_result: ExecutionResult = None):
        super().__init__()
        
        self.experiment = experiment
        self.run_control = RunController(
            tick_delay_ms=25
        )
        self.execution_result = execution_result
        
        print("Execution worker initialized.")

    @Slot()
    def run(self):
        
        def handle_execution_update(update: dict): 
            self.execution_update.emit(update)
        
        executor = ExperimentExecuter(experiment_json=self.experiment, on_execution_update=handle_execution_update)
        try:
            def handle_timestep(t: int, state: TimestepState):
                total = max(1, executor.experiment.config_data["ticks"])
                percent = int(((t+1) / total) * 100) 
                self.progress.emit(percent)
                
                self.timestep_update.emit({
                    "timestep": t,
                    "ticks": executor.experiment.config_data["ticks"],
                    "average_price": state.average_price,
                    "total_demand": state.total_demand,
                    "total_unmet_demand": state.total_unmet_demand,
                    "shock_active": state.shock_active,
                    "transaction_count": state.transaction_count,
                })
            
            result = executor.execute(on_timestep=handle_timestep, run_control=self.run_control)
            
            
            
            
            if not result:
                raise Exception("Simulation finished with no results")
                return    
            
            self.progress.emit(100)
            self.finished.emit(result)
            
        except Exception as e:
            self.failed.emit(str(e))
    
    @Slot()
    def run_analysis(self):        
        if isinstance(self.experiment, dict):
            self.experiment = Experiment.load(self.experiment)
            
        analysis_inst = ExperimentAnalyzer(
            experiment=self.experiment,
            execution_result=self.execution_result,
        )
        
        analysis = analysis_inst.build_all_analysis()
        analysis_inst.save_analysis()
        
        if not isinstance(analysis, dict):
            self.failed.emit("There was an error generating the analysis.")
            raise Exception("There was an error generating the analysis.")

        self.analysis_complete.emit(analysis)
    
    @Slot()
    def request_skip(self):
        if self.run_control:
            self.run_control.skip_requsted = True
            self.run_control.tick_delay_ms = 0

    @Slot()
    def request_cancel(self):
        if self.run_control:
            self.run_control.cancel_request = True
            self.run_control.tick_delay_ms = 99

    @Slot()
    def update_controller_delay(self, delay):
        if self.run_control:
            self.run_control.tick_delay_ms = delay