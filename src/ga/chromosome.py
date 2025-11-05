"""
Chromosome representation (alias for Solution with GA-specific methods)
"""

# In this implementation, Solution serves as the chromosome
# This module can be extended with GA-specific chromosome operations
from ..models import Solution

# Alias for clarity in GA context
Chromosome = Solution

__all__ = ['Chromosome']
