from pathlib import Path

import pytest

from oilmarket.data.simulation import SimulationConfig
from oilmarket.data.state import TimestepState
from oilmarket.market import Market
from oilmarket.simulation import Simulation

cfg_path = Path(__file__).parent / "test_configs" / "default.yaml"


def test_market_timestep_run():
    #setup simulation class.
    #can use test_config or default yaml
    #validate that one timestep run in Market returns a TimestepState
    config = SimulationConfig.from_yaml(path=cfg_path)
    market = Market(config)
    
    result = market.run_market_timestep(0)
    assert result
    assert type(result) == TimestepState
    print(result)
    
    