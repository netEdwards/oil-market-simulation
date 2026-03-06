


from dataclasses import dataclass
from uuid import uuid4
import uuid

import numpy as np



class Buyer:
    def __init__(
        self, 
        mean_wtp: float = 0.0, 
        signma: float = 0.0, 
        _min: float = 0.0, 
        _max: float = 0.0, 
        seed: str | int = None, 
        active: bool = False, 
        wtp: float = 0.0) -> None:
        
        self.id = str(uuid.uuid4())
        self.rng = np.random.default_rng(seed=seed)
        self.mean_wtp = mean_wtp
        self.sigma = signma
        self._min = _min
        self._max = _max
        self.seed = seed 
        self.active = active
        
        self.wtp = self.generate_wtp()
        
        
    
    def generate_demand(self):
        """
        A method to generate a buyers demand using the Poisson random selection method.
        """
        
    def select_seller(self, k):
        """
        Method to select a seller from a given subset k sellers
        """
        
    def generate_wtp(self) -> float:
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