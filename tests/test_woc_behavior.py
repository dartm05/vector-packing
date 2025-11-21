"""
Test to understand WoC behavior and why it doesn't improve on GA.
"""

from src.utils.data_generator import DataGenerator
from src.ga.simple_engine import run_simple_ga, create_initial_population, calculate_fitness
from src.woc import CrowdAnalyzer, CrowdBuilder

def test_woc():
    """Test WoC behavior."""

    print("="*80)
    print("Testing WoC Behavior")
    print("="*80)

    # Generate problem
    scenario = DataGenerator.generate_scenario('small', seed=42)
    vms = scenario['vms']
    server_template = scenario['server_template']

    print(f"\nProblem: {len(vms)} VMs\n")

    # Run GA with random initialization
    print("Step 1: Running GA with random initialization...")
    print("-"*80)
    best_ga = run_simple_ga(
        vms=vms,
        server_template=server_template,
        population_size=30,
        generations=50,
        elitism_count=2,
        mutation_rate=0.5,
        initial_quality="random"
    )

    print("\n" + "="*80)
    print(f"GA Result: {best_ga.num_servers_used} servers, fitness={best_ga.fitness:.2f}")
    print("="*80)

    # Create population for WoC analysis
    print("\nStep 2: Creating diverse population for WoC to analyze...")
    print("-"*80)

    # Create a diverse population with different qualities
    population = []

    # Add some random solutions
    random_pop = create_initial_population(vms, server_template, 10, quality="random")
    for sol in random_pop:
        calculate_fitness(sol)
    population.extend(random_pop)

    # Add some good solutions
    good_pop = create_initial_population(vms, server_template, 10, quality="good")
    for sol in good_pop:
        calculate_fitness(sol)
    population.extend(good_pop)

    # Add the best GA solution
    population.append(best_ga)

    # Sort and show diversity
    population.sort(key=lambda s: s.fitness)
    print(f"Population size: {len(population)}")
    print(f"Best in population: {population[0].num_servers_used} servers, fitness={population[0].fitness:.2f}")
    print(f"Worst in population: {population[-1].num_servers_used} servers, fitness={population[-1].fitness:.2f}")
    print(f"Average servers: {sum(s.num_servers_used for s in population) / len(population):.1f}")

    # Analyze with WoC
    print("\nStep 3: Analyzing patterns with WoC...")
    print("-"*80)

    analyzer = CrowdAnalyzer()
    analyzer.analyze_solutions(population, top_k=15)

    print(f"VM pairs analyzed: {len(analyzer.co_occurrence_matrix)}")

    # Show some patterns
    if analyzer.co_occurrence_matrix:
        print("\nTop 5 VM affinity patterns:")
        sorted_patterns = sorted(
            analyzer.co_occurrence_matrix.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for (vm1, vm2), count in sorted_patterns:
            affinity = analyzer.get_affinity_score(vm1, vm2)
            print(f"  VM {vm1} + VM {vm2}: co-occurrence={count}, affinity={affinity:.2f}")

    # Build solutions with WoC
    print("\nStep 4: Building solutions with WoC...")
    print("-"*80)

    builder = CrowdBuilder(analyzer)

    # Try different affinity weights
    print("\nTesting different affinity weights:")
    for weight in [0.3, 0.5, 0.7, 0.9]:
        woc_solutions = builder.build_multiple_solutions(
            vms, server_template, num_solutions=5, affinity_weight=weight
        )

        for sol in woc_solutions:
            calculate_fitness(sol)

        woc_solutions.sort(key=lambda s: s.fitness)
        best_woc = woc_solutions[0]

        print(f"  Weight {weight:.1f}: Best = {best_woc.num_servers_used} servers, "
              f"fitness={best_woc.fitness:.2f}")

    # Final comparison
    print("\n" + "="*80)
    print("FINAL COMPARISON:")
    print("="*80)
    print(f"GA Solution:  {best_ga.num_servers_used} servers, fitness={best_ga.fitness:.2f}")

    # Get best WoC solution overall
    all_woc_solutions = builder.build_multiple_solutions(
        vms, server_template, num_solutions=20, affinity_weight=0.7
    )
    for sol in all_woc_solutions:
        calculate_fitness(sol)
    all_woc_solutions.sort(key=lambda s: s.fitness)
    best_woc = all_woc_solutions[0]

    print(f"WoC Solution: {best_woc.num_servers_used} servers, fitness={best_woc.fitness:.2f}")

    if best_woc.fitness < best_ga.fitness:
        improvement = ((best_ga.fitness - best_woc.fitness) / best_ga.fitness) * 100
        print(f"\n✅ WoC improved by {improvement:.1f}%!")
    elif best_woc.fitness == best_ga.fitness:
        print(f"\n🔵 WoC matched GA (both found same solution)")
    else:
        degradation = ((best_woc.fitness - best_ga.fitness) / best_ga.fitness) * 100
        print(f"\n❌ WoC is {degradation:.1f}% worse than GA")

    print("="*80)

if __name__ == "__main__":
    test_woc()
