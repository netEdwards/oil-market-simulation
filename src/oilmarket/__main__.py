from __future__ import annotations

import yaml

from oilmarket.agents.agents import Producer, Consumer
from .market import Market
from oilmarket.shocks.shocks import Shock
from src.simulation import Simulation, SimulationConfig
import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt


def main() -> None:
    with open("configs/default.yaml", "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    cfg = SimulationConfig(
        seed=int(raw.get("seed", 42)),
        ticks=int(raw.get("ticks", 100)),
        shock=raw.get("shock"),
    )

    shock = None
    if cfg.shock:
        shock = Shock(
            start_tick=int(cfg.shock["tick"]),
            duration=int(cfg.shock.get("duration", 10)),
            multiplier=float(cfg.shock["multiplier"]),
        )

    # Simple population
    producers = [Producer(capacity=100.0) for _ in range(int(raw.get("num_producers", 5)))]
    consumers = [Consumer(base_demand=120.0) for _ in range(int(raw.get("num_consumers", 5)))]

    market = Market(producers=producers, consumers=consumers, price=float(raw.get("base_price", 100.0)))
    sim = Simulation(config=cfg, market=market, shock=shock)

    history = sim.run()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join("runs", timestamp)
    os.makedirs(run_dir, exist_ok=True)

    csv_path = os.path.join(run_dir, "history.csv")

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)
        
    prices = [h["price"] for h in history]
    ticks = [h["t"] for h in history]

    plt.figure()
    plt.plot(ticks, prices)
    plt.xlabel("Tick")
    plt.ylabel("Price")
    plt.title("Oil Price Over Time")

    plot_path = os.path.join(run_dir, "price.png")
    plt.savefig(plot_path)
    plt.close()
    print(f"Ran {len(history)} ticks. Final price={history[-1]['price']:.2f}")


if __name__ == "__main__":
    main()