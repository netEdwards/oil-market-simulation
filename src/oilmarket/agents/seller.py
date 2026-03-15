
from dataclasses import dataclass
from typing import Literal
import uuid



class Seller:
    price:      float = 0.0
    inventory:  float = 0.0
    prod_rate:  float = 0.0
    capacity:   float = 0.0

    
    def __init__(
        self,
        id: str = "",
        price:          float = 0.0,
        inventory:      float = 0.0,
        prod_rate:      float = 0.0,
        capacity:       float = 0.0,
        target_util:    float = 0.80,
        tier:           Literal["major", "medium", "small"] = None,
        ):
        self.id          = str(uuid.uuid4())
        self.price       = price
        self.inventory   = inventory
        self.prod_rate   = prod_rate
        self.capacity    = capacity
        self.target_util = target_util
        self.tier        = tier
        
        #variable util vars
        self.utilization = 0
        self.units_sold  = 0
        
        
    def update_utilization(self):
        """Updates the utlization for the seller.
        """
        
        if self.units_sold == 0:
            #log units sold as 0
            return
        util = self.units_sold / self.prod_rate
        self.utilization = util
        
    def _rest(self):
        """Resets timestep based values to normals.
        """
        self.utilization = 0
        self.units_sold = 0
    
    def replenish(self):
        """ 
        Method that will replenish a sellers inventory.
        """
        new_inventory = self.prod_rate + self.inventory
        if new_inventory > self.capacity:
            new_inventory = self.capacity
            #log excess produced
            
        self.inventory = new_inventory
        
        
        
    def calculate_new_price(self, k):
        """
        Changes the current price to the next timesteps calculated price
        
        Args:
        - k: Resposivness constant - 
        """
        
        cur_price = self.price
        util = self.utilization
        t_uti = self.target_util
        new_price = max(0, (cur_price * (1+k*(util - t_uti)) ))
        self.price = round(new_price, 2)
        
    def update_units_sold(self, units):
        if not type(units) == int:
            raise ValueError("Type mismtach between input units and Seller.units_sold")
        
        self.units_sold = units