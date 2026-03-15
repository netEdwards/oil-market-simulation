


from dataclasses import dataclass
from uuid import uuid4
import uuid

import numpy as np
from numpy.random import Generator

from oilmarket.agents.seller import Seller



class Buyer:
    def __init__(
        self, 
        mean_wtp: float = 0.0, 
        sigma: float = 0.0, 
        _min: float = 0.0, 
        _max: float = 0.0, 
        seed: str | int = None, 
        active: bool = False, 
        lambda_demand: float = 4.0,
        wtp: float = 0.0, #future shock use
        rng: Generator = None,
    ) -> None:
        
        self.id = str(uuid.uuid4())
        #self.rng = np.random.default_rng(seed=seed) MOVED TO MARKET FOR GLOBAL RNG USE IN AGENT BEHAVIOR
        self.rng = rng #needs fault tolerance for missing rng input but is fine for now
        self.mean_wtp = mean_wtp
        self.sigma = sigma
        self._min = _min
        self._max = _max
        self.seed = seed 
        self.active = active
        self.lambda_i = lambda_demand
        
        self.wtp = self._generate_wtp()
        self.demand = self.generate_demand() #may remove 
        
    
    def generate_demand(self):
        """
        A method to generate a buyers demand using the Poisson random selection method.
        """
        demand = self.rng.poisson(self.lambda_i)
        return demand
        
        
    def select_seller(self, k: list[Seller]) -> Seller:
        """
        Method to select a seller from a given subset k sellers
        """
        # for each seller in subset K is the price per unit lower than the wtp, 
        # then use demand to calculate how much they can buy from that seller. 
        # If they cannot buy all of there demand (due to supplier check and more) then demand is unmet. Next seller.
        
        if not k:
            return None
        
        #Filter sellers where price is greater than wtp
        affordable = [s for s in k if s.price <= self.wtp]

        if not affordable:
            return None
                
        return min(affordable, key=lambda s: s.price)
        
        
    def _generate_wtp(self) -> float:
        """
        Function to generate the willingness to pay value for the simulation run. 
        """
        mu = self.mean_wtp
        sigma = self.sigma
        _min = self._min
        _max = self._max
        
        while True:
            x = self.rng.normal(mu, sigma) #generate one normal dist number from the mean and deviation
            if _min <= x <= _max: #only return whats inside the min and max
                return x