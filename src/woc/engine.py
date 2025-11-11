"""
Wisdom of Crowds Engine

This module orchestrates the WOC approach:
1. Learn patterns from successful GA solutions
2. Build new solutions using multiple crowd strategies
3. Return the best solution found
"""

from typing import List, Optional
from ..models import VirtualMachine, Server, Solution
from ..ga.simple_fitness import SimpleFitnessEvaluator
from .affinity_matrix import AffinityMatrix
from .solution_builder import AffinityBasedBuilder


class WisdomOfCrowdsEngine:
    """
    Main WOC engine that learns from a population of solutions
    and generates new solutions based on collective patterns.
    """
    
    def __init__(self, num_vms: int):
        """
        Initialize the WOC engine.
        
        Args:
            num_vms: Total number of VMs in the problem
        """
        self.num_vms = num_vms
        self.affinity_matrix = AffinityMatrix(num_vms)
        self.evaluator = SimpleFitnessEvaluator()
    
    def learn_from_population(self, population: List[Solution], 
                             top_n: int = 20,
                             weight_by_fitness: bool = True):
        """
        Learn patterns from a population of solutions.
        Focuses on the best solutions.
        
        Args:
            population: List of solutions to learn from
            top_n: Number of top solutions to analyze
            weight_by_fitness: If True, better solutions have more influence
        """
        # Sort by fitness (lower is better in our case)
        sorted_pop = sorted(population, key=lambda s: s.fitness if s.fitness else float('inf'))
        
        # Take top N solutions
        top_solutions = sorted_pop[:min(top_n, len(sorted_pop))]
        
        # Learn from each solution
        for i, solution in enumerate(top_solutions):
            if weight_by_fitness:
                # Better solutions (lower rank) get higher weight
                weight = (len(top_solutions) - i) / len(top_solutions)
            else:
                weight = 1.0
            
            self.affinity_matrix.update(solution, weight)
        
        print(f"  WOC learned from {len(top_solutions)} solutions")
    
    def generate_solutions(self, vms: List[VirtualMachine],
                          server_template: Server,
                          num_solutions: int = 10) -> List[Solution]:
        """
        Generate multiple solutions using different crowd strategies.
        
        Args:
            vms: List of VMs to place
            server_template: Server capacity template
            num_solutions: Number of solutions to generate
            
        Returns:
            List of generated solutions
        """
        builder = AffinityBasedBuilder(self.affinity_matrix)
        solutions = []
        
        strategies = ['greedy', 'group_based', 'iterative']
        
        for i in range(num_solutions):
            # Rotate through strategies
            strategy = strategies[i % len(strategies)]
            
            try:
                solution = builder.build_solution(vms, server_template, strategy)
                
                # Evaluate the solution
                self.evaluator.evaluate(solution)
                
                solutions.append(solution)
            except Exception as e:
                print(f"  Warning: Failed to build solution with {strategy}: {e}")
        
        return solutions
    
    def get_best_solution(self, solutions: List[Solution]) -> Optional[Solution]:
        """
        Get the best solution from a list.
        
        Args:
            solutions: List of solutions
            
        Returns:
            Best solution, or None if list is empty
        """
        if not solutions:
            return None
        
        # Ensure all are evaluated
        for sol in solutions:
            if sol.fitness is None:
                self.evaluator.evaluate(sol)
        
        # Return best (lowest fitness)
        return min(solutions, key=lambda s: s.fitness)
    
    def get_affinity_statistics(self) -> dict:
        """
        Get statistics about learned affinities.
        
        Returns:
            Dictionary with affinity statistics
        """
        return {
            'solutions_analyzed': self.affinity_matrix.solution_count,
            'num_vms': self.num_vms,
            'affinity_groups': len(self.affinity_matrix.get_affinity_groups()),
        }


def run_woc(vms: List[VirtualMachine],
           server_template: Server,
           ga_population: List[Solution],
           top_n: int = 20,
           num_solutions: int = 30) -> Solution:
    """
    Run the Wisdom of Crowds approach.
    
    Args:
        vms: List of VMs to place
        server_template: Server capacity template
        ga_population: Population from GA to learn from
        top_n: Number of top GA solutions to learn from
        num_solutions: Number of WOC solutions to generate
        
    Returns:
        Best solution found by WOC
    """
    print("\n--- 🧠 Starting Wisdom of Crowds ---")
    print(f"Learning from top {top_n} GA solutions...")
    
    # Initialize WOC engine
    woc = WisdomOfCrowdsEngine(num_vms=len(vms))
    
    # Learn from GA population
    woc.learn_from_population(ga_population, top_n=top_n, weight_by_fitness=True)
    
    # Get statistics
    stats = woc.get_affinity_statistics()
    print(f"  Solutions analyzed: {stats['solutions_analyzed']}")
    print(f"  Affinity groups found: {stats['affinity_groups']}")
    
    # Generate new solutions using crowd wisdom
    print(f"\nGenerating {num_solutions} solutions using crowd wisdom...")
    woc_solutions = woc.generate_solutions(vms, server_template, num_solutions)
    
    print(f"  Generated {len(woc_solutions)} valid solutions")
    
    # Find best WOC solution
    best_woc = woc.get_best_solution(woc_solutions)
    
    if best_woc:
        print(f"\nBest WOC solution:")
        print(f"  Servers: {best_woc.num_servers_used}")
        print(f"  Fitness: {best_woc.fitness:.2f}")
        print(f"  Valid: {best_woc.is_valid()}")
        
        utils = best_woc.average_utilization
        print(f"  Avg utilization: CPU={utils['cpu']:.1f}%, "
              f"RAM={utils['ram']:.1f}%, Storage={utils['storage']:.1f}%")
    
    print("--- 🏁 WOC Finished ---\n")
    
    return best_woc
