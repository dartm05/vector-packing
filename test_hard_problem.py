#!/usr/bin/env python3
"""
Generate HARDER problem instances for meaningful GA vs WOC comparison.

The issue: Default scenarios are too easy because heuristics immediately
find optimal solutions. We need harder problems with:
1. More VMs with varied sizes
2. Tighter server capacity constraints
3. More diverse resource requirements
"""

import random
from src.models import VirtualMachine, Server
from src.ga.engine import run_ga
from src.woc.engine import run_woc
import time


def generate_hard_problem(num_vms=200, seed=42):
    """
    Generate a challenging problem instance.
    
    Key differences from default:
    - More VMs (200 instead of 100)
    - More heterogeneous VM sizes
    - Tighter capacity constraints
    - Unbalanced resource requirements
    """
    random.seed(seed)
    
    vms = []
    
    # Create diverse VM types with different resource profiles
    vm_types = [
        # (cpu_range, ram_range, storage_range, count)
        ((1, 4), (2, 8), (10, 50), 60),      # Small VMs
        ((4, 12), (8, 32), (50, 200), 80),   # Medium VMs
        ((12, 24), (32, 128), (200, 800), 40),  # Large VMs  
        ((2, 8), (64, 128), (100, 300), 20),  # RAM-heavy VMs
    ]
    
    vm_id = 0
    for (cpu_min, cpu_max), (ram_min, ram_max), (storage_min, storage_max), count in vm_types:
        for _ in range(count):
            vm = VirtualMachine(
                id=vm_id,
                cpu_cores=random.uniform(cpu_min, cpu_max),
                ram_gb=random.uniform(ram_min, ram_max),
                storage_gb=random.uniform(storage_min, storage_max)
            )
            vms.append(vm)
            vm_id += 1
    
    # Shuffle to make harder
    random.shuffle(vms)
    
    # Server with moderate capacity (not too generous)
    server_template = Server(
        id=0,
        max_cpu_cores=64,   # Moderate CPU
        max_ram_gb=256,     # Moderate RAM
        max_storage_gb=2000  # Moderate storage
    )
    
    return vms, server_template


