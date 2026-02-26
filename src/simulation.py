from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from oilmarket.market import Market
from oilmarket.shocks.shocks import Shock


@dataclass
class SimulationConfig:
    seed: int = 42
    ticks: int = 100
    shock: Optional[Dict[str, Any]] = None
    
@dataclass
class Simulation:
    config: SimulationConfig
    market: Market
    shock: Optional[Shock] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def run(self) -> List[Dict[str, Any]]:
        """Coor descrete time simulation loop.
        Each tick executes the conceptual 'activity diagram' steps in order.

        """
        #1. Init / reset any run-state
        self.market.reset(seed=self.config.seed)
        
        for t in range(self.config.ticks):
            #determine whetther shock is active this tick
            shock_multiplier = 1.0
            shock_active = False
            if self.shock and self.shock.is_active(t):
                shock_active = True
                shock_multiplier = self.shock.multiplier
                
            tick_result = self.market.step(tick=t, shock_multiplier=shock_multiplier)
            
            self.history.append(
                {
                    "t": t,
                    "price": tick_result["price"],
                    "total_supply": tick_result["total_supply"],
                    "total_demand": tick_result["total_demand"],
                    "shock_active": shock_active,
                }
            )
            
        return self.history