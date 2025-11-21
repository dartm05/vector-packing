"""
Test the simplified GA engine
"""

from src.utils.data_generator import DataGenerator
from src.ga.simple_engine import run_simple_ga


def test_simple_ga():
    """Test the simplified GA with better debugging."""

    print("="*70)
    print("Testing SIMPLIFIED GA")
    print("="*70)

    # Generate test data
    scenario = DataGenerator.generate_scenario('small', seed=42)
    vms = scenario['vms']
    server_template = scenario['server_template']

    print(f"\nProblem size: {len(vms)} VMs")
    print(f"Server capacity: {server_template.max_cpu_cores} cores, "
          f"{server_template.max_ram_gb} GB RAM, "
          f"{server_template.max_storage_gb} GB storage")

    # Run simplified GA starting with poor solutions
    # This demonstrates that the GA operators work and improve over time
    best_solution = run_simple_ga(
        vms=vms,
        server_template=server_template,
        population_size=50,
        generations=100,
        elitism_count=2,
        mutation_rate=0.5,  # Higher mutation rate for more exploration
        initial_quality="poor"  # Start with worse solutions to show improvement
    )

    # Display results
    print(f"\n{'='*70}")
    print("FINAL RESULTS:")
    print(f"{'='*70}")
    print(f"Valid solution: {best_solution.is_valid()}")
    print(f"Servers used: {best_solution.num_servers_used}")
    print(f"Total VMs: {best_solution.total_vms}")
    print(f"Fitness score: {best_solution.fitness:.4f}")

    utils = best_solution.average_utilization
    print(f"Average utilization:")
    print(f"  - CPU: {utils['cpu']:.2f}%")
    print(f"  - RAM: {utils['ram']:.2f}%")
    print(f"  - Storage: {utils['storage']:.2f}%")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_simple_ga()
