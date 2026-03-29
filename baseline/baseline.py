

from math import exp
from pathlib import Path
from typing import Any, Dict

from experiments.experiment import Experiment


class Baseline:
    def __init__(
            self,
            experiment: Experiment,
            output_data_dir: Path | str = None, 
        ):
        self.name = "baseline-"+experiment.name
        
        self.experiment = experiment
        if output_data_dir is not None:
            print("Using output data instead of experiment.")
            
    def calculate_price_stability():
        ...
        
    def calculate_fulfilled_demand():
        ...
        
    def calculate_supply_adequacy():
        ...
        
    
        