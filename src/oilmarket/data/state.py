

from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass
class Transaction:
    id: str =               uuid.uuid4()
    timestep:               int
    seller_id:              str
    buyer_id:               str
    units_sold:             float = 0.0
    unit_price:             float = 0.0
    total_price:            float = 0.0
    
@dataclass
class BuyerSnapshot:
    buyer_id:               str
    wtp:                    float
    initial_demand:         float = 0.0
    remaining_demand:       float = 0.0
    unmet_demand:           float = 0.0

@dataclass    
class SellerSnapshot:
    seller_id:              str
    price:                  float
    inventory:              float = 0.0
    prod_rate:              float = 0.0
    capacity:               int = 0
    units_sold:             float = 0.0
    utilization:            float = 0.0
    
@dataclass
class TimestepState:
    timestep:               int = 0
    buyers:                 List[BuyerSnapshot] = field(default_factory=list)
    sellers:                List[SellerSnapshot] = field(default_factory=list)
    transactions:           List[Transaction] = field(default_factory=list)
    total_units_sold:       float = 0.0
    total_unmet_demand:     float = 0.0
    average_price:          float = 0.0