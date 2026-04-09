

from dataclasses import dataclass
from fileinput import filename
from math import exp
from typing import Any, Callable, Dict, Optional
import uuid
import warnings

from experiments import experiment
from experiments.experiment import Experiment
from oilmarket.data.simulation import SimulationConfig
from oilmarket.data.state import TimestepState
from oilmarket.simulation import Simulation, RunController

@dataclass
class ExecutionResult:
    success: bool
    experiment_id: str
    shocked_results: dict
    shockless_results: dict
    id: str = "execution-" + str(uuid.uuid4())
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "success": self.success,
            "experiment_id": self.experiment_id,
            "shocked_results": self.shocked_results,
            "shockless_results": self.shockless_results
        }


class ExperimentExecuter:
    
    def __init__(
        self,
        experiment: Experiment = None,
        experiment_json: Dict[str, Any] = None,
        on_execution_update: Optional[Callable[[dict], None]] = None,
    ):
        
        self.on_execution_update = on_execution_update  
        self.experiment = experiment if experiment else Experiment.load(experiment_json.get("folder_path", ""))
        
        if not self.experiment:
            raise Exception("No experiment was passed.", self.experiment)
            
         
            
    def execute(self, on_timestep=None, run_control: RunController = None):
        
        
        self.on_execution_update({
            "currrent_execution": "shocked",
            "status": "running"
        })
        
        if not self.experiment:
            raise ValueError("There is no load experiment.")
        if not self.experiment.config_data or not self.experiment.config_path:
            raise ValueError("This experiment is missing config_data")
        
        
        config = SimulationConfig.from_yaml(self.experiment.config_path)
        config.output_path = self.experiment.output_path
        
        if not config:
            warnings.warn("There was an error loading the expeirment configuration, attempting to use experiments dictionary loaded configuration.")
            
            try:
                config = SimulationConfig.from_dict(self.experiment.config_data)
            except Exception as e:
                warnings.warn("There was an error loading configuraiton from dictionary: {e}".format(e))
            finally:
                if not config:
                    raise Exception("There is no configuration loadable from the experiment.")
        
        # =======================
        # Clear experiment runs
        #==========================
        self.experiment.clear_experiment()
        
        
        # =======================
        # Two simulation runs - One Shocked, One Shockless
        #==========================
        
        
                
        shocked_sim = Simulation(config, do_shock=True, experiment=self.experiment, on_timestep=on_timestep, run_control=run_control)
        shocked_sim.run()
        self.on_execution_update({
            "current_execution": "shocked",
            "status": "complete",
        })
        shocked_ouputs = shocked_sim.export_all_outputs()
        
        
        self.on_execution_update({
            "current_execution": "shockless",
            "status": "running",
        })
        shockless_sim = Simulation(config, do_shock=False, experiment=self.experiment, on_timestep=on_timestep, run_control=run_control)
        shockless_sim.run()
        self.on_execution_update({
            "current_execution": "shockless",
            "status": "complete",
        })
        shockless_outputs = shockless_sim.export_all_outputs()
        
        
        
        
        exec_result =  ExecutionResult(
            success=True,
            experiment_id=self.experiment.id,
            shocked_results=shocked_ouputs,
            shockless_results=shockless_outputs,
        )
        self.experiment.save_execution(exec_result.to_dict())
        
        return exec_result
        