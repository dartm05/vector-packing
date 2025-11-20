#!/usr/bin/env python3
"""
Quick test of the production scenario (500 VMs).
"""

import sys
import time
import json
from src.utils.data_generator import DataGenerator
from src.ga.simple_engine import run_simple_ga, create_initial_population, calculate_fitness
from src.woc import CrowdAnalyzer, CrowdBuilder

print("="*80)
print("TESTING PRODUCTION SCENARIO (500 VMs)")
print("="*80)

# Load Azure production scenario
scenario = DataGenerator.load_azure_scenario('production', seed=42)
vms = scenario['vms']
server_template = scenario['server_template']

print(f"\nLoaded {len(vms)} VMs from Azure dataset")
print(f"Server capacity: CPU={server_template.max_cpu_cores}, "
      f"RAM={server_template.max_ram_gb}GB, Storage={server_template.max_storage_gb}GB")

# Calculate theoretical minimum
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

# Run GA
print("\n" + "="*80)
print("RUNNING GENETIC ALGORITHM")
print("="*80)

ga_start = time.time()
ga_solution = run_simple_ga(
    vms=vms,
    server_template=server_template,
    population_size=50,
    generations=100,
    elitism_count=2,
    mutation_rate=0.3,
    initial_quality="random"
)
ga_time = time.time() - ga_start

print(f"\n✓ GA Complete:")
print(f"  Time: {ga_time:.2f}s")
print(f"  Servers: {ga_solution.num_servers_used}")
print(f"  Fitness: {ga_solution.fitness:.2f}")

# Run WoC
print("\n" + "="*80)
print("RUNNING WISDOM OF CROWDS")
print("="*80)

woc_start = time.time()

# Generate population for WoC
population = create_initial_population(vms, server_template, 30, quality="mixed")
for sol in population:
    calculate_fitness(sol)

# Analyze and build with WoC
analyzer = CrowdAnalyzer()
analyzer.analyze_solutions(population, top_k=20)

builder = CrowdBuilder(analyzer)  # Pass analyzer, not just the matrix
woc_solution = builder.build_solution(vms, server_template)
calculate_fitness(woc_solution)

woc_time = time.time() - woc_start

print(f"\n✓ WoC Complete:")
print(f"  Time: {woc_time:.2f}s")
print(f"  Servers: {woc_solution.num_servers_used}")
print(f"  Fitness: {woc_solution.fitness:.2f}")

# Compare
print("\n" + "="*80)
print("COMPARISON RESULTS")
print("="*80)

speedup = ga_time / woc_time if woc_time > 0 else float('inf')
server_improvement = ((ga_solution.num_servers_used - woc_solution.num_servers_used) /
                      ga_solution.num_servers_used * 100)

print(f"Speedup: {speedup:.1f}×")
print(f"Server reduction: {server_improvement:.1f}%")
print(f"WoC better solution: {woc_solution.fitness < ga_solution.fitness}")
print(f"GA servers: {ga_solution.num_servers_used} → WoC servers: {woc_solution.num_servers_used}")

result = {
    "scenario": "production",
    "num_vms": len(vms),
    "ga": {
        "time_seconds": round(ga_time, 2),
        "servers_used": ga_solution.num_servers_used,
        "fitness": round(ga_solution.fitness, 2)
    },
    "woc": {
        "time_seconds": round(woc_time, 2),
        "servers_used": woc_solution.num_servers_used,
        "fitness": round(woc_solution.fitness, 2),
        "speedup": round(speedup, 1)
    }
}

print(f"\n✓ Result saved")
print(json.dumps(result, indent=2))
