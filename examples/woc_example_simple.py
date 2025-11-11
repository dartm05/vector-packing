"""
Simple example of using Wisdom of Crowds (WoC) with Genetic Algorithm
This version does not require matplotlib or GUI dependencies.

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
    
    # Step 2: Run GA to get initial solutions
    print("\n[2] Running Genetic Algorithm...")
    print("  (This will generate a population of solutions)")
    
    # Run a short GA to get diverse solutions
    best_ga_solution = run_ga(
        vms=vms,
        server_template=server_template,
        population_size=30,
        generations=50,
        mutation_rate=0.3
    )
    
    print(f"\n  GA Best Solution:")
    print(f"    - Servers used: {best_ga_solution.num_servers_used}")
    print(f"    - Fitness: {best_ga_solution.fitness:.2f}")
    print(f"    - Valid: {best_ga_solution.is_valid()}")
    
    # Step 3: Analyze patterns with WoC
    print("\n[3] Analyzing VM affinity patterns with Wisdom of Crowds...")
    analyzer = CrowdAnalyzer()
    
    # We need to get the population from GA
    # For this example, we'll create a few solutions
    print("  - Creating sample population...")
    sample_solutions = []
    for i in range(10):
        import random
        random.seed(42 + i)
        shuffled_vms = list(vms)
        random.shuffle(shuffled_vms)
        
        # Create solution using first-fit
        solution = Solution()
        servers = []
        
        for vm in shuffled_vms:
            placed = False
            for server in servers:
                if server.can_fit(vm):
                    server.add_vm(vm)
                    placed = True
                    break
            
            if not placed:
                new_server = Server(
                    id=len(servers),
                    max_cpu_cores=server_template.max_cpu_cores,
                    max_ram_gb=server_template.max_ram_gb,
                    max_storage_gb=server_template.max_storage_gb,
                    name=f"Server-{len(servers)}"
                )
                new_server.add_vm(vm)
                servers.append(new_server)
        
        solution.servers = servers
        sample_solutions.append(solution)
    
    # Analyze the population
    analyzer.analyze_solutions(sample_solutions)
    
    print(f"\n  Analysis Results:")
    print(f"    - Affinity matrix computed: {len(analyzer.affinity_matrix)} x {len(analyzer.affinity_matrix)}")
    print(f"    - Number of VMs analyzed: {len(vms)}")
    
    # Show some affinity examples
    print(f"\n  Sample VM Affinities (top pairs that work well together):")
    affinity_pairs = []
    for vm1_id in analyzer.affinity_matrix:
        for vm2_id, score in analyzer.affinity_matrix[vm1_id].items():
            if vm1_id < vm2_id and score > 0.5:  # Only show strong affinities
                affinity_pairs.append((vm1_id, vm2_id, score))
    
    affinity_pairs.sort(key=lambda x: x[2], reverse=True)
    for i, (vm1_id, vm2_id, score) in enumerate(affinity_pairs[:5]):
        print(f"    {i+1}. VM {vm1_id} + VM {vm2_id}: {score:.3f}")
    
    # Step 4: Use WoC to build new solutions
    print("\n[4] Building new solutions using WoC patterns...")
    builder = CrowdBuilder(analyzer)
    
    woc_solutions = []
    for i in range(5):
        solution = builder.build_solution(vms, server_template)
        woc_solutions.append(solution)
    
    # Evaluate WoC solutions
    evaluator = SimpleFitnessEvaluator()
    best_woc_solution = None
    best_woc_fitness = float('inf')
    
    for sol in woc_solutions:
        evaluator.evaluate(sol)
        if sol.fitness < best_woc_fitness:
            best_woc_fitness = sol.fitness
            best_woc_solution = sol
    
    print(f"\n  WoC Best Solution:")
    print(f"    - Servers used: {best_woc_solution.num_servers_used}")
    print(f"    - Fitness: {best_woc_solution.fitness:.2f}")
    print(f"    - Valid: {best_woc_solution.is_valid()}")
    
    # Step 5: Compare results
    print("\n[5] Comparison: GA vs WoC")
    print("  " + "=" * 60)
    print(f"  {'Metric':<30} {'GA':<15} {'WoC':<15}")
    print("  " + "-" * 60)
    print(f"  {'Servers Used':<30} {best_ga_solution.num_servers_used:<15} {best_woc_solution.num_servers_used:<15}")
    print(f"  {'Fitness Score':<30} {best_ga_solution.fitness:<15.2f} {best_woc_solution.fitness:<15.2f}")
    print(f"  {'Valid Solution':<30} {str(best_ga_solution.is_valid()):<15} {str(best_woc_solution.is_valid()):<15}")
    
    ga_utils = best_ga_solution.average_utilization
    woc_utils = best_woc_solution.average_utilization
    
    print(f"  {'CPU Utilization (%)':<30} {ga_utils['cpu']:<15.2f} {woc_utils['cpu']:<15.2f}")
    print(f"  {'RAM Utilization (%)':<30} {ga_utils['ram']:<15.2f} {woc_utils['ram']:<15.2f}")
    print(f"  {'Storage Utilization (%)':<30} {ga_utils['storage']:<15.2f} {woc_utils['storage']:<15.2f}")
    print("  " + "=" * 60)
    
    # Determine winner
    if best_woc_solution.fitness < best_ga_solution.fitness:
        print("\n  🎉 WoC found a better solution!")
        improvement = ((best_ga_solution.fitness - best_woc_solution.fitness) / best_ga_solution.fitness) * 100
        print(f"  Improvement: {improvement:.2f}%")
    elif best_woc_solution.fitness > best_ga_solution.fitness:
        print("\n  GA solution is better.")
    else:
        print("\n  Both approaches found equivalent solutions.")
    
    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


def demonstrate_woc_with_ga_population():
    """
    A more advanced example showing how to use WoC during GA evolution.
    """
    print("\n" + "=" * 70)
    print("Advanced Example: WoC Integration During GA Evolution")
    print("=" * 70)
    
    # Generate problem
    print("\n[1] Generating problem...")
    scenario = DataGenerator.generate_scenario('small', seed=42)
    vms = scenario['vms']
    server_template = scenario['server_template']
    
    print(f"  - VMs: {len(vms)}")
    
    # Initialize WoC components
    print("\n[2] Initializing WoC components...")
    analyzer = CrowdAnalyzer()
    
    # Run GA with intermediate WoC analysis
    print("\n[3] Running GA with WoC integration...")
    
    # First phase: Pure GA
    print("  Phase 1: Running GA for 30 generations...")
    from src.ga.engine import create_initial_population
    
    population = create_initial_population(vms, server_template, size=30)
    evaluator = SimpleFitnessEvaluator()
    
    # Evaluate initial population
    for sol in population:
        evaluator.evaluate(sol)
    
    population.sort(key=lambda s: s.fitness)
    print(f"    Best fitness: {population[0].fitness:.2f}")
    
    # Analyze patterns from GA population
    print("\n  Phase 2: Analyzing patterns from GA solutions...")
    analyzer.analyze_solutions(population[:10])  # Analyze top 10
    
    # Generate WoC-based solutions
    print("  Phase 3: Generating WoC-enhanced solutions...")
    builder = CrowdBuilder(analyzer)
    
    woc_solutions = []
    for i in range(5):
        solution = builder.build_solution(vms, server_template)
        evaluator.evaluate(solution)
        woc_solutions.append(solution)
    
    # Compare best WoC with best GA
    best_woc = min(woc_solutions, key=lambda s: s.fitness)
    best_ga = population[0]
    
    print(f"\n  Results:")
    print(f"    GA best:  {best_ga.fitness:.2f} ({best_ga.num_servers_used} servers)")
    print(f"    WoC best: {best_woc.fitness:.2f} ({best_woc.num_servers_used} servers)")
    
    if best_woc.fitness < best_ga.fitness:
        print(f"    ✅ WoC improved the solution!")
    
    print("\n" + "=" * 70)


def show_affinity_details(analyzer, vms, top_n=10):
    """
    Print detailed affinity information.
    """
    print("\n" + "=" * 70)
    print("VM Affinity Analysis Details")
    print("=" * 70)
    
    # Find VMs with highest total affinity
    vm_total_affinity = {}
    for vm1_id in analyzer.affinity_matrix:
        total = sum(analyzer.affinity_matrix[vm1_id].values())
        vm_total_affinity[vm1_id] = total
    
    sorted_vms = sorted(vm_total_affinity.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\nTop {top_n} VMs by total affinity:")
    for i, (vm_id, total_affinity) in enumerate(sorted_vms[:top_n]):
        vm = next((v for v in vms if v.id == vm_id), None)
        if vm:
            print(f"  {i+1}. VM {vm_id}: Affinity={total_affinity:.2f}")
            print(f"     Resources: {vm.cpu_cores} cores, {vm.ram_gb} GB RAM, {vm.storage_gb} GB storage")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("WoC (Wisdom of Crowds) Example - Simple Version")
    print("No matplotlib or GUI dependencies required")
    print("=" * 70)
    
    # Run basic demo
    demonstrate_woc_integration()
    
    # Ask if user wants to run advanced demo
    print("\n\nWould you like to run the advanced demo? (y/n): ", end="")
    try:
        response = input().strip().lower()
        if response == 'y':
            demonstrate_woc_with_ga_population()
    except (EOFError, KeyboardInterrupt):
        print("\nSkipping advanced demo.")
    
    print("\n✅ All examples completed!")
