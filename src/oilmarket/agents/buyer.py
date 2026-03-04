


from dataclasses import dataclass
from uuid import uuid4
import uuid


@dataclass
class Buyer:
    id: str = "NIB" # default is non-initiated buyer or nib. Used to filter out buyers that were created and not initiated for debugging
    wtp: float = 0.0
    avg_demand: float = 0.0
    active: bool = False #is the buyer currently buying
    
    def __init__(self):
        self.id = str(uuid4())
        
    
    def generate_demand(self):
        """
        A method to generate a buyers demand using the Poisson random selection method.
        """
        
    def select_seller(self, k):
        """
        Method to select a seller from a given subset k sellers
        """