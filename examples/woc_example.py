"""
Example of using Wisdom of Crowds (WoC) with Genetic Algorithm

This script demonstrates how to integrate CrowdAnalyzer and CrowdBuilder
into the GA optimization process.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import VirtualMachine, Server, Solution
from src.ga.engine import run_ga
from src.woc import CrowdAnalyzer, CrowdBuilder
from src.utils.data_generator import DataGenerator
from src.ga.simple_fitness import SimpleFitnessEvaluator


def demonstrate_woc_integration():
    """
    Demonstrates how to use WoC components with the GA.
    
    Process:
    1. Run GA to get a population of solutions
    2. Use CrowdAnalyzer to learn VM affinity patterns
    3. Use CrowdBuilder to generate new solutions based on patterns
    4. Compare results
    """
    print("=" * 70)
    print("Wisdom of Crowds (WoC) Integration Example")
    print("=" * 70)
    
    # Step 1: Generate test data
    print("\n[1] Generating test data...")
    vms = DataGenerator.generate_vms(num_vms=30, seed=42)
    server_template = DataGenerator.create_server_template()
    
    print(f"  - Generated {len(vms)} VMs")
    print(f"  - Server capacity: {server_template.max_cpu_cores} cores, "
          f"{server_template.max_ram_gb} GB RAM, {server_template.max_storage_gb} GB storage")
    
    # Step 2: Run GA to get initial population
    print("\n[2] Running Genetic Algorithm...")
    best_solution = run_ga(
        vms=vms,
        server_template=server_template,
        population_size=50,
        generations=20
    )
    
    print(f"  - Best GA solution uses {best_solution.num_servers_used} servers")
    print(f"  - Fitness: {best_solution.fitness:.2f}")
    
    # Generate a population to analyze (simulate multiple GA runs)
    print("  - Generating additional solutions for analysis...")
    from src.ga.engine import create_initial_population
    fitness_evaluator = SimpleFitnessEvaluator()
    population = create_initial_population(vms, server_template, 30)
    for sol in population:
        fitness_evaluator.evaluate(sol)
    population.append(best_solution)  # Include the best GA solution
    
    # Step 3: Analyze the population with CrowdAnalyzer
    print("\n[3] Analyzing population with CrowdAnalyzer...")
    analyzer = CrowdAnalyzer()
    analyzer.analyze_solutions(population, top_k=20)  # Analyze top 20 solutions
    
    stats = analyzer.get_statistics()
    print(f"  - Solutions analyzed: {stats['solutions_analyzed']}")
    print(f"  - Unique VMs found: {stats['unique_vms']}")
    print(f"  - VM pairs discovered: {stats['vm_pairs_found']}")
    print(f"  - Avg co-occurrence: {stats['avg_co_occurrence']:.2f}")
    
    # Step 4: Build new solutions using CrowdBuilder
    print("\n[4] Building new solutions with CrowdBuilder...")
    builder = CrowdBuilder(analyzer)
    
    # Build 10 new solutions with different affinity weights
    crowd_solutions = builder.build_multiple_solutions(
        vms=vms,
        server_template=server_template,
        num_solutions=10,
        affinity_weight=0.7
    )
    
    # Evaluate the crowd-built solutions
    for solution in crowd_solutions:
        fitness_evaluator.evaluate(solution)
    
    # Find the best crowd solution
    best_crowd_solution = min(crowd_solutions, key=lambda s: s.fitness)
    
    print(f"  - Generated {len(crowd_solutions)} crowd-based solutions")
    print(f"  - Best crowd solution uses {best_crowd_solution.num_servers_used} servers")
    print(f"  - Fitness: {best_crowd_solution.fitness:.2f}")
    
    # Step 5: Compare results
    print("\n[5] Comparison:")
    print(f"  GA Best:    {best_solution.num_servers_used} servers, fitness = {best_solution.fitness:.2f}")
    print(f"  WoC Best:   {best_crowd_solution.num_servers_used} servers, fitness = {best_crowd_solution.fitness:.2f}")
    
    if best_crowd_solution.fitness < best_solution.fitness:
        improvement = ((best_solution.fitness - best_crowd_solution.fitness) / best_solution.fitness) * 100
        print(f"  🎉 WoC improved by {improvement:.2f}%!")
    elif best_crowd_solution.fitness == best_solution.fitness:
        print(f"  ⚖️  Both approaches achieved the same fitness!")
    else:
        print(f"  📊 GA still ahead, but WoC provides diverse alternatives.")
    
    # Step 6: Show some affinity patterns
    print("\n[6] Sample VM Affinity Patterns:")
    if len(vms) >= 5:
        for i in range(min(3, len(vms))):
            vm = vms[i]
            companions = analyzer.get_best_companions(vm.id, [v.id for v in vms], top_n=3)
            if companions:
                print(f"  VM {vm.id} works well with: {companions}")
                for comp_id in companions[:2]:
                    score = analyzer.get_affinity_score(vm.id, comp_id)
                    print(f"    - VM {comp_id}: affinity score = {score:.3f}")
    
    print("\n" + "=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


def run_ga_with_woc_injection(vms, server_template, inject_every=5):
    """
    Advanced integration: Periodically inject WoC solutions into GA population.
    
    This is a conceptual example showing how WoC could be integrated
    during the GA run (not fully implemented in the base engine).
    """
    print("\n[Advanced] GA with periodic WoC injection")
    print("This would inject crowd-based solutions every N generations")
    print("to maintain diversity and leverage learned patterns.")
    print("(Implementation would require modifying the GA engine)")


if __name__ == "__main__":
    demonstrate_woc_integration()
