from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Shock:
    start_tick: int
    duration: int
    multiplier: float
    
    def is_active(self, tick: int) -> bool:
        return self.start_tick <= tick < (self.start_tick +self.duration)
    