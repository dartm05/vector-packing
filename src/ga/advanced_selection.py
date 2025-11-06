"""
Advanced selection operator with fitness-proportionate selection
to maintain better diversity.
"""

import random
from typing import List
from ..models import Solution
from .operators import SelectionOperator


class RouletteWheelSelection(SelectionOperator):
    """
    Fitness-proportionate selection (Roulette Wheel).
    Better for maintaining diversity than tournament selection.
    """
    
    def select(self, population: List[Solution]) -> Solution:
        """
        Select a solution based on fitness-proportionate probabilities.
        Since we're minimizing, we need to invert the fitness values.
        """
        if not population:
            raise ValueError("Cannot select from empty population")
        
        # For minimization: convert fitness to selection probability
        # Use inverse fitness (smaller fitness = higher probability)
        min_fitness = min(sol.fitness for sol in population if sol.fitness is not None)
        max_fitness = max(sol.fitness for sol in population if sol.fitness is not None)
        
        # Avoid division by zero
        if max_fitness == min_fitness:
            return random.choice(population)
        
        # Calculate selection probabilities (inverse fitness)
        # Add a small offset to avoid negative probabilities
        fitness_range = max_fitness - min_fitness
        probabilities = []
        
        for sol in population:
            # Invert so that lower fitness = higher probability
            inverted_fitness = max_fitness - sol.fitness + 0.1 * fitness_range
            probabilities.append(inverted_fitness)
        
        # Normalize probabilities
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]
        
        # Select using roulette wheel
        r = random.random()
        cumulative = 0.0
        
        for i, prob in enumerate(probabilities):
            cumulative += prob
            if r <= cumulative:
                return population[i]
        
        # Fallback (should rarely happen)
        return population[-1]


class RankSelection(SelectionOperator):
    """
    Rank-based selection to maintain diversity better.
    Reduces selection pressure compared to pure fitness selection.
    """
    
    def __init__(self, selection_pressure: float = 1.5):
        """
        Args:
            selection_pressure: Value between 1.0 and 2.0
                1.0 = uniform selection (no pressure)
                2.0 = maximum pressure (linear ranking)
        """
        self.selection_pressure = max(1.0, min(2.0, selection_pressure))
    
    def select(self, population: List[Solution]) -> Solution:
        """
        Select based on rank rather than raw fitness.
        This reduces selection pressure and maintains diversity.
        """
        if not population:
            raise ValueError("Cannot select from empty population")
        
        # Sort by fitness (best to worst for minimization)
        sorted_pop = sorted(population, key=lambda s: s.fitness)
        n = len(sorted_pop)
        
        # Calculate rank-based probabilities
        # Best solution gets highest rank (n), worst gets lowest (1)
        probabilities = []
        for rank in range(n, 0, -1):  # n, n-1, ..., 1
            prob = (2 - self.selection_pressure) / n + \
                   (2 * rank * (self.selection_pressure - 1)) / (n * (n + 1))
            probabilities.append(prob)
        
        # Select using these probabilities
        return random.choices(sorted_pop, weights=probabilities, k=1)[0]
