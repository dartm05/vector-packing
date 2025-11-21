"""
Test script for Azure Data Loader

This script validates the Azure data loader and provides statistics
about the loaded real-world VM data.
"""

from src.utils import AzureDataLoader, DataGenerator
from src.ga.simple_engine import run_simple_ga
import time


def test_basic_loading():
    """Test basic data loading functionality."""
    print("\n" + "=" * 80)
    print("TEST 1: Basic Data Loading")
    print("=" * 80)

    db_path = 'datasets/packing_trace_zone_a_v1.sqlite'
    loader = AzureDataLoader(db_path)

    # Print dataset statistics
    loader.print_statistics()

    # Load VM types
    vm_types = loader.load_vm_types()
    print(f"\nLoaded {len(vm_types)} VM types")

    # Show sample VM types
    print("\nSample VM Types (first 5):")
    for vm_type_id in list(vm_types.keys())[:5]:
        vm_type = vm_types[vm_type_id]
        print(f"  Type {vm_type_id}: CPU={vm_type['core']:.4f}, "
              f"MEM={vm_type['memory']:.4f}, SSD={vm_type['ssd']:.4f}")


def test_scenario_generation():
    """Test generating scenarios of different sizes."""
    print("\n" + "=" * 80)
    print("TEST 2: Scenario Generation")
    print("=" * 80)

    db_path = 'datasets/packing_trace_zone_a_v1.sqlite'
    loader = AzureDataLoader(db_path)

    for scenario_size in ['small', 'medium', 'large', 'extra_large']:
        print(f"\n{'-' * 80}")
        print(f"Generating {scenario_size.upper()} scenario...")
        print(f"{'-' * 80}")

        scenario = loader.generate_scenario_from_azure(
            scenario_size=scenario_size,
            seed=42
        )

        vms = scenario['vms']
        server = scenario['server_template']

        print(f"VMs generated:           {len(vms)}")
        print(f"Server capacity:         {server.max_cpu_cores} cores, "
              f"{server.max_ram_gb} GB RAM, {server.max_storage_gb} GB storage")

        # Calculate resource statistics
        total_cpu = sum(vm.cpu_cores for vm in vms)
        total_ram = sum(vm.ram_gb for vm in vms)
        total_storage = sum(vm.storage_gb for vm in vms)

        print(f"\nTotal resource demand:")
        print(f"  CPU:                   {total_cpu:.2f} cores")
        print(f"  RAM:                   {total_ram:.2f} GB")
        print(f"  Storage:               {total_storage:.2f} GB")

        # Theoretical minimum servers
        min_servers_cpu = total_cpu / server.max_cpu_cores
        min_servers_ram = total_ram / server.max_ram_gb
        min_servers_storage = total_storage / server.max_storage_gb
        theoretical_min = max(min_servers_cpu, min_servers_ram, min_servers_storage)

        print(f"\nTheoretical minimum servers:")
        print(f"  By CPU:                {min_servers_cpu:.2f}")
        print(f"  By RAM:                {min_servers_ram:.2f}")
        print(f"  By Storage:            {min_servers_storage:.2f}")
        print(f"  Overall minimum:       {theoretical_min:.2f} ≈ {int(theoretical_min) + 1} servers")

        # Show VM size distribution
        print(f"\nVM size distribution:")
        small_vms = sum(1 for vm in vms if vm.cpu_cores < 8)
        medium_vms = sum(1 for vm in vms if 8 <= vm.cpu_cores < 16)
        large_vms = sum(1 for vm in vms if vm.cpu_cores >= 16)

        print(f"  Small (<8 cores):      {small_vms} VMs ({small_vms/len(vms)*100:.1f}%)")
        print(f"  Medium (8-16 cores):   {medium_vms} VMs ({medium_vms/len(vms)*100:.1f}%)")
        print(f"  Large (≥16 cores):     {large_vms} VMs ({large_vms/len(vms)*100:.1f}%)")


def test_data_generator_integration():
    """Test integration with DataGenerator."""
    print("\n" + "=" * 80)
    print("TEST 3: DataGenerator Integration")
    print("=" * 80)

    scenario = DataGenerator.load_azure_scenario('small', seed=42)

    print(f"Scenario name:           {scenario['scenario_name']}")
    print(f"Number of VMs:           {scenario['num_vms']}")
    print(f"Server template:         {scenario['server_template'].name}")
    print(f"\nMetadata:")
    for key, value in scenario['metadata'].items():
        print(f"  {key:<25} {value}")


