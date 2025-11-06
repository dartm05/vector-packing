"""
The main Genetic Algorithm (GA) Engine.

This module contains the logic for running the evolutionary process,
including population initialization and the main GA loop.
"""

import random
from typing import List
from ..models import VirtualMachine, Server, Solution

# --- GA Imports ---
from .simple_fitness import SimpleFitnessEvaluator, INVALID_PENALTY
from .concrete_operators import TournamentSelection, VMMapCrossover, MoveVMMutation
from .advanced_selection import RankSelection
from .local_search import local_search_improvement

# --- Utility Imports ---
from ..utils.data_generator import DataGenerator

def _create_solution_first_fit(vms: List[VirtualMachine], server_template: Server) -> Solution:
    """
    Creates a single solution using a simple First-Fit heuristic.
    (Helper function for initialization)
    """
    servers = [] 
    server_pool = [] 

    for vm in vms:
        placed = False
        # 1. Try to place in an existing server
        for server in server_pool:
            if server.add_vm(vm):
                placed = True
                break
        
        # 2. If it couldn't be placed, create a new server
        if not placed:
            new_server = Server(
                id=len(server_pool), 
                max_cpu_cores=server_template.max_cpu_cores,
                max_ram_gb=server_template.max_ram_gb,
                max_storage_gb=server_template.max_storage_gb,
                name=f"Server-{len(server_pool)}"
            )
            
            if new_server.add_vm(vm):
                server_pool.append(new_server)
            else:
                print(f"Warning: VM {vm.id} could not be placed in a new server.")

    return Solution(servers=server_pool)


def create_initial_population(vms: List[VirtualMachine], 
                              server_template: Server, 
                              size: int) -> List[Solution]:
    """
    Creates the initial population (Generation 0) for the GA.
    Uses different strategies to ensure diversity.
    """
    population = []
    vms_to_pack = list(vms)
    
    strategies = ['random', 'largest_first', 'smallest_first', 'balanced']
    
    for i in range(size):
        # Use different sorting strategies for diversity
        strategy = strategies[i % len(strategies)]
        
        if strategy == 'random':
            random.shuffle(vms_to_pack)
        elif strategy == 'largest_first':
            # Sort by total resource demand (descending)
            vms_to_pack.sort(key=lambda v: v.cpu_cores + v.ram_gb/10 + v.storage_gb/100, reverse=True)
        elif strategy == 'smallest_first':
            # Sort by total resource demand (ascending)
            vms_to_pack.sort(key=lambda v: v.cpu_cores + v.ram_gb/10 + v.storage_gb/100)
        else:  # balanced
            # Sort by a random resource dimension
            dimension = random.choice(['cpu', 'ram', 'storage'])
            if dimension == 'cpu':
                vms_to_pack.sort(key=lambda v: v.cpu_cores, reverse=random.choice([True, False]))
            elif dimension == 'ram':
                vms_to_pack.sort(key=lambda v: v.ram_gb, reverse=random.choice([True, False]))
            else:
                vms_to_pack.sort(key=lambda v: v.storage_gb, reverse=random.choice([True, False]))
        
        solution = _create_solution_first_fit(vms_to_pack, server_template)
        solution.generation = 0
        population.append(solution)
        
    return population

