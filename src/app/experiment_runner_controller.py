from numpy import isin

from experiments.experiment_executer import ExperimentExecuter, ExecutionResult
from PySide6.QtCore import QObject, Signal, QThread


class ExecutionWorker(QObject):
    
    finished = Signal(object)
    progress = Signal(int)
    failed = Signal(str)
    
    def __init__(self, experiment: dict):
        super().__init__()
        
        self.experiment = experiment


    
    def run(self):
        executor = ExperimentExecuter(experiment_json=self.experiment)
        try:
            
            #=======
            # Add async execution and singal emission of progress
            #=========
            
            self.progress.emit(10)
            
            result = executor.execute()
            
            self.progress.emit(90)
            
            
            if not result:
                raise Exception("Simulation finished with no results")
                return    
            
            self.progress.emit(100)
            self.finished.emit(result)
            
        except Exception as e:
            self.failed.emit(str(e))
    