def run_hard_comparison():
    """Run comparison on hard problem instances."""
    
    print("="*80)
    print("HARD PROBLEM COMPARISON: GA vs WOC")
    print("200 VMs with diverse resource requirements")
    print("="*80)
    
    # Generate hard problem
    vms, server_template = generate_hard_problem(num_vms=200, seed=42)
    
    print(f"\nProblem characteristics:")
    print(f"  Total VMs: {len(vms)}")
    print(f"  Server capacity: {server_template.max_cpu_cores} cores, "
          f"{server_template.max_ram_gb}GB RAM, {server_template.max_storage_gb}GB storage")
    
    # Analyze VM distribution
    small_vms = sum(1 for vm in vms if vm.cpu_cores < 4)
    medium_vms = sum(1 for vm in vms if 4 <= vm.cpu_cores < 12)
    large_vms = sum(1 for vm in vms if vm.cpu_cores >= 12)
    
    print(f"  VM distribution: {small_vms} small, {medium_vms} medium, {large_vms} large")
    
    # Calculate theoretical minimum servers (lower bound)
    total_cpu = sum(vm.cpu_cores for vm in vms)
    total_ram = sum(vm.ram_gb for vm in vms)
    total_storage = sum(vm.storage_gb for vm in vms)
    
    min_servers_cpu = total_cpu / server_template.max_cpu_cores
    min_servers_ram = total_ram / server_template.max_ram_gb
    min_servers_storage = total_storage / server_template.max_storage_gb
    theoretical_min = max(min_servers_cpu, min_servers_ram, min_servers_storage)
    
    print(f"  Theoretical minimum servers: {theoretical_min:.1f}")
    print(f"    (CPU: {min_servers_cpu:.1f}, RAM: {min_servers_ram:.1f}, Storage: {min_servers_storage:.1f})")
    
    # Run GA
    print("\n" + "="*80)
    print("PHASE 1: GENETIC ALGORITHM")
    print("="*80)
    ga_start = time.time()
    best_ga, ga_population = run_ga(
        vms=vms,
        server_template=server_template,
        population_size=100,  # Larger population for harder problem
        generations=200,      # More generations
        elitism_count=5,      # More elitism
        mutation_rate=0.3,
        tournament_k=5,       # Larger tournament
        use_local_search=False,
        return_population=True
    )
    ga_time = time.time() - ga_start
    
    # Run WOC
    print("\n" + "="*80)
    print("PHASE 2: WISDOM OF CROWDS")
    print("="*80)
    woc_start = time.time()
    best_woc = run_woc(
        vms=vms,
        server_template=server_template,
        ga_population=ga_population,
        top_n=30,  # Learn from more solutions
        num_solutions=50  # Generate more solutions
    )
    woc_time = time.time() - woc_start
    
    # Detailed comparison
    print("\n" + "="*80)
    print("DETAILED COMPARISON")
    print("="*80)
    
    print(f"\n{'Metric':<35} {'GA':<20} {'WOC':<20} {'Difference':<20}")
    print("-"*95)
    
    # Servers
    server_diff = best_ga.num_servers_used - best_woc.num_servers_used
    server_pct = (server_diff / best_ga.num_servers_used) * 100 if best_ga.num_servers_used > 0 else 0
    print(f"{'Servers Used':<35} {best_ga.num_servers_used:<20} {best_woc.num_servers_used:<20} {server_diff:+d} ({server_pct:+.1f}%)")
    
    # Compare to theoretical minimum
    ga_overhead = ((best_ga.num_servers_used - theoretical_min) / theoretical_min) * 100
    woc_overhead = ((best_woc.num_servers_used - theoretical_min) / theoretical_min) * 100
    print(f"{'Overhead vs Theoretical Min':<35} {ga_overhead:+.1f}%{' '*14} {woc_overhead:+.1f}%")
    
    # Fitness
    fitness_diff = best_ga.fitness - best_woc.fitness
    fitness_pct = (fitness_diff / best_ga.fitness) * 100 if best_ga.fitness > 0 else 0
    print(f"{'Fitness (lower=better)':<35} {best_ga.fitness:<20.2f} {best_woc.fitness:<20.2f} {fitness_diff:+.2f} ({fitness_pct:+.2f}%)")
    
    # Time
    time_ratio = woc_time / ga_time
    print(f"{'Computation Time (seconds)':<35} {ga_time:<20.2f} {woc_time:<20.2f} {time_ratio:.2f}x")
    
    # Utilization
    ga_util = best_ga.average_utilization
    woc_util = best_woc.average_utilization
    
    print(f"\n{'Resource Utilization':<35} {'GA':<20} {'WOC':<20} {'Difference':<20}")
    print("-"*95)
    
    for resource in ['cpu', 'ram', 'storage']:
        diff = woc_util[resource] - ga_util[resource]
        print(f"{resource.upper():<35} {ga_util[resource]:<19.2f}% {woc_util[resource]:<19.2f}% {diff:+.2f}%")
    
    avg_ga = sum(ga_util.values()) / 3
    avg_woc = sum(woc_util.values()) / 3
    avg_diff = avg_woc - avg_ga
    print(f"{'Average':<35} {avg_ga:<19.2f}% {avg_woc:<19.2f}% {avg_diff:+.2f}%")
    
    # Winner
    print("\n" + "="*80)
    if best_woc.fitness < best_ga.fitness - 0.01:  # WOC significantly better
        improvement = abs(fitness_pct)
        server_saving = abs(server_diff)
        print(f"🏆 WINNER: WOC")
        print(f"   • {improvement:.2f}% better fitness")
        if server_diff > 0:
            print(f"   • Uses {server_saving} fewer servers")
        print(f"   • {time_ratio:.2f}x computation time of GA")
    elif best_ga.fitness < best_woc.fitness - 0.01:  # GA significantly better
        improvement = abs(fitness_pct)
        print(f"🏆 WINNER: GA")
        print(f"   • {improvement:.2f}% better fitness")
        if server_diff < 0:
            print(f"   • Uses {abs(server_diff)} fewer servers")
    else:
        print("🤝 TIE: Both achieved similar fitness")
        print(f"   • WOC is {time_ratio:.2f}x computation time of GA")
        if avg_woc > avg_ga:
            print(f"   • WOC has {avg_diff:.1f}% better average utilization")
    
    print("\n" + "="*80)
    print("FOR YOUR PAPER:")
    print("="*80)
    print(f"""
1. PROBLEM COMPLEXITY:
   - 200 VMs with heterogeneous resource requirements
   - Theoretical minimum: {theoretical_min:.1f} servers
   - GA achieved: {best_ga.num_servers_used} servers ({ga_overhead:+.1f}% overhead)
   - WOC achieved: {best_woc.num_servers_used} servers ({woc_overhead:+.1f}% overhead)

2. SOLUTION QUALITY:
   - GA fitness: {best_ga.fitness:.2f}
   - WOC fitness: {best_woc.fitness:.2f}
   - Difference: {abs(fitness_pct):.2f}%

3. COMPUTATIONAL EFFICIENCY:
   - GA: {ga_time:.1f}s with {100} population over {200} generations
   - WOC: {woc_time:.1f}s learning from GA and generating {50} solutions
   - Ratio: {time_ratio:.2f}x

4. METHODOLOGY:
   - GA uses evolutionary operators (selection, crossover, mutation)
   - WOC learns VM affinity patterns from successful GA solutions
   - WOC builds new solutions using collective intelligence
   - Both approaches find high-quality solutions

5. KEY CONTRIBUTION:
   - WOC as alternative/complement to GA for bin packing
   - Learns patterns from successful solutions
   - Computationally {'more' if time_ratio > 1 else 'less'} expensive than full GA
   - Can be used as post-processing or standalone approach
""")
    
    print("="*80)
    print("✨ Hard problem test complete!")
    print("="*80)


if __name__ == "__main__":
    run_hard_comparison()
