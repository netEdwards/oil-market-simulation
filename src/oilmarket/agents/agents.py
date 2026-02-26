from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Producer:
    capacity: float
    sensitivity: float = 0.01
    
    def produce(self, price: float, capacity_multiplier: float = 1.0) -> float:
        cap = self.capacity * capacity_multiplier
        #higher price => slightly higher util
        utilization = min(1.0, 0.5 + self.sensitivity * (price - 50.0))
        return max(0.0, cap*utilization)
    
@dataclass
class Consumer:
    base_demand: float
    price_elasticity: float = 0.01  # higher => demand drops faster with price

    def demand(self, price: float) -> float:
        # higher price => lower demand
        demand = self.base_demand * (1.0 / (1.0 + self.price_elasticity * price))
        return max(0.0, demand)