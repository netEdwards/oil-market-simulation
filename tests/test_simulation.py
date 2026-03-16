#NOTE: This is to test end to end full loop of the simulation, timestepping and all.

from pathlib import Path
from unittest import result

import oilmarket
import oilmarket.data
from oilmarket.data.simulation import SimulationConfig
import oilmarket.data.simulation
from oilmarket.data.state import TimestepState
import oilmarket.data.state
from oilmarket.simulation import Simulation

cfg_path = Path(__file__).parent / "test_configs" / "default.yaml"

def test_simulation():
    s_config = SimulationConfig.from_yaml(cfg_path)
    simulation = Simulation(config=s_config)
    
    result = simulation.run()
    assert result
    assert len(result) > 0
    assert type(result) == list, (f"Current type {type(result)}")