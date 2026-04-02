

from dataclasses import dataclass
from math import exp
from typing import Any, Dict

from experiments import experiment
from experiments.experiment import Experiment
from oilmarket.data.simulation import SimulationConfig
from oilmarket.data.state import TimestepState
from oilmarket.simulation import Simulation

@dataclass
class ExecutionResult:
    success: bool
    experiment_id: str
    run_ids: str
    run_path: str

class ExperimentExecuter:
    
    def __init__(
        self,
        experiment: Experiment = None,
        experiment_json: Dict[str, Any] = None,
    ):
        
        self.experiment = experiment if experiment else Experiment.load(experiment_json.get("folder_path", ""))
        
        if not self.experiment:
            raise Exception("No experiment was passed.", self.experiment)
            
         
            
    def execute(self):
        
        if not self.experiment:
            raise ValueError("There is no load experiment.")
        if not self.experiment.config_data or not self.experiment.config_path:
            raise ValueError("This experiment is missing config_data")
        
        
        config = SimulationConfig.from_yaml(self.experiment.config_path)
        config.output_path = self.experiment.output_path
        
        if not config:
            Warning("There was an error loading the expeirment configuration, attempting to use experiments dictionary loaded configuration.")
            
            try:
                config = SimulationConfig.from_dict(self.experiment.config_data)
            except Exception as e:
                Warning("There was an error loading configuraiton from dictionary: {e}".format(e))
            finally:
                if not config:
                    raise Exception("There is no configuration loadable from the experiment.")
        
        # =======================
        # Two simulation runs - One Shocked, One Shockless
        #==========================
                
        shocked_sim = Simulation(config, do_shock=True, experiment=self.experiment)
        shocked_result = shocked_sim.run()
        shocked_sim.export_all_outputs()
        
        
        shockless_sim = Simulation(config, do_shock=False, experiment=self.experiment)
        shockless_result = shockless_sim.run()
        shocked_sim.export_all_outputs()
        
        
        
        return ExecutionResult(
            success=True,
            experiment_id=self.experiment.id,
        )
        