def test_quick_ga_run():
    """Test running GA on Azure data."""
    print("\n" + "=" * 80)
    print("TEST 4: Quick GA Run on Azure Data")
    print("=" * 80)

    # Load small Azure scenario
    scenario = DataGenerator.load_azure_scenario('small', seed=42)
    vms = scenario['vms']
    server = scenario['server_template']

    print(f"Running GA on {len(vms)} real VMs from Azure...")
    print(f"Server capacity: {server.max_cpu_cores} cores, "
          f"{server.max_ram_gb} GB RAM, {server.max_storage_gb} GB storage\n")

    start_time = time.time()

    best_solution = run_simple_ga(
        vms=vms,
        server_template=server,
        population_size=50,
        generations=50,
        elitism_count=2,
        mutation_rate=0.3,
        initial_quality='random'
    )

    elapsed = time.time() - start_time

    print(f"\n{'=' * 80}")
    print("GA RESULTS:")
    print(f"{'=' * 80}")
    print(f"Servers used:            {best_solution.num_servers_used}")
    print(f"Fitness:                 {best_solution.fitness:.2f}")
    print(f"Execution time:          {elapsed:.2f}s")
    print(f"Valid solution:          {best_solution.is_valid()}")

    # Show server utilization
    print(f"\nServer utilization:")
    for i, server_state in enumerate(best_solution.servers):
        if server_state.vms:
            cpu_used = sum(vm.cpu_cores for vm in server_state.vms)
            ram_used = sum(vm.ram_gb for vm in server_state.vms)
            storage_used = sum(vm.storage_gb for vm in server_state.vms)

            cpu_pct = (cpu_used / server.max_cpu_cores) * 100
            ram_pct = (ram_used / server.max_ram_gb) * 100
            storage_pct = (storage_used / server.max_storage_gb) * 100

            print(f"  Server {i}: {len(server_state.vms)} VMs - "
                  f"CPU: {cpu_pct:.1f}%, RAM: {ram_pct:.1f}%, Storage: {storage_pct:.1f}%")


def compare_synthetic_vs_azure():
    """Compare synthetic data vs Azure data characteristics."""
    print("\n" + "=" * 80)
    print("TEST 5: Synthetic vs Azure Data Comparison")
    print("=" * 80)

    # Load both datasets
    synthetic_scenario = DataGenerator.generate_scenario('small', seed=42)
    azure_scenario = DataGenerator.load_azure_scenario('small', seed=42)

    synthetic_vms = synthetic_scenario['vms']
    azure_vms = azure_scenario['vms']

    print(f"\nDataset: SYNTHETIC")
    print(f"{'-' * 80}")
    print_vm_statistics(synthetic_vms)

    print(f"\nDataset: AZURE (Real Data)")
    print(f"{'-' * 80}")
    print_vm_statistics(azure_vms)


def print_vm_statistics(vms):
    """Helper function to print VM statistics."""
    cpu_values = [vm.cpu_cores for vm in vms]
    ram_values = [vm.ram_gb for vm in vms]
    storage_values = [vm.storage_gb for vm in vms]

    print(f"Number of VMs:           {len(vms)}")
    print(f"\nCPU (cores):")
    print(f"  Min:                   {min(cpu_values):.2f}")
    print(f"  Max:                   {max(cpu_values):.2f}")
    print(f"  Average:               {sum(cpu_values)/len(cpu_values):.2f}")
    print(f"  Total:                 {sum(cpu_values):.2f}")

    print(f"\nRAM (GB):")
    print(f"  Min:                   {min(ram_values):.2f}")
    print(f"  Max:                   {max(ram_values):.2f}")
    print(f"  Average:               {sum(ram_values)/len(ram_values):.2f}")
    print(f"  Total:                 {sum(ram_values):.2f}")

    print(f"\nStorage (GB):")
    print(f"  Min:                   {min(storage_values):.2f}")
    print(f"  Max:                   {max(storage_values):.2f}")
    print(f"  Average:               {sum(storage_values)/len(storage_values):.2f}")
    print(f"  Total:                 {sum(storage_values):.2f}")


if __name__ == '__main__':
    print("=" * 80)
    print("AZURE DATA LOADER - VALIDATION TESTS")
    print("=" * 80)

    try:
        test_basic_loading()
        test_scenario_generation()
        test_data_generator_integration()
        test_quick_ga_run()
        compare_synthetic_vs_azure()

        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nYou can now use Azure data in your experiments:")
        print("  from src.utils import DataGenerator")
        print("  scenario = DataGenerator.load_azure_scenario('small', seed=42)")
        print("=" * 80)

    except Exception as e:
        print(f"\n{'=' * 80}")
        print(f"ERROR: {e}")
        print(f"{'=' * 80}")
        import traceback
        traceback.print_exc()
