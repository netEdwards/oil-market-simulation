from oilmarket.data import simulation
from pathlib import Path

_path = Path(__file__).parent.parent / "configs" / "default.yaml"

def test_simulation_load(path: Path):
    if path.exists():
        print("Yaml found")
    else:
        print("fix path")
        
    new_sim = simulation.SimulationConfig.from_yaml(_path)
    print(new_sim.ticks, " Sim config")
    
test_simulation_load(path=_path)