#!/usr/bin/env python3
"""
Simple convergence capture - runs GA and parses output to extract convergence data.
"""

import json
import re
import sys
from io import StringIO
from contextlib import redirect_stdout

from src.utils.data_generator import DataGenerator
from src.ga.simple_engine import run_simple_ga


def parse_ga_output(output_text):
    """Parse GA console output to extract convergence data."""
    best_fitness = []
    avg_fitness = []
    best_servers = []

    # Pattern: Gen  1: Best=805.37 (8s), Avg=1044.38, Worst=1407.36, Stag=0
    pattern = r'Gen\s+\d+: Best=(\d+\.\d+) \((\d+)s\), Avg=(\d+\.\d+),'

    for line in output_text.split('\n'):
        match = re.search(pattern, line)
        if match:
            best_fitness.append(float(match.group(1)))
            best_servers.append(int(match.group(2)))
            avg_fitness.append(float(match.group(3)))

    return {
        'best_fitness': best_fitness,
        'avg_fitness': avg_fitness,
        'best_servers': best_servers
    }


def run_scenario_with_capture(scenario_name, max_gens, seed=42):
    """Run a scenario and capture convergence data."""
    print(f"\n{'='*70}")
    print(f"Running {scenario_name.upper()} scenario")
    print('='*70)

    # Generate problem
    scenario = DataGenerator.generate_scenario(scenario_name, seed=seed)
    vms = scenario['vms']
    server_template = scenario['server_template']

    print(f"Problem: {len(vms)} VMs")
    print(f"Server: {server_template.max_cpu_cores} cores, "
          f"{server_template.max_ram_gb} GB RAM, "
          f"{server_template.max_storage_gb} GB storage")

    # Capture stdout
    output_buffer = StringIO()

    # Run GA and capture output
    with redirect_stdout(output_buffer):
        best_solution = run_simple_ga(
            vms=vms,
            server_template=server_template,
            population_size=50,
            generations=max_gens,
            elitism_count=2,
            mutation_rate=0.3,
            initial_quality="random"
        )

    # Get the output
    output_text = output_buffer.getvalue()
    print(output_text, end='')  # Print to console too

    # Parse convergence data
    convergence = parse_ga_output(output_text)

    result = {
        'num_vms': len(vms),
        'best_servers': best_solution.num_servers_used,
        'best_fitness': round(best_solution.fitness, 2),
        'convergence': convergence
    }

    print(f"\n✓ Captured {len(convergence['best_fitness'])} generations")
    print(f"  Final: {best_solution.num_servers_used} servers, fitness={best_solution.fitness:.2f}")

    return result


def main():
    """Run experiments and capture convergence data."""
    print("="*70)
    print("CAPTURING CONVERGENCE DATA")
    print("="*70)
    print("\nRunning GA experiments to capture real convergence curves.")
    print("Using current fitness multiplier (100×).")
    print("Takes ~2-3 minutes for 3 scenarios.\n")

    scenarios = [
        ('small', 50),      # scenario, max_generations
        ('medium', 60),
        ('large', 100)
    ]

    all_results = {}

    for scenario_name, max_gens in scenarios:
        result = run_scenario_with_capture(scenario_name, max_gens, seed=42)
        all_results[scenario_name] = result

    # Save to JSON
    output_file = 'convergence_data.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "="*70)
    print("✅ CONVERGENCE DATA CAPTURED")
    print("="*70)
    print(f"\nData saved to: {output_file}")
    print("\nSummary:")
    for scenario, data in all_results.items():
        gens = len(data['convergence']['best_fitness'])
        print(f"  {scenario.capitalize():12} {data['num_vms']:3} VMs: "
              f"{data['best_servers']} servers, fitness={data['best_fitness']}, "
              f"{gens} generations")

    print("\nNext step:")
    print("  python update_convergence_visual.py")
    print()


if __name__ == "__main__":
    main()
