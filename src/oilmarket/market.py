from __future__ import annotations

from hmac import new
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List
from oilmarket.agents.agents import Producer, Consumer
from oilmarket.agents.buyer import Buyer
from oilmarket.agents.seller import Seller

"""
This market class is old. It was for a demo of the concept....

"""
@dataclass
class OldMarket:
    producers: List[Producer] = field(default_factory=list)
    consumers: List[Consumer] = field(default_factory=list)
    price: float = 100.0
    k: float = 0.1
    
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
        
class Market:
    def __init__(
        self,
        num_sellers: int = 0,
        num_buyers: int = 0,
        config: dict = None,
        target_utilization: float = 0.0,
        k: float = 0.80,
        seed: int = None
        ):
        self.seed = seed
        self.num_sellers = num_sellers
        self.num_buyers = num_buyers
        self.config = config
        self.target_util = target_utilization
        self.k = k
        
        self.sellers = []
        
        #initialize buyers and sellers
        for i in range(self.num_sellers):
            new_seller = Seller(price=config.seller.price, prod_rate=config.seller.prod_rate, target_util=target_utilization)
            self.sellers.append()
            
        for i in range(self.num_buyers):
            new_buyer = Buyer(mean_wtp=config.buyers[i].price, sigma=..., _min=..., _max=..., seed=self.seed)
            
    