#!/usr/bin/env python3
"""
Generate updated results using the simplified GA engine.
This will benchmark all scenarios and create updated visualization data.
"""

import time
import json
from src.utils.data_generator import DataGenerator
from src.ga.simple_engine import run_simple_ga, create_initial_population, calculate_fitness
from src.woc import CrowdAnalyzer, CrowdBuilder

def benchmark_scenario(scenario_name, seed=42):
    """Run both GA and WoC on a scenario and collect results."""

    print(f"\n{'='*70}")
    print(f"Benchmarking {scenario_name.upper()} scenario")
    print(f"{'='*70}")

    # Generate problem
    scenario = DataGenerator.generate_scenario(scenario_name, seed=seed)
    vms = scenario['vms']
    server_template = scenario['server_template']

    print(f"Problem: {len(vms)} VMs")
    print(f"Server: {server_template.max_cpu_cores} cores, "
          f"{server_template.max_ram_gb} GB RAM, "
          f"{server_template.max_storage_gb} GB storage")

    results = {
        'scenario': scenario_name,
        'num_vms': len(vms),
        'server_capacity': {
            'cpu': server_template.max_cpu_cores,
            'ram': server_template.max_ram_gb,
            'storage': server_template.max_storage_gb
        }
    }

    # Benchmark GA
    print(f"\n1. Running GA (random initialization)...")
    ga_start = time.time()

    best_ga = run_simple_ga(
        vms=vms,
        server_template=server_template,
        population_size=50,
        generations=100,
        elitism_count=2,
        mutation_rate=0.5,
        initial_quality="random"  # Show improvement
    )

    ga_time = time.time() - ga_start

    ga_utils = best_ga.average_utilization
    results['ga'] = {
        'time_seconds': round(ga_time, 2),
        'servers_used': best_ga.num_servers_used,
        'fitness': round(best_ga.fitness, 2),
        'valid': best_ga.is_valid(),
        'utilization': {
            'cpu': round(ga_utils['cpu'], 1),
            'ram': round(ga_utils['ram'], 1),
            'storage': round(ga_utils['storage'], 1)
        }
    }

    print(f"   GA completed in {ga_time:.2f}s")
    print(f"   Result: {best_ga.num_servers_used} servers, fitness={best_ga.fitness:.2f}")

    # Benchmark WoC
    print(f"\n2. Running WoC...")
    woc_start = time.time()

    # Create diverse population for WoC
    population = create_initial_population(vms, server_template, 30, quality="mixed")
    for sol in population:
        calculate_fitness(sol)
    population.append(best_ga)

    # Analyze with WoC
    analyzer = CrowdAnalyzer()
    analyzer.analyze_solutions(population, top_k=20)

    # Build WoC solutions
    builder = CrowdBuilder(analyzer)
    woc_solutions = builder.build_multiple_solutions(
        vms, server_template, num_solutions=20, affinity_weight=0.7
    )

    for sol in woc_solutions:
        calculate_fitness(sol)

    woc_solutions.sort(key=lambda s: s.fitness)
    best_woc = woc_solutions[0]

    woc_time = time.time() - woc_start

    woc_utils = best_woc.average_utilization
    results['woc'] = {
        'time_seconds': round(woc_time, 2),
        'servers_used': best_woc.num_servers_used,
        'fitness': round(best_woc.fitness, 2),
        'valid': best_woc.is_valid(),
        'utilization': {
            'cpu': round(woc_utils['cpu'], 1),
            'ram': round(woc_utils['ram'], 1),
            'storage': round(woc_utils['storage'], 1)
        },
        'speedup': round(ga_time / woc_time, 1) if woc_time > 0 else 0
    }

    print(f"   WoC completed in {woc_time:.2f}s")
    print(f"   Result: {best_woc.num_servers_used} servers, fitness={best_woc.fitness:.2f}")
    print(f"   Speedup: {results['woc']['speedup']}×")

    return results


def main():
    """Run benchmarks and save results."""

    print("="*70)
    print("GENERATING UPDATED RESULTS WITH SIMPLIFIED GA")
    print("="*70)
    print("\nThis will run GA and WoC on all scenarios and save updated data")
    print("for visualization generation.\n")

    scenarios = ['small', 'medium', 'large', 'extra_large']
    all_results = []

    for scenario in scenarios:
        results = benchmark_scenario(scenario)
        all_results.append(results)

        # Print summary
        print(f"\n{'='*70}")
        print(f"Summary for {scenario.upper()}")
        print(f"{'='*70}")
        print(f"GA:  {results['ga']['servers_used']} servers, "
              f"fitness={results['ga']['fitness']}, "
              f"time={results['ga']['time_seconds']}s")
        print(f"WoC: {results['woc']['servers_used']} servers, "
              f"fitness={results['woc']['fitness']}, "
              f"time={results['woc']['time_seconds']}s "
              f"(speedup: {results['woc']['speedup']}×)")

    # Save results
    output_file = 'updated_benchmark_results.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*70}")
    print("RESULTS SAVED")
    print(f"{'='*70}")
    print(f"Results saved to: {output_file}")
    print("\nYou can now use these results to update visualizations:")
    print("  1. Run: python update_visualizations.py")
    print("  2. Or manually update the HTML files with the new data")

    # Print formatted table for easy copy-paste
    print(f"\n{'='*70}")
    print("RESULTS TABLE (for presentations)")
    print(f"{'='*70}")
    print(f"{'Scenario':<12} {'VMs':<6} {'Method':<8} {'Time':<8} {'Servers':<8} {'Fitness':<10} {'Speedup'}")
    print("-"*70)

    for result in all_results:
        scenario = result['scenario'].capitalize()
        vms = result['num_vms']

        # GA row
        print(f"{scenario:<12} {vms:<6} {'GA':<8} "
              f"{result['ga']['time_seconds']:<8.2f} "
              f"{result['ga']['servers_used']:<8} "
              f"{result['ga']['fitness']:<10.2f} {'':>8}")

        # WoC row
        print(f"{'':>12} {'':>6} {'WoC':<8} "
              f"{result['woc']['time_seconds']:<8.2f} "
              f"{result['woc']['servers_used']:<8} "
              f"{result['woc']['fitness']:<10.2f} "
              f"{result['woc']['speedup']:>7.1f}×")
        print("-"*70)

    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    main()
