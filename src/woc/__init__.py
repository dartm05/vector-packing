# Create population for WOC to learn from
ga_population = create_initial_population(vms, server_template, args.population)"""
Wisdom of Crowds (WoC) Implementation

Analyzes patterns from successful GA solutions and builds
new solutions using collective intelligence.
"""

from .affinity_matrix import AffinityMatrix
from .solution_builder import AffinityBasedBuilder
from .engine import WisdomOfCrowdsEngine, run_woc

__all__ = [
    'AffinityMatrix',
    'AffinityBasedBuilder', 
    'WisdomOfCrowdsEngine',
    'run_woc'
]
