#!/usr/bin/env python3
"""
Generate comprehensive comparison between Synthetic and Azure data.

This script runs benchmarks on both data sources and creates:
1. Benchmark results JSON files
2. Comparison visualizations
3. Detailed analysis reports
"""

import time
import json
from pathlib import Path
from src.utils.data_generator import DataGenerator
from src.ga.simple_engine import run_simple_ga, create_initial_population, calculate_fitness
from src.woc import CrowdAnalyzer, CrowdBuilder


def benchmark_scenario(scenario_name, data_source='synthetic', seed=42):
    """Run both GA and WoC on a scenario and collect results.

    Args:
        scenario_name: 'small', 'medium', 'large', 'extra_large', or 'production'
        data_source: 'synthetic' or 'azure'
        seed: Random seed for reproducibility
    """

    print(f"\n{'='*80}")
    print(f"Benchmarking {scenario_name.upper()} scenario with {data_source.upper()} data")
    print(f"{'='*80}")

    # Load problem data
    if data_source == 'azure':
        scenario = DataGenerator.load_azure_scenario(scenario_name, seed=seed)
        metadata = scenario.get('metadata', {})
        print(f"Data source: Azure Packing Trace 2020")
        print(f"Original pool: {metadata.get('original_pool_size', 'N/A'):,} VMs")
    else:
        scenario = DataGenerator.generate_scenario(scenario_name, seed=seed)
        print(f"Data source: Synthetic (pattern-based generation)")

    vms = scenario['vms']
    server_template = scenario['server_template']

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
        'data_source': data_source,
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

    # Quality comparison
    if best_woc.num_servers_used <= best_ga.num_servers_used:
        quality_verdict = "equal or better"
    else:
        quality_verdict = "slightly worse"

    results['comparison'] = {
        'quality_verdict': quality_verdict,
        'quality_equal': best_woc.num_servers_used == best_ga.num_servers_used,
        'woc_better': best_woc.num_servers_used < best_ga.num_servers_used,
        'ga_better': best_ga.num_servers_used < best_woc.num_servers_used
    }

    return results


