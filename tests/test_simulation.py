#NOTE: This is to test end to end full loop of the simulation, timestepping and all.

from pathlib import Path
from unittest import result

from numpy import show_config

import oilmarket
import oilmarket.data
from oilmarket.data.simulation import SimulationConfig
import oilmarket.data.simulation
from oilmarket.data.state import TimestepState
import oilmarket.data.state
from oilmarket.simulation import Simulation

cfg_path = Path(__file__).parent / "test_configs" / "default.yaml"

s_config = SimulationConfig.from_yaml(cfg_path)
simulation = Simulation(config=s_config)

def test_simulation():
    result = simulation.run()
    assert result
    assert len(result) > 0
    assert type(result) == list, (f"Current type {type(result)}")
    
def test_simulation_and_plots():
    result = simulation.run()
    simulation.export_history_json()
    #graph results
    path_str = simulation.plot_price()
    print("Prices plotted... \nchecking file.")
    assert result
    print(f"Result {path_str}")
    path = Path(path_str)
    assert path.exists()