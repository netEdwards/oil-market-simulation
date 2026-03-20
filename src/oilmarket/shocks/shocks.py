from __future__ import annotations

from dataclasses import dataclass



from oilmarket.agents.seller import Seller
from oilmarket.data.simulation import ShockConfig, SimulationConfig
from oilmarket.data.state import ShockSnapshot

"""
To apply a shock in the most basic form, we take in the shock values from the config. We then apply something like a production rate reducer. It goes like this:
- Use severity (param/input) as the reduced rate. Example Prod Rate @100% is 100. If severity is 0.2 thats a 20% reduction. 1-severity = 80% the new operating production rate.
- Apply this to a top seller for now. It will have the most visual impact. 
"""

class Shock:
    def __init__(
        self,
        config: SimulationConfig,
        ):
        shock_config = config.shock
        ticks = config.ticks
        self.severity = shock_config.severity
        if self.severity < 0 > 1:
            raise ValueError("Shock severity in the config needs to be a fraction or decimal between 0 and 1.")
        
        
        self.duration = shock_config.duration
        self.start_time = shock_config.start_time
        self.target = shock_config.target #currently required, but a bit unrealiable for full user inputs.
        if isinstance(self.start_time, float):
            self.start_tick = round(ticks * self.start_time) #(total sim ticks) * (fractional start time)
        elif isinstance(self.start_time, int):
            self.start_tick = shock_config.start_time
        else:
            raise ValueError("Start time for the Shock is not usable.")
        
        if (self.start_tick + self.duration) > config.ticks:
            self.end_tick = config.ticks
            raise Warning("The input duration for the shock is longer than the simulation length.")
            
            
        self.end_tick = self.start_tick + self.duration
    
    def apply_shock(self, sellers: list[Seller], timestep: int) -> list[ShockSnapshot]:
        """A method that will use the input config target to select a seller and apply a shock to that sellers instance.

        Args:
            timestep (int): The current timestep.
        """
        sellers_to_shock = []
        if self.target == "top_seller":
            for s in sellers:
                if s.tier == "major":
                    sellers_to_shock.append(s)
        elif self.target == "small_sellers":
            for s in sellers:
                if s.tier == "small":
                    sellers_to_shock.append(s)
        shocks = []        
        for s in sellers_to_shock:
            shock = self._apply_shock(s, timestep)
            shocks.append(shock)
            
        return shocks
                    
    
    def _apply_shock(self, seller: Seller, timestep: int) -> ShockSnapshot:
        """Method that attempts to apply a shock to a seller instance in memory.

        Args:
            seller (Seller): The seller the shock will be applied to.
            timestep (int): The current timestep.
        """
        is_active = self.is_active(tick=timestep)
        if not is_active:
            print("There is no shock to apply for the current tick.")
            return
        
        reduced_supply_amount = (1-self.severity)
        previous_rate = seller.prod_rate
        seller.prod_rate = round((seller.prod_rate * reduced_supply_amount), 2)
        print(f"Shock applied for tick, {timestep}. Reduce seller {seller.id} production rate by {self.severity}.")
        print(f"Previous production rate was: {previous_rate}. \n New rate is: {seller.prod_rate}")
        return ShockSnapshot(
            severity=self.severity,
            tick=timestep,
            prev_rate=previous_rate,
            new_rate=seller.prod_rate,
            sellers_id=seller.id,
        )
        
        
    
    def is_active(self, tick: int) -> bool:
        return self.start_tick <= tick < self.end_tick
    