#
# --- THIS IS THE MISSING run_ga FUNCTION ---
#
def run_ga(vms: List[VirtualMachine], 
           server_template: Server, 
           population_size: int, 
           generations: int,
           elitism_count: int = 2,
           mutation_rate: float = 0.3,
           tournament_k: int = 3,
           use_local_search: bool = False) -> Solution:
    """
    Runs the full Genetic Algorithm using operator classes.
    """
    
    print("--- 🧬 Starting Genetic Algorithm (Object-Oriented) ---")
    
    # 1. Initialize Operators and Evaluator
    evaluator = SimpleFitnessEvaluator()
    
    # Use multiple selection strategies for diversity
    tournament_selection = TournamentSelection(k=tournament_k)
    rank_selection = RankSelection(selection_pressure=1.5)
    
    crossover_op = VMMapCrossover()
    
    # Start with higher mutation rate, decrease over time
    base_mutation_rate = mutation_rate
    mutation_op = MoveVMMutation(mutation_rate=base_mutation_rate)
    
    # 2. Create Initial Population (Generation 0)
    print(f"Creating initial population (size={population_size})...")
    population = create_initial_population(vms, server_template, population_size)
    
    # 3. Run Evolutionary Loop
    best_ever_fitness = float('inf')
    stagnation_counter = 0
    
    for gen in range(generations):
        
        # 3a. Evaluate Population
        for sol in population:
            evaluator.evaluate(sol) # Fitness is set on sol.fitness
            
        population.sort(key=lambda sol: sol.fitness)
        
        best_fitness = population[0].fitness
        best_servers = population[0].num_servers_used
        worst_fitness = population[-1].fitness
        
        # Track improvement for early stopping
        if best_fitness < best_ever_fitness:
            best_ever_fitness = best_fitness
            stagnation_counter = 0
        else:
            stagnation_counter += 1
        
        # Adaptive mutation rate - increase when stagnating
        if stagnation_counter > 10:
            current_mutation_rate = min(0.5, base_mutation_rate * (1 + stagnation_counter / 20))
            mutation_op.mutation_rate = current_mutation_rate
        else:
            mutation_op.mutation_rate = base_mutation_rate
            
        print(f"Generation {gen+1}/{generations}: Best={best_fitness:.2f} ({best_servers} servers), "
              f"Worst={worst_fitness:.2f}, Stagnation={stagnation_counter}, MutRate={mutation_op.mutation_rate:.2f}")

        # Early stopping if no improvement for too long
        if stagnation_counter >= 30:
            print(f"Stopping early - no improvement for {stagnation_counter} generations")
            break

        # 3b. Create Next Generation
        new_population = []
        
        # Elitism: The best solutions survive unchanged
        for i in range(elitism_count):
            elite = population[i].clone()
            elite.generation = gen + 1
            new_population.append(elite)
            
        # 3c. Crossover & Mutation Loop
        while len(new_population) < population_size:
            # Alternate between selection strategies for diversity
            if random.random() < 0.7:
                parent1 = tournament_selection.select(population)
                parent2 = tournament_selection.select(population)
            else:
                parent1 = rank_selection.select(population)
                parent2 = rank_selection.select(population)
            
            # Crossover
            child1, child2 = crossover_op.crossover(parent1, parent2)
            
            # Mutation
            child1 = mutation_op.mutate(child1)
            child2 = mutation_op.mutate(child2)
            
            # Set generation
            child1.generation = gen + 1
            child2.generation = gen + 1
            
            # Optional: Apply local search to children
            if use_local_search and random.random() < 0.2:  # 20% chance
                child1 = local_search_improvement(child1, max_iterations=5)
            if use_local_search and random.random() < 0.2:
                child2 = local_search_improvement(child2, max_iterations=5)
            
            # Add both children (if space allows)
            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)
        
        # *** CRITICAL FIX: Update population with new generation ***
        population = new_population
        
        # Optional: Apply local search to best solutions periodically
        if use_local_search and (gen + 1) % 10 == 0:
            for i in range(min(3, len(population))):
                population[i] = local_search_improvement(population[i], max_iterations=10)

    # 4. Return Best Solution
    for sol in population:
        evaluator.evaluate(sol)
    population.sort(key=lambda sol: sol.fitness)
    
    best_solution = population[0]
    
    print("--- 🏁 GA Finished ---")
    print(f"Best solution found: {best_solution.num_servers_used} servers")
    print(f"Best fitness: {best_solution.fitness:.4f}")
    
    return best_solution
# -----------------------------------------------------------------
#  TESTING BLOCK: Run this file directly to test its functions
# -----------------------------------------------------------------
if __name__ == "__main__":
    print("--- Testing GA Engine (Object-Oriented) ---")
    
    # 1. --- Test Data Generation ---
    print("1. Generating 'small' test scenario...")
    scenario = DataGenerator.generate_scenario("small", seed=42)
    vms = scenario['vms']
    server_template = scenario['server_template']
    print(f"   -> Created {len(vms)} VMs and 1 server template.")

    # 2. --- Test the full run_ga loop ---
    print("\n2. Testing run_ga() (with concrete operators)...")
    
    # Use small numbers for a quick test
    best_solution = run_ga(
        vms=vms,
        server_template=server_template,
        population_size=10,  # Small population
        generations=5,       # Only 5 generations
        elitism_count=1,
        mutation_rate=0.1,
        tournament_k=3
    )
    
    print("\n--- Test Run Complete ---")
    print(f"Final best solution is valid: {best_solution.is_valid()}")
    print(f"Final servers used: {best_solution.num_servers_used}")
    
    if best_solution.is_valid() and best_solution.fitness < INVALID_PENALTY:
        print("   -> SUCCESS: GA loop ran and produced a valid solution.")
    else:
        print("   -> FAILURE: GA loop produced an invalid or non-optimal solution.")