#!/usr/bin/env python3
"""
Capture real convergence data by running experiments with the current fitness multiplier.
"""

import json
from src.utils.data_generator import DataGenerator
from src.ga.simple_engine import create_initial_population, calculate_fitness
from src.models import Solution
import random
from typing import List

def run_ga_with_tracking(vms, server_template, population_size=50, generations=100,
                         elitism_count=2, mutation_rate=0.3, initial_quality="random"):
    """
    Run GA and track convergence data.
    """
    from src.ga.simple_engine import (
        tournament_selection, crossover, mutate_solution,
        consolidate_servers_mutation, simple_move_mutation,
        validate_and_fix_solution
    )

    print(f"\n--- Tracking GA Convergence ---")
    print(f"Problem: {len(vms)} VMs, {population_size} population, {generations} generations")
    print(f"Initial population quality: {initial_quality}\n")

    # Create initial population
    population = create_initial_population(vms, server_template, population_size, quality=initial_quality)

    # Evaluate initial population
    for sol in population:
        calculate_fitness(sol)

    # Track convergence data
    convergence_history = {
        'best_fitness': [],
        'avg_fitness': [],
        'worst_fitness': [],
        'best_servers': [],
        'avg_servers': []
    }

    best_ever_fitness = float('inf')
    best_ever_servers = float('inf')
    stagnation = 0

    for gen in range(generations):
        # Sort by fitness
        population.sort(key=lambda s: s.fitness)

        best_fitness = population[0].fitness
        best_servers = population[0].num_servers_used
        worst_fitness = population[-1].fitness
        avg_fitness = sum(s.fitness for s in population) / len(population)
        avg_servers = sum(s.num_servers_used for s in population) / len(population)

        # Store convergence data
        convergence_history['best_fitness'].append(round(best_fitness, 2))
        convergence_history['avg_fitness'].append(round(avg_fitness, 2))
        convergence_history['worst_fitness'].append(round(worst_fitness, 2))
        convergence_history['best_servers'].append(best_servers)
        convergence_history['avg_servers'].append(round(avg_servers, 1))

        # Track improvements
        improved = False
        if best_servers < best_ever_servers:
            best_ever_servers = best_servers
            improved = True
            stagnation = 0
            print(f"  *** NEW BEST: {best_servers} servers! ***")
        elif best_fitness < best_ever_fitness:
            best_ever_fitness = best_fitness
            improved = True
            stagnation = 0
        else:
            stagnation += 1

        # Print progress
        print(f"Gen {gen+1:3d}: Best={best_fitness:6.2f} ({best_servers}s), "
              f"Avg={avg_fitness:6.2f}, Worst={worst_fitness:6.2f}, "
              f"Stag={stagnation}")

        # Early stopping
        if stagnation >= 40:
            print(f"\nStopping early after {stagnation} generations without improvement\n")
            break

        # Evolution
        new_population = []

        # Elitism
        for i in range(elitism_count):
            new_population.append(population[i].clone())

        # Generate offspring
        while len(new_population) < population_size:
            parent1 = tournament_selection(population, k=3)
            parent2 = tournament_selection(population, k=3)

            child = crossover(parent1, parent2, server_template)

            # Mutation
            if random.random() < mutation_rate:
                if random.random() < 0.6:  # 60% consolidation
                    child = consolidate_servers_mutation(child, server_template)
                else:
                    child = simple_move_mutation(child, server_template)

            child = validate_and_fix_solution(child, list(vms), server_template)
            calculate_fitness(child)
            new_population.append(child)

        population = new_population

    # Return best solution and convergence history
    population.sort(key=lambda s: s.fitness)
    return population[0], convergence_history


def main():
    """Run experiments on small, medium, and large scenarios."""

    print("=" * 70)
    print("CAPTURING CONVERGENCE DATA")
    print("=" * 70)
    print("\nThis will run GA experiments to capture real convergence curves.")
    print("Takes ~2-3 minutes for 3 scenarios.\n")

    scenarios_to_run = [
        ('small', 20, 50),     # scenario, expected_gens to converge, generations to run
        ('medium', 20, 60),
        ('large', 50, 100)
    ]

    all_results = {}

    for scenario_name, _, max_gens in scenarios_to_run:
        print("\n" + "=" * 70)
        print(f"Running {scenario_name.upper()} scenario")
        print("=" * 70)

        # Generate problem
        scenario = DataGenerator.generate_scenario(scenario_name, seed=42)
        vms = scenario['vms']
        server_template = scenario['server_template']

        print(f"Problem: {len(vms)} VMs")
        print(f"Server: {server_template.max_cpu_cores} cores, "
              f"{server_template.max_ram_gb} GB RAM, "
              f"{server_template.max_storage_gb} GB storage\n")

        # Run GA with tracking
        best_solution, convergence = run_ga_with_tracking(
            vms=vms,
            server_template=server_template,
            population_size=50,
            generations=max_gens,
            elitism_count=2,
            mutation_rate=0.3,
            initial_quality="random"
        )

        # Store results
        all_results[scenario_name] = {
            'num_vms': len(vms),
            'best_servers': best_solution.num_servers_used,
            'best_fitness': round(best_solution.fitness, 2),
            'convergence': convergence
        }

        print(f"\n✓ {scenario_name.capitalize()}: {best_solution.num_servers_used} servers, "
              f"fitness={best_solution.fitness:.2f}")

    # Save to JSON
    output_file = 'results/convergence/convergence_data.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "=" * 70)
    print("✅ CONVERGENCE DATA CAPTURED")
    print("=" * 70)
    print(f"\nData saved to: {output_file}")
    print("\nNext step:")
    print("  python presentation/scripts/update_convergence_visual.py")
    print("\nThis will update vis_11_convergence_curves.html with the new data.")
    print()


if __name__ == "__main__":
    main()
