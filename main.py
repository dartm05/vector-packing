#!/usr/bin/env python3
"""
Main entry point for the Vector Packing Solver
Demonstrates how to use the Genetic Algorithm to solve VM placement problems
test2
"""

import argparse
from src.utils.data_generator import DataGenerator
from src.ga.engine import run_ga


def main():
    """Main function to run the Vector Packing Solver."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Vector Packing Solver using Genetic Algorithm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (small scenario)
  python main.py
  
  # Run medium scenario with more generations
  python main.py --scenario medium --generations 100
  
  # Run with local search enabled
  python main.py --scenario large --local-search
  
  # Custom population and mutation
  python main.py --population 100 --mutation-rate 0.4
        """
    )
    
    parser.add_argument(
        '--scenario',
        type=str,
        choices=['small', 'medium', 'large', 'extra_large'],
        default='small',
        help='Problem scenario size (default: small)'
    )
    
    parser.add_argument(
        '--population',
        type=int,
        default=50,
        help='Population size (default: 50)'
    )
    
    parser.add_argument(
        '--generations',
        type=int,
        default=100,
        help='Maximum number of generations (default: 100)'
    )
    
    parser.add_argument(
        '--mutation-rate',
        type=float,
        default=0.3,
        help='Mutation rate (default: 0.3)'
    )
    
    parser.add_argument(
        '--elitism',
        type=int,
        default=2,
        help='Number of elite solutions preserved (default: 2)'
    )
    
    parser.add_argument(
        '--tournament-k',
        type=int,
        default=3,
        help='Tournament size for selection (default: 3)'
    )
    
    parser.add_argument(
        '--local-search',
        action='store_true',
        help='Enable local search (memetic algorithm)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("=" * 70)
    print("VECTOR PACKING SOLVER - GENETIC ALGORITHM")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Scenario: {args.scenario}")
    print(f"  Population size: {args.population}")
    print(f"  Max generations: {args.generations}")
    print(f"  Mutation rate: {args.mutation_rate}")
    print(f"  Elitism: {args.elitism}")
    print(f"  Tournament k: {args.tournament_k}")
    print(f"  Local search: {'Enabled' if args.local_search else 'Disabled'}")
    print(f"  Random seed: {args.seed}")
    print()
    
    # Generate test data
    print(f"Generating test data for '{args.scenario}' scenario...")
    scenario = DataGenerator.generate_scenario(args.scenario, seed=args.seed)
    vms = scenario['vms']
    server_template = scenario['server_template']
    
    print(f"  VMs to place: {len(vms)}")
    print(f"  Server capacity: {server_template.max_cpu_cores} cores, "
          f"{server_template.max_ram_gb} GB RAM, "
          f"{server_template.max_storage_gb} GB storage")
    print()
    
    # Run Genetic Algorithm
    best_solution = run_ga(
        vms=vms,
        server_template=server_template,
        population_size=args.population,
        generations=args.generations,
        elitism_count=args.elitism,
        mutation_rate=args.mutation_rate,
        tournament_k=args.tournament_k,
        use_local_search=args.local_search
    )
    
    # Display final results
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"\n✅ Solution found!")
    print(f"  Valid: {best_solution.is_valid()}")
    print(f"  Servers used: {best_solution.num_servers_used}")
    print(f"  Total VMs placed: {best_solution.total_vms} / {len(vms)}")
    print(f"  Fitness score: {best_solution.fitness:.2f}")
    
    print(f"\n  Average utilization:")
    utils = best_solution.average_utilization
    print(f"    CPU: {utils['cpu']:.2f}%")
    print(f"    RAM: {utils['ram']:.2f}%")
    print(f"    Storage: {utils['storage']:.2f}%")
    
    # Show per-server breakdown
    print(f"\n  Server breakdown:")
    used_servers = [s for s in best_solution.servers if s.vms]
    for i, server in enumerate(used_servers, 1):
        print(f"    Server {i}: {len(server.vms)} VMs, "
              f"CPU: {server.utilization_cpu:.1f}%, "
              f"RAM: {server.utilization_ram:.1f}%, "
              f"Storage: {server.utilization_storage:.1f}%")
    
    print("\n" + "=" * 70)
    print("✨ Done!")
    print("=" * 70)


if __name__ == "__main__":
    main()
