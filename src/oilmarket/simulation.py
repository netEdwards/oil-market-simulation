from __future__ import annotations

import csv
from typing import Any
import uuid
import json
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
        self.output_path = Path(self.config.output_path) / f"run-{self.run_id}"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
    
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
    
    
    
    """
    ==========================================
    Data aggregration and output creation
    ==========================================
    """
    
    def plot_price(self) -> str:
        rows = self._build_timestep_rows()
        if not rows:
            return str(self.output_path / f"avg_price-{self.run_id}.png")

        timesteps = [r["timestep"] for r in rows]
        avg_prices = [r["average_price"] for r in rows]

        plot.figure(figsize=(10, 5))
        plot.plot(timesteps, avg_prices, marker="o")
        plot.title("Average Price Over Time")
        plot.xlabel("Timestep")
        plot.ylabel("Average Price")
        plot.grid(True)

        if avg_prices:
            ymin = min(avg_prices)
            ymax = max(avg_prices)
            if ymin != ymax:
                plot.ylim(ymin - 2, ymax + 2)

        filepath = self.output_path / f"avg_price-{self.run_id}.png"
        plot.savefig(filepath, bbox_inches="tight")
        plot.close()

        return str(filepath)
    
    def plot_supply_demand(self) -> str:
        rows = self._build_timestep_rows()
        if not rows:
            return str(self.output_path / f"supply_demand-{self.run_id}.png")

        timesteps = [r["timestep"] for r in rows]
        demand = [r["total_demand"] for r in rows]
        supply_available = [r["total_supply_available"] for r in rows]
        inventory = [r["total_inventory"] for r in rows]

        plot.figure(figsize=(10, 5))
        plot.plot(timesteps, demand, marker="o", label="Total Demand")
        plot.plot(timesteps, supply_available, marker="o", label="Supply Available")
        plot.plot(timesteps, inventory, marker="o", label="Ending Inventory")
        plot.title("Supply and Demand Over Time")
        plot.xlabel("Timestep")
        plot.ylabel("Units")
        plot.grid(True)
        plot.legend()

        filepath = self.output_path / f"supply_demand-{self.run_id}.png"
        plot.savefig(filepath, bbox_inches="tight")
        plot.close()

        return str(filepath)
    
    def plot_fulfillment(self) -> str:
        rows = self._build_timestep_rows()
        if not rows:
            return str(self.output_path / f"fulfillment-{self.run_id}.png")

        timesteps = [r["timestep"] for r in rows]
        fulfilled = [r["total_units_sold"] for r in rows]
        unmet = [r["total_unmet_demand"] for r in rows]

        plot.figure(figsize=(10, 5))
        plot.plot(timesteps, fulfilled, marker="o", label="Fulfilled Units")
        plot.plot(timesteps, unmet, marker="o", label="Unmet Demand")
        plot.title("Demand Fulfillment Over Time")
        plot.xlabel("Timestep")
        plot.ylabel("Units")
        plot.grid(True)
        plot.legend()

        filepath = self.output_path / f"fulfillment-{self.run_id}.png"
        plot.savefig(filepath, bbox_inches="tight")
        plot.close()

        return str(filepath)
    
    def export_all_outputs(self) -> dict[str, str]:
        outputs = {
            "timesteps_csv": self.export_timesteps_csv(),
            "sellers_csv": self.export_sellers_csv(),
            "buyers_csv": self.export_buyers_csv(),
            "transactions_csv": self.export_transactions_csv(),
            "price_plot": self.plot_price(),
            "supply_demand_plot": self.plot_supply_demand(),
            "fulfillment_plot": self.plot_fulfillment(),
        }
        return outputs
    
    

    
    
    def export_history_json(self) -> str: 
        filepath = self.output_path / "history.json"

        history_payload = []

        for state in self.history:
            state_dict = {
                "timestep": state.timestep,
                "buyers": [
                    {
                        "id": b.buyer_id,
                        "wtp": b.wtp,
                        "demand": b.initial_demand,
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
    
    def export_timesteps_csv(self) -> str:
        rows = self._build_timestep_rows()
        return self._write_csv("timesteps.csv", rows)
    
    def export_sellers_csv(self) -> str:
        rows = self._build_seller_rows()
        return self._write_csv("sellers.csv", rows)
    
    def export_buyers_csv(self) -> str:
        rows = self._build_buyer_rows()
        return self._write_csv("buyers.csv", rows)
    
    def export_transactions_csv(self) -> str:
        rows = self._build_transaction_rows()
        return self._write_csv("transactions.csv", rows)
    
    
    """
    ==========================================
    Utility and private functions
    ==========================================
    """
    
    def _build_transaction_rows(self) -> list[dict[str, Any]]:
        rows = []

        for t in self.history:
            for tx in t.transactions:
                rows.append({
                    "run_id": str(self.run_id),
                    "timestep": tx.timestep,
                    "transaction_id": str(tx.id),
                    "buyer_id": tx.buyer_id,
                    "seller_id": tx.seller_id,
                    "units_sold": tx.units_sold,
                    "unit_price": tx.unit_price,
                    "total_price": tx.total_price,
                    "buyer_wtp": tx.buyer_wtp,
                    "remaining_demand": tx.remaining_demand,
                })

        return rows    
    
    def _build_buyer_rows(self) -> list[dict[str, Any]]:
        rows = []

        for t in self.history:
            for b in t.buyers:
                rows.append({
                    "run_id": str(self.run_id),
                    "timestep": t.timestep,
                    "buyer_id": b.buyer_id,
                    "wtp": b.wtp,
                    "initial_demand": b.initial_demand,
                    "unmet_demand": b.unmet_demand,
                    "fulfilled_demand": b.initial_demand - b.unmet_demand,
                    "served": (b.initial_demand - b.unmet_demand) > 0,
                })

        return rows
    
    def _build_seller_rows(self) -> list[dict[str, Any]]:
        rows = []

        for t in self.history:
            for s in t.sellers:
                rows.append({
                    "run_id": str(self.run_id),
                    "timestep": t.timestep,
                    "seller_id": s.seller_id,
                    "price": s.price,
                    "inventory": s.inventory,
                    "prod_rate": s.prod_rate,
                    "capacity": s.capacity,
                    "units_sold": s.units_sold,
                    "utilization": s.utilization,
                })

        return rows
    
    def _build_timestep_rows(self) -> list[dict[str, Any]]:
        """Takes self.history and creates a dict of timestep attrs (not nested attrs)"""
        rows = []
        for t in self.history:
            row = {
                "run_id":                   self.run_id,
                "timestep":                 t.timestep,
                "total_units_sold":         t.total_units_sold,
                "total_demand":             t.total_demand,
                "total_inventory":          t.total_inventory,
                "total_supply_available":   t.total_supply_available,
                "min_price":                t.min_price,
                "max_price":                t.max_price,
                "shock_active":             t.shock_active,
                "total_unmet_demand":       t.total_unmet_demand,
                "average_price":            t.average_price,
                "transaction_count" :       t.transaction_count,
            }
            rows.append(row)
            
        return rows
    
    def _write_csv(self, filename: str, rows: list[dict[str, Any]]) -> str:
        filepath = self.output_path / filename

        if not rows:
            return str(filepath)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        return str(filepath)
    
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