def main():
    """Run comprehensive benchmarks on both data sources."""

    print("="*80)
    print("COMPREHENSIVE BENCHMARK: SYNTHETIC vs AZURE DATA")
    print("="*80)
    print()
    print("This script will:")
    print("  1. Run benchmarks on Synthetic data (all scenarios)")
    print("  2. Run benchmarks on Azure data (all scenarios)")
    print("  3. Generate comparison visualizations")
    print("  4. Create detailed analysis reports")
    print()
    print("="*80)

    scenarios = ['small', 'medium', 'large', 'extra_large', 'production']
    seed = 42

    # Run synthetic benchmarks
    print(f"\n{'#'*80}")
    print("PHASE 1: SYNTHETIC DATA BENCHMARKS")
    print(f"{'#'*80}")

    synthetic_results = []
    for scenario in scenarios:
        try:
            results = benchmark_scenario(scenario, data_source='synthetic', seed=seed)
            synthetic_results.append(results)

            print(f"\n✓ {scenario.upper()} synthetic complete")
            print(f"  GA: {results['ga']['servers_used']} servers in {results['ga']['time_seconds']}s")
            print(f"  WoC: {results['woc']['servers_used']} servers in {results['woc']['time_seconds']}s "
                  f"({results['woc']['speedup']}× faster)")
        except Exception as e:
            print(f"\n✗ Error benchmarking synthetic {scenario}: {e}")
            continue

    # Run Azure benchmarks
    print(f"\n{'#'*80}")
    print("PHASE 2: AZURE DATA BENCHMARKS")
    print(f"{'#'*80}")

    azure_results = []
    for scenario in scenarios:
        try:
            results = benchmark_scenario(scenario, data_source='azure', seed=seed)
            azure_results.append(results)

            print(f"\n✓ {scenario.upper()} Azure complete")
            print(f"  GA: {results['ga']['servers_used']} servers in {results['ga']['time_seconds']}s")
            print(f"  WoC: {results['woc']['servers_used']} servers in {results['woc']['time_seconds']}s "
                  f"({results['woc']['speedup']}× faster)")
        except Exception as e:
            print(f"\n✗ Error benchmarking Azure {scenario}: {e}")
            print(f"  Make sure you've downloaded the Azure dataset:")
            print(f"  python3 download_azure_dataset.py")
            continue

    # Save results
    print(f"\n{'='*80}")
    print("SAVING RESULTS")
    print(f"{'='*80}")

    with open('synthetic_benchmark_results.json', 'w') as f:
        json.dump(synthetic_results, f, indent=2)
    print("✓ Synthetic results saved: synthetic_benchmark_results.json")

    with open('azure_benchmark_results.json', 'w') as f:
        json.dump(azure_results, f, indent=2)
    print("✓ Azure results saved: azure_benchmark_results.json")

    # Combined results
    combined_results = {
        'synthetic': synthetic_results,
        'azure': azure_results,
        'metadata': {
            'seed': seed,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'scenarios': scenarios
        }
    }

    with open('combined_benchmark_results.json', 'w') as f:
        json.dump(combined_results, f, indent=2)
    print("✓ Combined results saved: combined_benchmark_results.json")

    # Print comparison table
    print(f"\n{'='*80}")
    print("COMPARISON TABLE")
    print(f"{'='*80}")
    print()
    print(f"{'Scenario':<12} {'Data':<10} {'VMs':<5} {'Method':<6} {'Time':<8} {'Servers':<8} {'Fitness':<10} {'Speedup'}")
    print("-"*100)

    for syn_result, az_result in zip(synthetic_results, azure_results):
        scenario = syn_result['scenario'].capitalize()
        vms = syn_result['num_vms']

        # Synthetic GA
        print(f"{scenario:<12} {'Synthetic':<10} {vms:<5} {'GA':<6} "
              f"{syn_result['ga']['time_seconds']:<8.2f} "
              f"{syn_result['ga']['servers_used']:<8} "
              f"{syn_result['ga']['fitness']:<10.2f} {'':>8}")

        # Synthetic WoC
        print(f"{'':>12} {'':>10} {'':>5} {'WoC':<6} "
              f"{syn_result['woc']['time_seconds']:<8.2f} "
              f"{syn_result['woc']['servers_used']:<8} "
              f"{syn_result['woc']['fitness']:<10.2f} "
              f"{syn_result['woc']['speedup']:>7.1f}×")

        print("-"*100)

        # Azure GA
        print(f"{scenario:<12} {'Azure':<10} {vms:<5} {'GA':<6} "
              f"{az_result['ga']['time_seconds']:<8.2f} "
              f"{az_result['ga']['servers_used']:<8} "
              f"{az_result['ga']['fitness']:<10.2f} {'':>8}")

        # Azure WoC
        print(f"{'':>12} {'':>10} {'':>5} {'WoC':<6} "
              f"{az_result['woc']['time_seconds']:<8.2f} "
              f"{az_result['woc']['servers_used']:<8} "
              f"{az_result['woc']['fitness']:<10.2f} "
              f"{az_result['woc']['speedup']:>7.1f}×")

        print("="*100)

    # Print key insights
    print(f"\n{'='*80}")
    print("KEY INSIGHTS")
    print(f"{'='*80}")
    print()

    for i, (syn, az) in enumerate(zip(synthetic_results, azure_results)):
        scenario = syn['scenario']
        print(f"{scenario.upper()}:")
        print(f"  • Synthetic: {syn['ga']['servers_used']} servers (theoretical min: {syn['theoretical_min_servers']:.1f})")
        print(f"  • Azure:     {az['ga']['servers_used']} servers (theoretical min: {az['theoretical_min_servers']:.1f})")

        if az['ga']['servers_used'] < syn['ga']['servers_used']:
            print(f"  → Azure data packs {syn['ga']['servers_used'] - az['ga']['servers_used']} fewer servers!")
        elif az['ga']['servers_used'] > syn['ga']['servers_used']:
            print(f"  → Synthetic data packs {az['ga']['servers_used'] - syn['ga']['servers_used']} fewer servers!")
        else:
            print(f"  → Equal packing efficiency!")
        print()

    print("="*80)
    print("✅ COMPREHENSIVE BENCHMARK COMPLETE!")
    print("="*80)
    print()
    print("Next steps:")
    print("  1. python3 create_comparison_visualization.py  # Create visual charts")
    print("  2. Check the JSON files for detailed data")
    print("  3. Use in your presentation/report")
    print()


if __name__ == "__main__":
    main()
