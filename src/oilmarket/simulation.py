from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from oilmarket.data.state import TimestepState
from oilmarket.market import Market
from oilmarket.shocks.shocks import Shock
from oilmarket.data.simulation import SimulationConfig

    
@dataclass
class Simulation:
    config: SimulationConfig
    market: Market
    shock: Optional[Shock] = None
    history: list[TimestepState]
    
    def run(self) -> List[Dict[str, Any]]:
        """Coor descrete time simulation loop.
        Each tick executes the conceptual 'activity diagram' steps in order.

        """
        #1. Init / reset any run-state
        self.market = Market(config=self.config)
        
        for t in range(self.config.ticks):
            #determine whetther shock is active this tick
            
                
            tick_result = self.market.run_market_timestep(t)
            
            self.history.append(
                tick_result
            )
            
        return self.history