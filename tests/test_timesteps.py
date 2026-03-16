from pathlib import Path

import pytest

from oilmarket.data.simulation import SimulationConfig
from oilmarket.data.state import TimestepState
from oilmarket.market import Market
from oilmarket.simulation import Simulation

cfg_path = Path(__file__).parent / "test_configs" / "default.yaml"


def test_market_timestep_run():
    #setup simulation class.
    #can use test_config or default yaml
    #validate that one timestep run in Market returns a TimestepState
    config = SimulationConfig.from_yaml(path=cfg_path)
    market = Market(config)
    
    result = market.run_market_timestep(0)
    assert result
    assert type(result) == TimestepState
    print(
        "======================================\n"
        f"--TimestepState--\n",
        f"Timestep: {result.timestep}\n",
        f"Buyers: {len(result.buyers)}\n",
        f"Sellers: {len(result.sellers)}\n",
        f"Transactins: {len(result.transactions)}\n",
        f"Total Units Sold: {result.total_units_sold}\n",
        f"Total unmet demand: {result.total_unmet_demand}\n",
        f"Average Price: {result.average_price}\n"
        "======================================\n\n\n"
    )
    for t in result.transactions:
        print(
            "====Transactions that Occured====\n",
            f"Timestep: {t.timestep}\n",
            f"Seller: {t.seller_id}\n",
            f"Buyer: {t.buyer_id}\n",
            f"Units Sold: {t.units_sold}\n",
            f"Unit Price: {t.unit_price}\n",
            f"Buyer WTP: {t.buyer_wtp}\n",
            f"Remaining demand: {t.remaining_demand}\n",
            f"Total Price: {t.total_price}\n",
            
            f"Transaction ID: {t.id}\n\n\n"
        )
    
    