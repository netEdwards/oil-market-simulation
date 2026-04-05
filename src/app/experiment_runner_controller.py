from numpy import isin

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
    
    def __init__(self, experiment: dict):
        super().__init__()
        
        self.experiment = experiment
        self.run_control = RunController(
            tick_delay_ms=25
        )

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