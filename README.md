# Oil Market Simulation

**CS 4632 -- Modeling & Simulation**\
Adrian Edwards

------------------------------------------------------------------------

## Project Status

### What's Implemented So Far

The current implementation provides a functioning discrete-time
agent-based market simulation framework. The system includes:

-   A discrete-time simulation loop (`Simulation.run()`)
-   A `Market` class that aggregates supply and demand
-   `Producer` and `Consumer` agent classes
-   An exogenous `Shock` mechanism
-   YAML-based configuration (`configs/default.yaml`)
-   CSV output logging
-   Automatic time-series visualization of price dynamics

The model simulates supply-demand imbalance and updates price using an
exponential feedback adjustment rule. Experimental runs demonstrate
equilibrium convergence and predictable response to temporary supply
shocks.

------------------------------------------------------------------------

### What's Still to Come

-   Explicit buyer-seller transaction processing
-   Per-seller pricing and inventory tracking
-   Implementation of "cheapest-of-K sellers" buyer selection logic
-   Stochastic demand generation
-   Extended performance metrics and scenario comparisons

------------------------------------------------------------------------

### Changes from Original Proposal

The original proposal specified explicit buyer-seller interactions with
local seller sampling and transaction processing.

The current implementation instead uses an aggregate market-clearing
mechanism with a global price update rule to establish a stable and
testable simulation backbone before introducing transaction-level
complexity.

------------------------------------------------------------------------

## Installation Instructions

### Dependencies

-   Python 3.10
-   numpy \>= 1.26
-   pandas \>= 2.1
-   matplotlib \>= 3.8
-   pyyaml \>= 6.0

All dependencies are defined in `pyproject.toml`.

------------------------------------------------------------------------

### Step-by-Step Setup

1.  Create a conda environment:

    conda create -n oil_sim python=3.10\
    conda activate oil_sim

2.  Install the project in editable mode:

    python -m pip install -e .

3.  Verify installation:

    python -c "import oilmarket; print('Installation successful')"

------------------------------------------------------------------------

### Troubleshooting Common Issues

ModuleNotFoundError: oilmarket\
Ensure the correct environment is activated and
`python -m pip install -e .` was executed.

yaml import error\
Ensure `pyyaml` is installed via editable install.

------------------------------------------------------------------------

## Usage

Run the simulation from the project root:

python -m oilmarket

Configuration is located in:

configs/default.yaml

Running the simulation generates:

-   runs/`<timestamp>`/history.csv
-   runs/`<timestamp>`/price.png

------------------------------------------------------------------------

## Architecture Overview

### Main Components

Simulation (`simulation.py`)\
Controls time progression, applies shock state, logs simulation history.

Market (`market.py`)\
Aggregates supply and demand and updates price via exponential imbalance
adjustment.

Agents (`agents.py`)\
- Producer: Supplies output based on price and capacity\
- Consumer: Generates demand based on price elasticity

Shock (`shocks.py`)\
Encodes start time, duration, and multiplier for supply disruption.

------------------------------------------------------------------------

### Mapping to UML Design

Simulation Engine -> Simulation\
Market -> Market\
Seller Agent -> Producer\
Buyer Agent -> Consumer\
Shock Event -> Shock

------------------------------------------------------------------------

### Architectural Changes

The architecture currently implements aggregate price clearing to ensure
system stability.\
Future milestones will introduce explicit transaction-level
buyer--seller interactions and cheapest-of-K seller selection logic.
