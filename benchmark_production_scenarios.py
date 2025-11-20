#!/usr/bin/env python3
"""
Benchmark production scenarios with 500, 750, and 1000 VMs.

This script runs comprehensive benchmarks on production-scale scenarios
and generates detailed results for analysis.
"""

import time
import json
from pathlib import Path
from src.utils.data_generator import DataGenerator
from src.ga.simple_engine import run_simple_ga, create_initial_population, calculate_fitness
from src.woc import CrowdAnalyzer, CrowdBuilder


def benchmark_production_scenario(scenario_name, seed=42):
    """Run both GA and WoC on a production scenario and collect results.

    Args:
        scenario_name: 'production', 'production_medium', or 'production_large'
        seed: Random seed for reproducibility
    """

    print(f"\n{'='*80}")
    print(f"Benchmarking {scenario_name.upper().replace('_', ' ')} scenario")
    print(f"{'='*80}")

    # Load problem data from Azure dataset
    scenario = DataGenerator.load_azure_scenario(scenario_name, seed=seed)
    metadata = scenario.get('metadata', {})

    vms = scenario['vms']
    server_template = scenario['server_template']

    print(f"Data source: Azure Packing Trace 2020")
    print(f"Original pool: {metadata.get('original_pool_size', 'N/A'):,} VMs")
    print(f"Sampled VMs: {len(vms)}")
    print(f"Server capacity: {server_template.max_cpu_cores} cores, "
          f"{server_template.max_ram_gb} GB RAM, "
          f"{server_template.max_storage_gb} GB storage")

    # Calculate total demand and theoretical minimum
    total_cpu = sum(vm.cpu_cores for vm in vms)
    total_ram = sum(vm.ram_gb for vm in vms)
    total_storage = sum(vm.storage_gb for vm in vms)

    theoretical_min = max(
        total_cpu / server_template.max_cpu_cores,
        total_ram / server_template.max_ram_gb,
        total_storage / server_template.max_storage_gb
    )

    print(f"Total demand: CPU={total_cpu:.1f}, RAM={total_ram:.1f}, Storage={total_storage:.1f}")
    print(f"Theoretical minimum: {theoretical_min:.2f} servers")

    results = {
        'scenario': scenario_name,
        'num_vms': len(vms),
        'server_capacity': {
            'cpu': server_template.max_cpu_cores,
            'ram': server_template.max_ram_gb,
            'storage': server_template.max_storage_gb
        },
        'total_demand': {
            'cpu': round(total_cpu, 2),
            'ram': round(total_ram, 2),
            'storage': round(total_storage, 2)
        },
        'theoretical_min_servers': round(theoretical_min, 2)
    }

    # Benchmark GA
    print(f"\n[1/2] Running Genetic Algorithm...")
    ga_start = time.time()

    best_ga = run_simple_ga(
        vms=vms,
        server_template=server_template,
        population_size=50,
        generations=100,
        elitism_count=2,
        mutation_rate=0.3,
        initial_quality="random"
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
            'storage': round(ga_utils['storage'], 1),
            'average': round((ga_utils['cpu'] + ga_utils['ram'] + ga_utils['storage']) / 3, 1)
        }
    }

    print(f"✓ GA completed in {ga_time:.2f}s")
    print(f"  Result: {best_ga.num_servers_used} servers, fitness={best_ga.fitness:.2f}")
    print(f"  Utilization: CPU={ga_utils['cpu']:.1f}%, RAM={ga_utils['ram']:.1f}%, "
          f"Storage={ga_utils['storage']:.1f}%")

    # Benchmark WoC
    print(f"\n[2/2] Running Wisdom of Crowds...")
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
            'storage': round(woc_utils['storage'], 1),
            'average': round((woc_utils['cpu'] + woc_utils['ram'] + woc_utils['storage']) / 3, 1)
        },
        'speedup': round(ga_time / woc_time, 1) if woc_time > 0 else 0
    }

    print(f"✓ WoC completed in {woc_time:.2f}s")
    print(f"  Result: {best_woc.num_servers_used} servers, fitness={best_woc.fitness:.2f}")
    print(f"  Speedup: {results['woc']['speedup']}×")
    print(f"  Utilization: CPU={woc_utils['cpu']:.1f}%, RAM={woc_utils['ram']:.1f}%, "
          f"Storage={woc_utils['storage']:.1f}%")

    # Quality comparison
    server_reduction = round(
        ((best_ga.num_servers_used - best_woc.num_servers_used) / best_ga.num_servers_used) * 100, 1
    )

    results['comparison'] = {
        'server_reduction_pct': server_reduction,
        'servers_saved': best_ga.num_servers_used - best_woc.num_servers_used,
        'quality_equal': best_woc.num_servers_used == best_ga.num_servers_used,
        'woc_better': best_woc.num_servers_used < best_ga.num_servers_used,
        'ga_better': best_ga.num_servers_used < best_woc.num_servers_used
    }

    print(f"\nComparison:")
    print(f"  Server reduction: {server_reduction}% ({results['comparison']['servers_saved']} servers)")

    return results


