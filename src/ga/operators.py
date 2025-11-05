"""
Genetic Algorithm Operators: Base classes for Selection, Crossover, and Mutation
Implement these abstract classes with your own strategies
"""

from typing import List, Tuple
from abc import ABC, abstractmethod


class SelectionOperator(ABC):
    """Base class for selection operators"""
    
    @abstractmethod
    def select(self, population: List, fitness_scores: List[float], num_parents: int) -> List:
        """
        Select parents from population.
        
        Args:
            population: List of solutions
            fitness_scores: Fitness scores for each solution
            num_parents: Number of parents to select
            
        Returns:
            List of selected parent solutions
        """
        pass


class CrossoverOperator(ABC):
    """Base class for crossover operators"""
    
    @abstractmethod
    def crossover(self, parent1, parent2) -> Tuple:
        """
        Perform crossover between two parents.
        
        Args:
            parent1: First parent solution
            parent2: Second parent solution
            
        Returns:
            Tuple of (child1, child2) offspring solutions
        """
        pass


class MutationOperator(ABC):
    """Base class for mutation operators"""
    
    @abstractmethod
    def mutate(self, solution):
        """
        Mutate a solution.
        
        Args:
            solution: Solution to mutate
            
        Returns:
            Mutated solution
        """
        pass
