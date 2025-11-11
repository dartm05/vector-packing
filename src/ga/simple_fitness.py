"""
A concrete fitness evaluator for the Vector Packing problem.
This class *implements* the abstract FitnessEvaluator.
"""

from .fitness import FitnessEvaluator  # <-- Imports the template
from ..models.solution import Solution

# Define a very large penalty for invalid solutions
INVALID_PENALTY = 1_000_000.0

#
# This class IMPLEMENTS the template
#
class SimpleFitnessEvaluator(FitnessEvaluator):
    """
    A simple fitness function that prioritizes two goals:
    1. (Primary) Minimize the number of servers used.
    2. (Secondary) Maximize the average resource utilization of used servers.
    
    This implementation assumes the GA is a *minimization* algorithm
    (it tries to find the *lowest* score).
    """

    def evaluate(self, solution: Solution) -> float:
        """
        Calculate the fitness (cost) of a solution. Lower is better.
        (This method is REQUIRED by the FitnessEvaluator template)
        """
        
        # --- 1. Validity Check (The "Must-Have") ---
        if not solution.is_valid():
            solution.fitness = INVALID_PENALTY
            return INVALID_PENALTY
        
        num_servers = solution.num_servers_used
        
        if num_servers == 0:
            solution.fitness = 0.0
            return 0.0  # An empty solution has 0 cost

        # --- 2. Primary Goal: Minimize Servers (weighted heavily) ---
        primary_cost = num_servers * 100.0

        # --- 3. Secondary Goal: Maximize Utilization ---
        # Penalize waste more significantly to encourage better packing
        utils = solution.average_utilization
        avg_util = (utils['cpu'] + utils['ram'] + utils['storage']) / 3.0
        
        # Convert utilization percentage to a cost (100% util = 0 cost, 0% util = 100 cost)
        waste_cost = (100.0 - avg_util)

        # --- 4. Balance Penalty: Penalize unbalanced resource usage ---
        # Encourage balanced usage of CPU, RAM, and storage
        util_variance = ((utils['cpu'] - avg_util)**2 + 
                        (utils['ram'] - avg_util)**2 + 
                        (utils['storage'] - avg_util)**2) / 3.0
        balance_penalty = util_variance * 0.1

        total_cost = primary_cost + waste_cost + balance_penalty
        
        solution.fitness = total_cost
        return total_cost
        
    def compare_solutions(self, sol1: Solution, sol2: Solution) -> int:
        """
        Compare two solutions (lower fitness is better).
        (This overrides the base method for efficiency)
        """
        # Ensure fitness is calculated if it hasn't been
        if sol1.fitness is None:
            self.evaluate(sol1)
        if sol2.fitness is None:
            self.evaluate(sol2)
            
        if sol1.fitness < sol2.fitness:
            return -1  # sol1 is better
        elif sol1.fitness > sol2.fitness:
            return 1   # sol2 is better
        return 0       # they are equal