def main():
    """Run comprehensive benchmarks on production scenarios."""

    print("="*80)
    print("PRODUCTION SCENARIO BENCHMARKS (500, 750, 1000 VMs)")
    print("="*80)
    print()
    print("This script will:")
    print("  1. Run benchmarks on production scenarios (500, 750, 1000 VMs)")
    print("  2. Compare GA vs WoC performance at scale")
    print("  3. Generate detailed JSON results")
    print("  4. Create summary statistics")
    print()
    print("="*80)

    production_scenarios = ['production', 'production_medium', 'production_large']
    seed = 42

    # Run production benchmarks
    print(f"\n{'#'*80}")
    print("BENCHMARKING PRODUCTION SCENARIOS")
    print(f"{'#'*80}")

    production_results = []
    for scenario in production_scenarios:
        try:
            results = benchmark_production_scenario(scenario, seed=seed)
            production_results.append(results)

            print(f"\n✓ {scenario.upper().replace('_', ' ')} complete")
            print(f"  GA: {results['ga']['servers_used']} servers in {results['ga']['time_seconds']}s")
            print(f"  WoC: {results['woc']['servers_used']} servers in {results['woc']['time_seconds']}s "
                  f"({results['woc']['speedup']}× faster)")
        except Exception as e:
            print(f"\n✗ Error benchmarking {scenario}: {e}")
            print(f"  Make sure you've downloaded the Azure dataset:")
            print(f"  python3 download_azure_dataset.py")
            import traceback
            traceback.print_exc()
            continue

    # Save results
    print(f"\n{'='*80}")
    print("SAVING RESULTS")
    print(f"{'='*80}")

    output_file = 'production_benchmark_results.json'
    with open(output_file, 'w') as f:
        json.dump(production_results, f, indent=2)
    print(f"✓ Production results saved: {output_file}")

    # Print comparison table
    print(f"\n{'='*80}")
    print("PRODUCTION SCENARIOS COMPARISON TABLE")
    print(f"{'='*80}")
    print()
    print(f"{'Scenario':<20} {'VMs':<6} {'Method':<6} {'Time':<8} {'Servers':<8} {'Fitness':<12} {'Util%':<8} {'Speedup'}")
    print("-"*110)

    for result in production_results:
        scenario = result['scenario'].replace('_', ' ').title()
        vms = result['num_vms']

        # GA
        print(f"{scenario:<20} {vms:<6} {'GA':<6} "
              f"{result['ga']['time_seconds']:<8.2f} "
              f"{result['ga']['servers_used']:<8} "
              f"{result['ga']['fitness']:<12.2f} "
              f"{result['ga']['utilization']['average']:<8.1f} {'':>8}")

        # WoC
        print(f"{'':>20} {'':>6} {'WoC':<6} "
              f"{result['woc']['time_seconds']:<8.2f} "
              f"{result['woc']['servers_used']:<8} "
              f"{result['woc']['fitness']:<12.2f} "
              f"{result['woc']['utilization']['average']:<8.1f} "
              f"{result['woc']['speedup']:>7.1f}×")

        print("-"*110)

    # Print key insights
    print(f"\n{'='*80}")
    print("KEY INSIGHTS")
    print(f"{'='*80}")
    print()

    for result in production_results:
        scenario = result['scenario'].replace('_', ' ').title()
        print(f"{scenario} ({result['num_vms']} VMs):")
        print(f"  • Theoretical min: {result['theoretical_min_servers']:.1f} servers")
        print(f"  • GA result: {result['ga']['servers_used']} servers in {result['ga']['time_seconds']:.1f}s")
        print(f"  • WoC result: {result['woc']['servers_used']} servers in {result['woc']['time_seconds']:.1f}s")
        print(f"  • Server reduction: {result['comparison']['server_reduction_pct']}% "
              f"({result['comparison']['servers_saved']} servers saved)")
        print(f"  • Speedup: {result['woc']['speedup']}× faster")
        print(f"  • Utilization improvement: {result['ga']['utilization']['average']:.1f}% → "
              f"{result['woc']['utilization']['average']:.1f}%")
        print()

    # Calculate averages
    avg_speedup = sum(r['woc']['speedup'] for r in production_results) / len(production_results)
    avg_reduction = sum(r['comparison']['server_reduction_pct'] for r in production_results) / len(production_results)

    print(f"Average Performance Across Production Scenarios:")
    print(f"  • Average speedup: {avg_speedup:.1f}×")
    print(f"  • Average server reduction: {avg_reduction:.1f}%")
    print()

    print("="*80)
    print("✅ PRODUCTION BENCHMARK COMPLETE!")
    print("="*80)
    print()
    print("Next steps:")
    print(f"  1. python3 visualize_production_scenarios.py  # Create visual charts")
    print(f"  2. Check {output_file} for detailed data")
    print("  3. Use in your presentation/report")
    print()


if __name__ == "__main__":
    main()
