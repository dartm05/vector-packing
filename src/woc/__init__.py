"""
Wisdom of Crowds (WoC) components

This module implements crowd intelligence algorithms that analyze patterns
in successful solutions and use them to generate improved solutions.

Key Components:
- CrowdAnalyzer: Analyzes solution populations to discover VM co-location patterns
- CrowdBuilder: Constructs new solutions using discovered patterns
"""

from .crowd_analyzer import CrowdAnalyzer
from .crowd_builder import CrowdBuilder

__all__ = ['CrowdAnalyzer', 'CrowdBuilder']
