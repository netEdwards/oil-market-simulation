
from dataclasses import dataclass


@dataclass
class Seller:
    price: float = 0.0
    inventory: float = 0.0
    prod_rate: float = 0.0
    capacity: float = 0.0
    
    def __init__(self):
        pass
    
    def replenish(self):
        """ 
        Method that will replenish a sellers inventory.
        """
        pass
    def update_price(self):
        """
        Method to update the sellers current price
        """