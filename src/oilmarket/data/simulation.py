

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ShockConfig:
    tick: int
    duration: int
    multiplier: float
    
@dataclass
class BuyerWTPConfig:
    dist: str
    mu: float
    sigma: float
    _min: float
    _max: float
    
@dataclass
class BuyerDemandConfig:
    lambda_demand: float
    
@dataclass
class BuyerConfig:
    count: int
    wtp: BuyerWTPConfig
    demand: BuyerDemandConfig
    
@dataclass
class PricingConfig:
    min_price: float
    target_utilization: float
    responsiveness: float
    
@dataclass
class SellerTierConfig:
    count: int
    prod_rate: float
    capacity: float
    init_inventory: float
    init_price: float
    
@dataclass
class SellerConfig:
    major: SellerTierConfig
    medium: SellerTierConfig
    small: SellerTierConfig
    pricing: PricingConfig
    
@dataclass
class SimulationConfig:
    seed: int
    ticks: int
    base_price: float
    shock: ShockConfig
    buyers: BuyerConfig
    sellers: SellerConfig
    
    #ADD POST INIT?
    
    @classmethod
    def from_yaml(cls, path: str | Path) -> "SimulationConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SimulationConfig":
        shock = ShockConfig(**data["shock"])
        
        buyers_raw = data["buyers"]
        buyer_wtp = BuyerWTPConfig(**buyers_raw["wtp"])
        buyer_demand = BuyerDemandConfig(**buyers_raw["demand"])
        buyers = BuyerConfig(
            count=buyers_raw["count"],
            wtp=buyer_wtp,
            demand=buyer_demand,
        )
        sellers_raw = data["sellers"]
        pricing = PricingConfig(**sellers_raw["pricing"])
        sellers = SellerConfig(
            major=SellerTierConfig(**sellers_raw["major"]),
            medium=SellerTierConfig(**sellers_raw["medium"]),
            small=SellerTierConfig(**sellers_raw["small"]),
            pricing=pricing,
        )

        return cls(
            seed=data["seed"],
            ticks=data["ticks"],
            base_price=data["base_price"],
            shock=shock,
            buyers=buyers,
            sellers=sellers,
        )