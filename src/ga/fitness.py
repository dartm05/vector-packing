"""
Fitness Evaluation for Vector Packing Solutions
Base class for fitness evaluation - implement your own strategy
"""

from typing import Dict
from abc import ABC, abstractmethod


class FitnessEvaluator(ABC):
    """
    Base class for evaluating the fitness of packing solutions.
    Implement the evaluate() method with your own fitness function.
    """
    
    @abstractmethod
    def evaluate(self, solution) -> float:
        """
        Calculate fitness score for a solution.
        
        Args:
            solution: Solution object to evaluate
            
        Returns:
            Fitness score
        """
        pass
    
    def compare_solutions(self, sol1, sol2) -> int:
        """
        Compare two solutions based on fitness.
        
        Args:
            sol1: First solution
            sol2: Second solution
            
        Returns:
            -1 if sol1 is better, 1 if sol2 is better, 0 if equal
        """
        fitness1 = self.evaluate(sol1)
        fitness2 = self.evaluate(sol2)
        
        if fitness1 < fitness2:
            return -1
        elif fitness1 > fitness2:
            return 1
        return 0
