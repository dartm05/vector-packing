"""
Test script to verify GA convergence improvements
"""

from src.utils.data_generator import DataGenerator
from src.ga.engine import run_ga

def test_ga_convergence():
    """Test the GA with improved convergence mechanisms."""
    
    print("="*60)
    print("Testing GA Convergence Improvements")
    print("="*60)
    
    # Test on different problem sizes
    scenarios = ['small', 'medium']
    
    for scenario_name in scenarios:
        print(f"\n{'='*60}")
        print(f"Testing scenario: {scenario_name.upper()}")
        print(f"{'='*60}\n")
        
        # Generate test data
        scenario = DataGenerator.generate_scenario(scenario_name, seed=42)
        vms = scenario['vms']
        server_template = scenario['server_template']
        
        print(f"Problem size: {len(vms)} VMs")
        print(f"Server capacity: {server_template.max_cpu_cores} cores, "
              f"{server_template.max_ram_gb} GB RAM, "
              f"{server_template.max_storage_gb} GB storage\n")
        
        # Run GA with improved parameters
        best_solution = run_ga(
            vms=vms,
            server_template=server_template,
            population_size=50,
            generations=100,
            elitism_count=2,
            mutation_rate=0.3,
            tournament_k=3
        )
        
        # Display results
        print(f"\n{'='*60}")
        print("FINAL RESULTS:")
        print(f"{'='*60}")
        print(f"Valid solution: {best_solution.is_valid()}")
        print(f"Servers used: {best_solution.num_servers_used}")
        print(f"Total VMs: {best_solution.total_vms}")
        print(f"Fitness score: {best_solution.fitness:.4f}")
        print(f"Average utilization:")
        utils = best_solution.average_utilization
        print(f"  - CPU: {utils['cpu']:.2f}%")
        print(f"  - RAM: {utils['ram']:.2f}%")
        print(f"  - Storage: {utils['storage']:.2f}%")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    test_ga_convergence()
