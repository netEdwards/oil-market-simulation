

from dataclasses import dataclass
from typing import Any, Dict

from experiments import experiment
from experiments.experiment import Experiment
from oilmarket.data.simulation import SimulationConfig
from oilmarket.data.state import TimestepState
from oilmarket.simulation import Simulation

@dataclass
class ExectuionResult:
    success: bool
    experiment_id: str
    run_id: str
    run_path: str
    is_baseline: bool #shockless
    error_message: str

class ExperimentExecuter:
    
    def __init__(
        self,
        is_baseline: bool = False,
        experiment: Experiment = None,
        experiment_json: Dict[str, Any] = None,
    ):
        if not experiment:
            self.experiment = Experiment.from_dict(experiment_json) #experiment needs this function
        else:
            self.experiment = experiment
            
        self.is_baseline = is_baseline
            
    def execute(self):
        if not self.experiment:
            raise ValueError("There is no load experiment.")
        
        
        if not self.experiment.config_data or not self.experiment.config_path:
            raise ValueError("This experiment is missing config_data")
        
        config = SimulationConfig.from_yaml(self.experiment.config_path)
        if not config:
            Warning("There was an error loading the expeirment configuration, attempting to use experiments dictionary loaded configuration.")
            
            try:
                config = SimulationConfig.from_dict(self.experiment.config_data)
            except Exception as e:
                Warning("There was an error loading configuraiton from dictionary: {e}".format(e))
            finally:
                if not config:
                    raise Exception("There is no configuration loadable from the experiment.")
                
        sim = Simulation(config)
        result = sim.run()
        if not isinstance(result, list[TimestepState]):
            raise Exception("There was an error with the output of simulation state.")
        if len(result) == 0:
            raise Exception("There werre no results returned from the simulation run.")
        
        return ExectuionResult(
            success=True,
            experiment_id=self.experiment.id,
            run_id=sim.run_id,
            run_path=sim.output_path,
            is_baseline=self.is_baseline,
        )
        