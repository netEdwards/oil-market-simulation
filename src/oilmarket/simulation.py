from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from yaml import Mark

from oilmarket.data.state import TimestepState
from oilmarket.market import Market
from oilmarket.shocks.shocks import Shock
from oilmarket.data.simulation import SimulationConfig

    

class Simulation:
    
    def __init__(
        self,
        config: SimulationConfig,
    ):
        self.config = config
        self.market = Market(config=config)
        self.history: list[TimestepState] = []
        
    
    def run(self) -> List[Dict[str, Any]]:
        """Coor descrete time simulation loop.
        Each tick executes the conceptual 'activity diagram' steps in order.

        """
        
        for t in range(self.config.ticks):
            #determine whetther shock is active this tick
            tick_result = self.market.run_market_timestep(t)
            
            self.history.append(
                tick_result
            )
            
        return self.history