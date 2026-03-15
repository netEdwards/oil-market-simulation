from __future__ import annotations

from hmac import new
import math
import random
import numpy as np

from dataclasses import dataclass, field
from typing import Dict, List
from oilmarket.agents.agents import Producer, Consumer
from oilmarket.agents.buyer import Buyer
from oilmarket.agents.seller import Seller
from oilmarket.data.simulation import BuyerConfig, SellerConfig, SimulationConfig
from oilmarket.data.state import TimestepState, Transaction

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
        config: SimulationConfig,
        responsiveness: float = 0,
        timestep: int = None,
        ):
        self.config = config 
        seed        = self.config.seed
        self.rng    = np.random.default_rng(seed=seed)
        
        
        self.timestep = timestep
        if not self.timestep:
            raise Warning("No timestep was provided, this could affect logging and metrics in the simulation")
        
        
        # k = responsiveness (controls the scale at which sellers adjust prices in reaction to market changes.) 
        #NOTE: Possible Shock idea: You could create a shock that changes K, simulating economical overreaction in the market.
        if responsiveness == 0:
            self.k = self.config.sellers.pricing.responsiveness
        else:
            self.k = responsiveness
        
        self.sellers: List[Seller] = []
        self.buyers: List[Buyer]   = []
        
        self._init_config() #1 ✅
        self._init_buyers() #2 ✅
        self._init_sellers() #2 ✅
    
    
    def run_market_timestep(self):
        """Calculates and simulates the current timestep in clearing order first calculations last. The market class will retain all state from the current/previous timestep until the this function is called again on the same instance.
        
        
        """
        # Clear state. Replenish inventories. Calculate Demand.
        for s in self.sellers:
            s.units_sold = 0
            s.utilization = 0
            s.replenish()
            
        for b in self.buyers:
            b.active = True
            # REMAINING DEMAND"??? -- Just use the demand value for now, subtract units sold from demand.
        all_transactions = []
        # create loop to eval each buyer this timestep.
        
        total_units_sold = 0
        total_unmet_demand = 0
        
        for b in self.buyers:
            
            b.demand = b.generate_demand()
            #create subset of sellers k
            k = self._create_subset_sellers()
            #call select seller function
            selected_seller = b.select_seller(k=k)
            if not selected_seller:
                #NOTE: record unmet demand
                total_unmet_demand+=b.demand
                
                continue
            #use returned seller selection to create a transaction
            transaction = self._process_transaction(buyer=b, seller=selected_seller)
            #update units sold for that seller
            selected_seller.inventory-= transaction.units_sold
            selected_seller.units_sold += transaction.units_sold
            
            #update demand for that buyer
            b.demand -= transaction.units_sold
            total_unmet_demand+=b.demand #demand is 0 then nothing is added to total unmet demand.

            all_transactions.append(transaction)
            
        #create timestep state
        market_timestep = TimestepState(
            timestep=self.timestep,
            buyers=self.buyers,
            sellers=self.sellers,
            transactions=all_transactions,
            total_units_sold=...,
            total_unmet_demand=...,
            average_price=...
        )
        
        # calculate new seller prices.
        for s in self.sellers:
            s.update_utilization()
            s.calculate_new_price()




    def _process_transaction(self, buyer: Buyer, seller: Seller) -> Transaction:
        """
        Method to create a transaction in the market using subset of sellers k and then modifying seller and buyer instances. Result is a Transaction instance recording the transaction(s)
        
        Args:
        - Buyer: The buyer currently looking to make a transaction.
        Output:
        - Transaction: A `Transaction` instance with the transaction recorded.
        """
        ##buyer demand is purchase amount
        #subtract buyer demand from seller inventory
        # 
        units_sold = 0
        if buyer.demand > seller.inventory:
            units_sold = seller.inventory
        elif buyer.demand < seller.inventory:
            units_sold = seller.inventory - buyer.demand
            
        transaction = Transaction(
            timestep=self.timestep, 
            seller_id=seller.id, 
            buyer_id=buyer.id, 
            units_sold=units_sold, 
            unit_price=seller.price, 
            total_price=(units_sold * seller.price)
        )
        return transaction
            
            
            
        
        
    def _create_subset_sellers(self, size_k: int = 4) -> list[Seller]:
        """Returns a completely random subset of sellers in the class. The size of the subset can be changed with `size_k`.

        Args:
            size_k (int, optional): Determines the size of the subset (num of sellers in k). Defaults to 4.

        Returns:
            _type_: List
        """
        subset = self.rng.choice(self.sellers, size=size_k, replace=False)
        return subset.tolist()
                
        
        #created function to extract config values:
    def _init_config(self):
        if not self.config:
            raise ValueError("Configuration is corrupt or missing.")
        
        #just push all subclasses and instances to a new variable for ease of use.
        #may be removed for opimization later...
        self.shock_config   = self.config.shock
        self.buyers_config  = self.config.buyers
        self.sellers_config = self.config.sellers
        self.base_price     = self.config.base_price
        self.seed           = self.config.seed
            
            
    def _init_buyers(self) -> None:
        buyers = []
        
        num_buyers = self.buyers_config.count
        for i in range(num_buyers):
            buyers.append(Buyer(
                mean_wtp=self.buyers_config.wtp.mu,
                sigma=self.buyers_config.wtp.sigma,
                _min=self.buyers_config.wtp._min,
                _max=self.buyers_config.wtp._max,
                seed=self.config.seed,
                lambda_demand=self.buyers_config.demand.lambda_demand
            ))
        if not len(buyers) == num_buyers:
            raise Exception("ERROR: There was an issue when initializing all buyers in the market from the config.")
        
        self.buyers = buyers
        
    def _init_sellers(self) -> None:
        sellers = []
        t_util = self.sellers_config.pricing.target_utilization
        #create major sellers first
        majors = self.sellers_config.major
        m_count = majors.count
        for i in range(m_count):
            sellers.append(Seller(
                price=majors.init_price | self.config.base_price,
                inventory=majors.init_inventory,
                capacity=majors.capacity,
                prod_rate=majors.prod_rate,
                target_util=t_util, #currently broad across tiers
                tier="major"
            ))
        
        #create medium sellers
        m_sellers = self.sellers_config.medium
        md_count = m_sellers.count
        for i in range(md_count):
            sellers.append(Seller(
                price=m_sellers.init_price,
                inventory=m_sellers.init_inventory,
                prod_rate=m_sellers.prod_rate,
                capacity=m_sellers.capacity,
                target_util=t_util,
                tier="medium"
            ))
            
        #small sellers
        s_sellers = self.sellers_config.small
        s_count = s_sellers.count
        for i in range(s_count):
            sellers.append(Seller(
                price=s_sellers.init_price,
                inventory=s_sellers.init_inventory,
                prod_rate=s_sellers.prod_rate,
                capacity=s_sellers.capacity,
                target_util=t_util,
                tier="small"
            ))
            
        total_count = m_count + md_count + s_count
        if not len(sellers) == total_count:
            raise Exception("ERROR: There was an issue initializating all sellers in the market from the config.")
        
        self.sellers = sellers
        
            
    