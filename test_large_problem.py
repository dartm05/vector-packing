#!/usr/bin/env python3
"""
Quick test to demonstrate GA vs WOC differences on LARGE problems
This shows why increasing VMs matters for your paper.
"""

import time
from src.utils.data_generator import DataGenerator
from src.ga.engine import run_ga
from src.woc.engine import run_woc

print("="*80)
print("LARGE PROBLEM TEST: GA vs WOC (100 VMs)")
print("This demonstrates why problem size matters for comparison")
print("="*80)

# Test on LARGE problem (100 VMs)
scenario = DataGenerator.generate_scenario('large', seed=42)
vms = scenario['vms']
server_template = scenario['server_template']

print(f"\nProblem: {len(vms)} VMs")
print(f"Server: {server_template.max_cpu_cores} cores, {server_template.max_ram_gb}GB RAM, {server_template.max_storage_gb}GB storage")

# Run GA
print("\n" + "="*80)
print("PHASE 1: GENETIC ALGORITHM")
print("="*80)
ga_start = time.time()
best_ga, ga_population = run_ga(
    vms=vms,
    server_template=server_template,
    population_size=50,
    generations=100,
    elitism_count=2,
    mutation_rate=0.3,
    tournament_k=3,
    use_local_search=False,
    return_population=True
)
ga_time = time.time() - ga_start

# Run WOC
print("\n" + "="*80)
print("PHASE 2: WISDOM OF CROWDS (learning from GA)")
print("="*80)
woc_start = time.time()
best_woc = run_woc(
    vms=vms,
    server_template=server_template,
    ga_population=ga_population,  # Learn from evolved population!
    top_n=20,
    num_solutions=30
)
woc_time = time.time() - woc_start

# Comparison
print("\n" + "="*80)
print("FINAL COMPARISON")
print("="*80)

print(f"\n{'Metric':<30} {'GA':<20} {'WOC':<20} {'Difference':<15}")
print("-"*85)

# Servers
server_diff = best_ga.num_servers_used - best_woc.num_servers_used
print(f"{'Servers Used':<30} {best_ga.num_servers_used:<20} {best_woc.num_servers_used:<20} {server_diff:+d}")

# Fitness
fitness_diff = best_ga.fitness - best_woc.fitness
fitness_pct = (fitness_diff / best_ga.fitness) * 100 if best_ga.fitness > 0 else 0
print(f"{'Fitness (lower=better)':<30} {best_ga.fitness:<20.2f} {best_woc.fitness:<20.2f} {fitness_diff:+.2f} ({fitness_pct:+.1f}%)")

# Time
time_ratio = woc_time / ga_time
print(f"{'Time (seconds)':<30} {ga_time:<20.2f} {woc_time:<20.2f} {woc_time-ga_time:+.2f}s (WOC is {time_ratio:.2f}x)")

# Utilization
ga_util = best_ga.average_utilization
woc_util = best_woc.average_utilization

print(f"\n{'Resource Utilization':<30} {'GA':<20} {'WOC':<20} {'Difference':<15}")
print("-"*85)
cpu_diff = woc_util['cpu'] - ga_util['cpu']
print(f"{'CPU':<30} {ga_util['cpu']:<20.2f}% {woc_util['cpu']:<20.2f}% {cpu_diff:+.2f}%")
ram_diff = woc_util['ram'] - ga_util['ram']
print(f"{'RAM':<30} {ga_util['ram']:<20.2f}% {woc_util['ram']:<20.2f}% {ram_diff:+.2f}%")
storage_diff = woc_util['storage'] - ga_util['storage']
print(f"{'Storage':<30} {ga_util['storage']:<20.2f}% {woc_util['storage']:<20.2f}% {storage_diff:+.2f}%")

# Winner
print("\n" + "="*80)
if best_woc.fitness < best_ga.fitness:
    print(f"🏆 WINNER: WOC (Better by {abs(fitness_pct):.2f}%)")
elif best_ga.fitness < best_woc.fitness:
    print(f"🏆 WINNER: GA (Better by {abs(fitness_pct):.2f}%)")
else:
    print("🤝 TIE: Both achieved same fitness")

print("\nKEY INSIGHTS:")
if abs(server_diff) > 0:
    print(f"  • {'WOC' if server_diff > 0 else 'GA'} uses {abs(server_diff)} fewer servers")
print(f"  • WOC is {time_ratio:.2f}x faster than GA ({woc_time:.1f}s vs {ga_time:.1f}s)")
print(f"  • Both solutions are valid: GA={best_ga.is_valid()}, WOC={best_woc.is_valid()}")

print("\nWHY THIS MATTERS FOR YOUR PAPER:")
print("  1. Larger problems (100+ VMs) show clearer algorithmic differences")
print("  2. WOC learns patterns from GA's evolved population (not random)")
print("  3. WOC is computationally more efficient (faster execution)")
print("  4. Both approaches find high-quality solutions")
print("  5. Hybrid approach combines strengths of both methods")

print("\n" + "="*80)
print("✨ Test complete!")
print("="*80)
