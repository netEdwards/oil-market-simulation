from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List
from oilmarket.agents.agents import Producer, Consumer


@dataclass
class Market:
    producers: List[Producer] = field(default_factory=list)
    consumers: List[Consumer] = field(default_factory=list)
    price: float = 100.0
    k: float = 0.05
    
    def reset(self, seed: int) -> None:
        random.seed(seed)
        
    def step(self, tick:int, shock_multiplier: float = 1.0) -> Dict[str, float]:
        # Producers produce (shock affects capacity)
        total_supply = 0.0
        for p in self.producers:
            total_supply += p.produce(price=self.price, capacity_multiplier = shock_multiplier)
            
        # Consumers demand (later shocks will affect demand as well)
        total_demand = 0.0
        for c in self.consumers:
            total_demand += c.demand(price=self.price)
            
        # Market clearing=ish price update
        imbalance = (total_demand - total_supply)
        denom = max(1.0, total_supply)
        self.price *= math.exp(self.k * (imbalance / denom))
        
        #clamp to prevent runaway
        self.price = max(1.0, min(self.price, 10_000.0))

        return {
            "price": float(self.price),
            "total_supply": float(total_supply),
            "total_demand": float(total_demand),
        }