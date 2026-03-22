from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid

from yaml import Mark
import json
from dataclasses import asdict
from pathlib import Path
from oilmarket.data.state import TimestepState
from oilmarket.market import Market
from oilmarket.shocks.shocks import Shock
from oilmarket.data.simulation import SimulationConfig

import matplotlib.pyplot as plot

class Simulation:
    
    def __init__(
        self,
        config: SimulationConfig,
    ):
        self.config = config
        self.market = Market(config=config)
        self.history: list[TimestepState] = []
        self.run_id = uuid.uuid4()
        
    
    def run(self) -> list[TimestepState]:
        """Coor descrete time simulation loop.
        Each tick executes the conceptual 'activity diagram' steps in order.

        """
        
        for t in range(self.config.ticks):
            #determine whetther shock is active this tick
            tick_result = self.market.run_market_timestep(t)
            
            self.history.append(
                tick_result
            )
            
        return self.history
    
    def plot_price(self, avg_prices: list[float] = None) -> str:
        """Generates a plot of prices over time using matplotlib. 
        To automatically calulate seller average prices in order, leave param avg_prices as None (default).
        
        Args:
        - avg_prices: The average seller prices per timestep. default: None
        Output:
        - str: .png file path.
        """
        if not avg_prices:
                avg_prices = self._calculate_avg_prices()

        timesteps = [state.timestep for state in self.history]
        valid_timesteps = timesteps[1:]
        valid_prices = avg_prices[1:]
        plot.figure(figsize=(10, 5))
        plot.plot(valid_timesteps, valid_prices, marker="o")
        plot.title("Average Price Over Time")
        plot.xlabel("Timestep")
        plot.ylabel("Price")
        plot.ylim(min(valid_prices) - 2, max(valid_prices) + 2)
        plot.grid(True)
        filename = f"avg_price-{self.run_id}.png"
        output_dir = self.config.output_path
        plot.savefig(output_dir / filename)
        return f"{output_dir}/{filename}"
        
    def _calculate_avg_prices(self) -> list[float]:
        """Returns the average seller price for each timestep."""
        avg_prices = []

        for t in self.history:
            if not t.sellers:
                continue

            total_price = 0
            for s in t.sellers:
                
                total_price += s.price

            avg = total_price / len(t.sellers)
            avg_prices.append(avg)

        print("\n\n Average Prices: ", avg_prices, "\n\n")
        return avg_prices
    
    def export_history_json(self) -> str:
        output_dir = self.config.output_path
        output_dir.mkdir(parents=True, exist_ok=True)

        filepath = output_dir / "history.json"

        history_payload = []

        for state in self.history:
            state_dict = {
                "timestep": state.timestep,
                "buyers": [
                    {
                        "id": b.buyer_id,
                        "wtp": b.wtp,
                        "demand": b.initial_demand,
                        "wtp": b.wtp,
                        "unmet_demand": b.unmet_demand,
                    }
                    for b in state.buyers
                ],
                "sellers": [
                    {
                        "id": s.seller_id,
                        "price": s.price,
                        "inventory": s.inventory,
                        "prod_rate": s.prod_rate,
                        "capacity": s.capacity,
                        "utilization": s.utilization,
                        "units_sold": s.units_sold,
                    }
                    for s in state.sellers
                ],
                "transactions": [
                    {
                        "id": tx.id,
                        "buyer_id": tx.buyer_id,
                        "seller_id": tx.seller_id,
                        "units_sold": tx.units_sold,
                        "unit_price": tx.unit_price,
                        "total_price": tx.total_price,
                        "timestep": tx.timestep,
                    }
                    for tx in state.transactions
                ],
                "total_units_sold": state.total_units_sold,
                "total_unmet_demand": state.total_unmet_demand,
                "average_price": state.average_price,
            }
            history_payload.append(state_dict)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(history_payload, f, indent=2, default=str)

        return str(filepath)