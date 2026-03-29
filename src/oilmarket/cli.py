from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from oilmarket.data.simulation import SimulationConfig
from oilmarket.simulation import Simulation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oilmarket",
        description="Run the oil market simulation from a config file.",
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to the simulation config file.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Optional override for number of timesteps.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional override for random seed.",
    )
    parser.add_argument(
        "--no-history-json",
        action="store_true",
        help="Skip exporting history.json.",
    )

    return parser


def load_config(config_path: str) -> SimulationConfig:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    # Adjust this if your project uses a different config loader
    return SimulationConfig.from_yaml(path)


def apply_overrides(config: SimulationConfig, steps: int | None, seed: int | None) -> SimulationConfig:
    if steps is not None:
        config.timesteps = steps
    if seed is not None:
        config.seed = seed
    return config


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = load_config(args.config)
    config = apply_overrides(config=config, steps=args.steps, seed=args.seed)

    sim = Simulation(config=config)
    sim.run()

    outputs: dict[str, Any] = sim.export_all_outputs()

    if not args.no_history_json:
        outputs["history_json"] = sim.export_history_json()

    print("\nSimulation complete.")
    print(f"Run ID: {sim.run_id}")
    print(f"Output directory: {sim.output_path}")

    print("\nGenerated outputs:")
    for name, path in outputs.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()