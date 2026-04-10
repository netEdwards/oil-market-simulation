

import datetime
import json
from os import set_inheritable
from pathlib import Path
import stat
from typing import List
import warnings

from experiments.experiment import Experiment
from experiments.experiment_executer import ExecutionResult


class ExperimentAnalyzer:
    def __init__(
        self,
        experiment: Experiment | dict = None,
        execution_result: ExecutionResult | dict = None,
    ):
        
        if isinstance(experiment, dict):
            self.experiment = Experiment.load(experiment)
        elif isinstance(experiment, Experiment): 
            self.experiment = experiment
        else:
            raise TypeError("Experiment passed is not proper type or value for loading the experiment.")
        
        
        if isinstance(execution_result, dict):
            self.execution_result = ExecutionResult(
                success=execution_result.get("success"),
                experiment_id=execution_result.get("experiment_id"),
                shocked_results=execution_result.get("shocked_results"),
                shockless_results=execution_result.get("shockless_results"),
            )
        elif isinstance(execution_result, ExecutionResult):
            self.execution_result = execution_result
        else:
            raise ValueError("Execution result was not passed in a readable way. (dict or class ExecutionResult).")
            
        
        self.shocked_run_path:          str | Path = None
        self.shockless_run_path:        str | Path = None
        self.shockless_run_history:     dict | list = None
        self.shocked_run_history:       dict | list = None
        self.shocked_run_manifest:      dict = None
        self.shockless_run_manifest:    dict = None
        self.shocked_execution_result   = self.execution_result.shocked_results
        self.shockless_execution_result = self.execution_result.shockless_results
        self.analysis:                  dict = None
        
        self._load_runs()
        
        
    def build_config_summary(self) -> dict:
        """Builds the config summary.

        Returns:
            dict: Configuration summary from the experiment.
        """
        if not self.experiment or not self.experiment.config_data:
            raise AttributeError("Expected self.experiment to be present and have a loaded experiment.")
        config_data = self.experiment.config_data
        
        config_summary = {
            "seed": config_data["seed"],
            "ticks": config_data["ticks"],
            "shock": config_data["shock"],
            "buyers": config_data["buyers"],
            "sellers": config_data["sellers"]
        }
        
        return config_summary
       
    def build_all_analysis(self) -> dict:
        if not self.shocked_run_history or not self.shockless_run_history:
            raise AttributeError("Expected self to contain shocked and shockless run history, missing one.")
        
        
        a_price         = self.build_price_analysis()
        a_fulfillment   = self.build_fulfillment_analysis()
        a_supply        = self.build_supply_analysis()
        
        analysis = {
            "experiment_id": self.experiment.id,
            "experiment_name": self.experiment.name,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "config_summary": self.build_config_summary(),
            "runs": {
                "shockless": {
                    "run_id": self.shockless_run_manifest.get("run_id", ""),
                    "run_path": self.shockless_run_manifest.get("run_output_path", ""),
                    "manifest": self.shockless_run_manifest,
                },
                "shocked": {
                    "run_id": self.shocked_run_manifest.get("run_id", ""),
                    "run_path": self.shocked_run_manifest.get("run_output_path", ""),
                    "manifest": self.shocked_run_manifest,
                },
            },
            "price": a_price,
            "fulfillment": a_fulfillment,
            "supply": a_supply,
        }
        
        self.analysis = analysis
        
        return analysis
        
    def save_analysis(self) -> Path:
        """Saves the analysis with current instance set experiment. Requires experiment to be present.
        """
        if not self.experiment:
            raise AttributeError("Experiment is missing from the ExperimentAnalyzer instance.")
        
        if not self.analysis:
            raise AttributeError("Expected self.analysis to be populated, was not. Try calling an analysis to be built.")
        
        analysis_path = self.experiment.save_analysis(self.analysis)
        return analysis_path
        
    def build_price_analysis(self) -> dict:
        shocked_price_series = self.build_price_series(self.shocked_run_history)
        shockless_price_series = self.build_price_series(self.shockless_run_history)
        
        shocked_mean_price = sum(shocked_price_series) / len(shocked_price_series)
        shockless_mean_price = sum(shockless_price_series) / len(shockless_price_series)
        
        shocked_price_volatility = self.compute_price_volatility(shocked_price_series)
        shockless_price_volatility = self.compute_price_volatility(shockless_price_series)
        
        #shockless price percent change
        sl_price_pc = self.compute_perc_change_price(shockless_price_series)
        s_price_pc = self.compute_perc_change_price(shocked_price_series)
        
        sl_mean_abs_change = sum(sl_price_pc) / len(sl_price_pc)
        s_mean_abs_change = sum(s_price_pc) / len(s_price_pc)
        
        s_min_price = min(shocked_price_series)
        sl_min_price = min(shockless_price_series)
        
        sl_peak_price = max(shockless_price_series)
        s_peak_price = max(shocked_price_series)
        print("Shockless min/max:", sl_min_price, sl_peak_price)
        print("Shocked min/max:", s_min_price, s_peak_price)
        
        sl_max_price_change = max(sl_price_pc)
        s_max_price_change = max(s_price_pc)
        
        # Comparisons
        delta_mean_price = shocked_mean_price - shockless_mean_price
        percent_change = delta_mean_price / shockless_mean_price
        delta_volatility = shocked_price_volatility - shockless_price_volatility
        
        return {
            "shocked": {
                "price_series": shocked_price_series,
                "price_perc_change_series": s_price_pc,
                "mean_price": shocked_mean_price,
                "price_volatility": shocked_price_volatility,
                "mean_price_change": s_mean_abs_change,
                "min_price": s_min_price,
                "peak_price": s_peak_price,
                "max_price_change": s_max_price_change,
            },
            "shockless": {
                "price_series": shockless_price_series,
                "price_perc_change_series": sl_price_pc,
                "mean_price": shockless_mean_price,
                "price_volatility": shockless_price_volatility,
                "mean_price_change": sl_mean_abs_change,
                "min_price": sl_min_price,
                "peak_price": sl_peak_price,
                "max_price_change": sl_max_price_change,
            },
            "comparison": {
                "delta_mean_price": delta_mean_price,
                "percent_change": percent_change,
                "delta_volatility": delta_volatility,
            }
        }
    
    @staticmethod
    def compute_price_volatility(price_series: list[float]) -> float:
        if len(price_series) < 2:
            return 0.0
        changes = [
            abs(price_series[i] - price_series[i-1])
            for i in range(1, len(price_series))
        ]
        
        return sum(changes) / len(changes)
        
    @staticmethod
    def compute_perc_change_price(price_series: list[float]) -> list[float]:
        
        if not price_series: return
        
        changes = []
        
        for i in range(1, len(price_series)):
            percent_change = (price_series[i] - price_series[i-1]) / price_series[i-1]
            changes.append(abs(percent_change))
            
        return changes
            
        

    @staticmethod
    def build_price_series(history: list) -> list[float]:
        return [t["average_price"] for t in history]
       
       
       
        
    def build_fulfillment_analysis(self) -> dict:
        shocked_ff_series = self.build_fulfillment_series(self.shocked_run_history)
        shockless_ff_series = self.build_fulfillment_series(self.shockless_run_history)
        
        shocked_ff_rate_series = self.build_fulfillment_rate_series(self.shocked_run_history)
        shockless_ff_rate_series = self.build_fulfillment_rate_series(self.shockless_run_history)
        
        s_ff_rate_change = self.calculate_ff_rate_changes(shocked_ff_rate_series)
        sl_ff_rate_change = self.calculate_ff_rate_changes(shockless_ff_rate_series)
        
        s_mean_ff_rate_change = sum(s_ff_rate_change) / len(s_ff_rate_change)
        sl_mean_ff_rate_change = sum(sl_ff_rate_change) / len(sl_ff_rate_change)
        
        s_total_sold = sum(shocked_ff_series["fulfilled"])
        s_total_demand = sum(shocked_ff_series["demand"])
        sl_total_sold = sum(shockless_ff_series["fulfilled"])
        sl_total_demand = sum(shockless_ff_series["demand"])
        
        s_ff_rate = s_total_sold / s_total_demand if s_total_demand > 0 else 0.0
        sl_ff_rate = sl_total_sold / sl_total_demand if sl_total_demand > 0 else 0.0
        
        shocked_peak_unmet = max(shocked_ff_series["unmet"]) if shocked_ff_series["unmet"] else 0.0
        shockless_peak_unmet = max(shockless_ff_series["unmet"]) if shockless_ff_series["unmet"] else 0.0
        
        return {
            "shocked": {
                "fulfilled_series": shocked_ff_series["fulfilled"],
                "unmet_series": shocked_ff_series["unmet"],
                "fulfillment_rate": s_ff_rate,
                "peak_unmet": shocked_peak_unmet,
                "mean_change_rate": s_mean_ff_rate_change,
            },
            "shockless": {
              "fulfilled_series": shockless_ff_series["fulfilled"],
              "unmet_series": shockless_ff_series["unmet"],
              "fulfillment_rate": sl_ff_rate,
              "peak_unmet": shockless_peak_unmet,
              "mean_change_rate": sl_mean_ff_rate_change,
            },
            "comparison": {
                "delta_fulfillment_rate": s_ff_rate - sl_ff_rate,
                "delta_peak_unmet": shocked_peak_unmet - shockless_peak_unmet,
            }
        }
          
    @staticmethod
    def build_fulfillment_series(history: list) -> dict:
        fulfilled = [t["total_units_sold"] for t in history]
        unmet = [t["total_unmet_demand"] for t in history]
        demand = [t["total_demand"] for t in history]
        
        return {
            "fulfilled": fulfilled,
            "unmet": unmet,
            "demand": demand,
        }
        
    @staticmethod
    def build_fulfillment_rate_series(history: list) -> list:
        rates = []
        for t in history:
            if t["total_demand"] == 0:
                rates.append(0.0)
            else:
                rates.append(t["total_units_sold"] / t["total_demand"])
        
        return rates
    
    @staticmethod  
    def calculate_ff_rate_changes(series: list[float]):
        if not series: return
        changes = []
        for i in range(len(series)):
            change = series[i] - series[i-1]
            changes.append(abs(change))
        
        return changes
        
        
        
    def build_supply_analysis(self) -> dict:
        shocked_supply_series = self.build_supply_series(self.shocked_run_history)
        shockless_supply_series = self.build_supply_series(self.shockless_run_history)
        
        s_avg_supply = self._compute_mean_list(shocked_supply_series)
        s_min_supply = min(shocked_supply_series)
        sl_min_supply = min(shockless_supply_series)
        sl_avg_supply = self._compute_mean_list(shockless_supply_series)
        
        sl_supply_pc = self.calculate_percent_change_supply(shockless_supply_series)
        s_supply_pc = self.calculate_percent_change_supply(shocked_supply_series)
        
        sl_mean_supply_pc = sum(sl_supply_pc) / len(sl_supply_pc)
        s_mean_supply_pc = sum(s_supply_pc) / len(s_supply_pc)
        
        print(f"Shockless mean supply pc: {sl_mean_supply_pc}")
        print(f"Shockled mean supply pc: {s_mean_supply_pc}")
        
        sl_peak_supply_change = max(sl_supply_pc)
        s_peak_supply_change = max(s_supply_pc)
        
        
        #percent change = pc
        avg_supply_pc = self._percent_change(sl_avg_supply, s_avg_supply)
    
        
        return {
            "shocked": {
                "supply_series": shocked_supply_series,
                "avg_supply": s_avg_supply,
                "min_supply": s_min_supply,
                "supply_pc": s_mean_supply_pc,
                "peak_supply_change": s_peak_supply_change,
            },
            "shockless": {
                "supply_series": shockless_supply_series,
                "avg_supply": sl_avg_supply,
                "min_supply": sl_min_supply,
                "supply_pc": sl_mean_supply_pc,
                "peak_supply_change": sl_peak_supply_change,
            },
            "comparison": {
                "delta_avg_supply": s_avg_supply - sl_avg_supply,
                "delta_min_supply": s_min_supply - sl_min_supply,
                "percent_avg_supply_change": avg_supply_pc,
            }
        }
       
    @staticmethod 
    def build_supply_series(history: list) -> list:
        return [t["total_supply_available"] for t in history]
    
    @staticmethod
    def build_inventory_series(history: list) -> list:
        return [t["total_inventory"] for t in history]
    
    @staticmethod
    def calculate_percent_change_supply(series: list[float]) -> list[float]:
        if not series:
            return []

        changes = []

        for i in range(1, len(series)):
            prev = series[i - 1]
            curr = series[i]

            if prev == 0:
                print("HELLO?")
                # Handle edge case explicitly
                if curr == 0:
                    change = 0.0  # no change
                else:
                    change = None  # undefined / skip / special case
            else:
                change = (curr - prev) / prev

            if change is not None:
                changes.append(change)

        return changes
            
    
    
    
        
        
    def _load_runs(self) -> None:
        """
        Load the runs from this experiment into the experiment analyzer.
        """
        
        
            
        if not self.execution_result:
            raise AttributeError("Expected attribute execution_result to be present.")
        
        self.shocked_run_manifest = self._load_run_manifest(self.shocked_execution_result)
        self.shockless_run_manifest = self._load_run_manifest(self.shockless_execution_result)
        self.shocked_run_history = self._load_run_history(self.shocked_execution_result)
        self.shockless_run_history = self._load_run_history(self.shockless_execution_result)
        
        self.shocked_run_path = self.shocked_run_manifest.get("run_output_path", "")
        self.shockless_run_path = self.shockless_run_manifest.get("run_output_path", "")
        if not self.shocked_run_path or not self.shockless_run_path:
            warnings.warn("Run paths were not assigned.")      
    
    def _load_run_manifest(self, run_result: dict, path: str | Path = None) -> dict:
        """Loads a runs manifest from the original run directory or the ExecutionResult

        Args:
            run_result(dict): Required run result from the execution result identifying which run manifest to load.
            path(str | Path): Optional path variable to manually control the path it loads the manifest from. Defaults to None
        Returns:
            dict: the loaded manifest.
        """
        if path:
            if isinstance(path, str):
                path = Path(path)
            elif not isinstance(path, Path):
                raise ValueError("The path passed is not a readable string or Path class.")
            
            if not path.exists():
                raise AttributeError("The path passed does not exist or is not a directory.")
            
        else:
            path = run_result.get("manifest", "")
            path = Path(path)
            if not path.exists():
                raise ValueError("The passed result contains a manifest path that does not exist.")
        
        manifest = {}
        
        with open(path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            
        if not manifest:
            raise Exception("There was an issue reading the manifest file.")
        
        return manifest
            
    def _load_run_history(self, run_result: dict, path: str | Path = None) -> List[dict]:
        """Loads a singular runs `history.json` from the original run directory.

        Args:
            run_result (dict): The specific run result dict from the `ExecutionResult`.
            path (str | Path, optional): A optional path to directly load a `history.json`. Defaults to None.

        Returns:
            List[dict]: The history.json loaded as a list of dictionaries. Convertable to list of `TimestepState`'s
        """
        if path:
            if isinstance(path, str):
                path = Path(path)
            elif not isinstance(path, Path):
                raise ValueError("The path passed is not a readable string or Path class.")
            
            if not path.exists():
                raise AttributeError("The path passed does not exist or is not a directory.")
            
        else:
            path = run_result.get("history")
            path = Path(path)
            if not path.exists():
                raise ValueError("The passed result contains a history json path that does not exist.")
        
        history = []
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)
            
        if not history:
            raise Exception("There was an erorr when attempting to load the history json.")
        
        return history
     
    @staticmethod       
    def _compute_mean_list(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0
        
    @staticmethod
    def _percent_change(old: float, new: float) -> float:
        if old == 0:
            return 0.0
        return ((new - old) / old) 
        
        
        