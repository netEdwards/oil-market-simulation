

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
    run_type: str #shockless
    shock_enabled: bool
    error_message: str

class ExperimentExecuter:
    
    def __init__(
        self,
        run_type: str = "",
        experiment: Experiment = None,
        experiment_json: Dict[str, Any] = None,
    ):
        if not experiment:
            self.experiment = Experiment.from_dict(experiment_json) #experiment needs this function
        else:
            self.experiment = experiment
            
        self.run_type = run_type    
            
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
                
                
        if self.run_type == "baseline": do_shock = False
        else: do_shock = True
                
        sim = Simulation(config, do_shock, self.run_type)
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
            run_type=self.run_type,
            shock_enabled=do_shock,
        )
        