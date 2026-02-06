# Oil Market Simulation

Discrete-time agent-based simulation of supply shocks and price dynamics in an oil market.

## Overview

This project implements a discrete-time, agent-based simulation of a commodity market with scarce resources, using the oil industry as a representative case. The simulation models interactions between buyers and sellers under stochastic demand and examines how market prices, inventories, and unmet demand evolve following sudden supply disruptions.

The model emphasizes decentralization and emergence: market-level behavior arises from local agent interactions rather than centralized optimization or global knowledge.

## System Model

The simulation consists of four primary components:

**Buyers**
Generate stochastic demand and purchase from sellers subject to willingness-to-pay constraints.

**Sellers**
Produce a limited resource, manage inventory, and adjust prices adaptively based on sales outcomes.

**Market Mechanism**
Facilitates transactions between buyers and sellers using rule-based allocation.

**Shock Events**
Exogenous disruptions that reduce production capacity for selected sellers over time.

Time advances in discrete steps, with production, demand generation, transactions, price updates, and logging occurring once per timestep.

## Key Features

- Discrete-time agent-based modeling (ABM)
- Stochastic demand generation
- Trait-based buyer willingness-to-pay
- Adaptive seller pricing via feedback rules
- Exogenous supply shock modeling
- Reproducible simulation runs via random seeding
- Structured logging for post-run analysis

## Repository Structure

src/
  agents/
    buyer.py
    seller.py
  market.py
  simulation.py
  shocks.py
  logging/
    metrics_logger.py
  config.py
  main.py

docs/
  uml_classes.pdf
  uml_activity.pdf

outputs/
  (generated simulation logs – gitignored)

## Running the Simulation

Implementation is in progress.

Planned usage:

python -m src.main --seed 42

Simulation parameters (number of agents, demand distributions, shock schedules) will be configurable via a central configuration module.

## Outputs

Each simulation run will produce structured logs containing:
= Seller prices and inventory levels
= Transaction volumes
- Unmet demand
- Market response following shock events
These outputs support both single-run inspection and aggregate statistical analysis across multiple runs.

## Status

This repository currently contains the conceptual design, UML diagrams, and implementation scaffolding as part of an academic modeling and simulation project. Full implementation and experimental analysis will be developed in subsequent milestones.

License

MIT License
