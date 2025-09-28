#!/usr/bin/env python3
"""
Player behavior modules for the FYNDR Life Simulator.
"""

from .whale_behavior import simulate_whale_behavior
from .grinder_behavior import simulate_grinder_behavior
from .casual_behavior import simulate_casual_behavior

__all__ = [
    'simulate_whale_behavior',
    'simulate_grinder_behavior', 
    'simulate_casual_behavior'
]
