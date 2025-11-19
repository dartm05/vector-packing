"""
Simplified GA Engine for debugging and better convergence.
This version focuses on clarity and effective operators.
"""

import random
from typing import List
from ..models import VirtualMachine, Server, Solution


def calculate_fitness(solution: Solution) -> float:
    """
    Simplified fitness function with better granularity.

    Goal: Minimize servers, then maximize utilization
    Uses a more gradual scale to allow improvements
    """
    if not solution.is_valid():
        return 10000.0

    num_servers = solution.num_servers_used

    if num_servers == 0:
        return 0.0

    # Primary: server count (weighted but not overwhelming)
    server_cost = num_servers * 10.0

    # Secondary: utilization (inverted - higher util = lower cost)
    utils = solution.average_utilization
    avg_util = (utils['cpu'] + utils['ram'] + utils['storage']) / 3.0

    # Penalize low utilization (scaled to be comparable to server differences)
    utilization_cost = (100.0 - avg_util) / 10.0  # Range: 0-10

    total_fitness = server_cost + utilization_cost
    solution.fitness = total_fitness

    return total_fitness


def first_fit_solution(vms: List[VirtualMachine], server_template: Server) -> Solution:
    """Create a solution using first-fit heuristic."""
    servers = []

    for vm in vms:
        placed = False
        for server in servers:
            if server.can_fit(vm):
                server.add_vm(vm)
                placed = True
                break

        if not placed:
            new_server = Server(
                id=len(servers),
                max_cpu_cores=server_template.max_cpu_cores,
                max_ram_gb=server_template.max_ram_gb,
                max_storage_gb=server_template.max_storage_gb,
                name=f"Server-{len(servers)}"
            )
            new_server.add_vm(vm)
            servers.append(new_server)

    return Solution(servers=servers)


def worst_fit_solution(vms: List[VirtualMachine], server_template: Server) -> Solution:
    """Create a deliberately inefficient solution using worst-fit."""
    servers = []

    for vm in vms:
        # Try to place in the server with MOST space (worst fit)
        worst_server = None
        max_available = -1

        for server in servers:
            if server.can_fit(vm):
                available = server.available_cpu + server.available_ram/10
                if available > max_available:
                    max_available = available
                    worst_server = server

        if worst_server:
            worst_server.add_vm(vm)
        else:
            # Create new server
            new_server = Server(
                id=len(servers),
                max_cpu_cores=server_template.max_cpu_cores,
                max_ram_gb=server_template.max_ram_gb,
                max_storage_gb=server_template.max_storage_gb,
                name=f"Server-{len(servers)}"
            )
            new_server.add_vm(vm)
            servers.append(new_server)

    return Solution(servers=servers)


def random_placement_solution(vms: List[VirtualMachine], server_template: Server) -> Solution:
    """Create a solution with completely random VM placement (no heuristics)."""
    servers = []
    shuffled_vms = list(vms)
    random.shuffle(shuffled_vms)

    # Create way more servers than needed
    num_servers = len(vms) // 2 + random.randint(1, len(vms) // 3)
    for i in range(num_servers):
        servers.append(Server(
            id=i,
            max_cpu_cores=server_template.max_cpu_cores,
            max_ram_gb=server_template.max_ram_gb,
            max_storage_gb=server_template.max_storage_gb,
            name=f"Server-{i}"
        ))

    # Place VMs randomly
    for vm in shuffled_vms:
        placed = False
        attempts = 0
        while not placed and attempts < len(servers):
            server_idx = random.randint(0, len(servers) - 1)
            if servers[server_idx].can_fit(vm):
                servers[server_idx].add_vm(vm)
                placed = True
            attempts += 1

        # If couldn't place, create new server
        if not placed:
            new_server = Server(
                id=len(servers),
                max_cpu_cores=server_template.max_cpu_cores,
                max_ram_gb=server_template.max_ram_gb,
                max_storage_gb=server_template.max_storage_gb,
                name=f"Server-{len(servers)}"
            )
            new_server.add_vm(vm)
            servers.append(new_server)

    return Solution(servers=servers)


def create_initial_population(vms: List[VirtualMachine],
                              server_template: Server,
                              size: int,
                              quality: str = "mixed") -> List[Solution]:
    """
    Create initial population with diversity.

    Args:
        quality: 'good' for optimal heuristics, 'poor' for inefficient,
                'mixed' for combination (default), 'random' for no heuristics
    """
    population = []

    for i in range(size):
        shuffled_vms = list(vms)

        # Determine strategy based on quality setting
        if quality == "random":
            # Completely random placement - no heuristics at all
            solution = random_placement_solution(shuffled_vms, server_template)

        elif quality == "poor":
            # Use worse strategies more often
            if i % 3 == 0:
                random.shuffle(shuffled_vms)
                solution = worst_fit_solution(shuffled_vms, server_template)
            elif i % 3 == 1:
                shuffled_vms.sort(key=lambda v: v.cpu_cores)  # ascending (worse)
                solution = first_fit_solution(shuffled_vms, server_template)
            else:
                random.shuffle(shuffled_vms)
                solution = first_fit_solution(shuffled_vms, server_template)

        elif quality == "good":
            # Use better strategies
            if i % 4 == 0:
                shuffled_vms.sort(key=lambda v: v.cpu_cores, reverse=True)
            elif i % 4 == 1:
                shuffled_vms.sort(key=lambda v: v.ram_gb, reverse=True)
            elif i % 4 == 2:
                shuffled_vms.sort(key=lambda v: v.storage_gb, reverse=True)
            else:
                random.shuffle(shuffled_vms)
            solution = first_fit_solution(shuffled_vms, server_template)

        else:  # mixed
            # Use mix of strategies
            if i % 5 == 0:
                random.shuffle(shuffled_vms)
                solution = worst_fit_solution(shuffled_vms, server_template)
            elif i % 5 == 1:
                shuffled_vms.sort(key=lambda v: v.cpu_cores, reverse=True)
                solution = first_fit_solution(shuffled_vms, server_template)
            elif i % 5 == 2:
                shuffled_vms.sort(key=lambda v: v.ram_gb, reverse=True)
                solution = first_fit_solution(shuffled_vms, server_template)
            elif i % 5 == 3:
                shuffled_vms.sort(key=lambda v: v.cpu_cores)  # ascending (worse)
                solution = first_fit_solution(shuffled_vms, server_template)
            else:
                random.shuffle(shuffled_vms)
                solution = first_fit_solution(shuffled_vms, server_template)

        solution.generation = 0
        population.append(solution)

    return population


def tournament_selection(population: List[Solution], k: int = 3) -> Solution:
    """Select a solution using tournament selection."""
    tournament = random.sample(population, k)
    return min(tournament, key=lambda s: s.fitness)


def simple_crossover(parent1: Solution, parent2: Solution) -> Solution:
    """
    Simple crossover: take VM assignments from both parents.
    Ensures ALL VMs are included in the child.
    """
    # Get VM assignments
    map1 = parent1.get_vm_assignment()
    map2 = parent2.get_vm_assignment()

    # Get all VMs
    all_vm_ids = sorted(set(map1.keys()) | set(map2.keys()))

    if not all_vm_ids or not parent1.servers:
        return parent1.clone()

    # Collect all VMs (CRITICAL: ensure we have all VMs)
    all_vms = {}
    for server in parent1.servers + parent2.servers:
        for vm in server.vms:
            all_vms[vm.id] = vm

    # Get server template
    template = parent1.servers[0]

    # Create child by randomly choosing from parent assignments
    child_servers = {}
    unplaced_vms = []  # Track VMs that couldn't be placed

    for vm_id in all_vm_ids:
        vm = all_vms.get(vm_id)
        if not vm:
            continue

        # Get server IDs from both parents
        server_id_1 = map1.get(vm_id)
        server_id_2 = map2.get(vm_id)

        # Filter out None values
        valid_options = [s for s in [server_id_1, server_id_2] if s is not None]

        if not valid_options:
            # Neither parent has this VM (shouldn't happen, but handle it)
            unplaced_vms.append(vm)
            continue

        # Randomly choose assignment from valid options
        server_id = random.choice(valid_options)

        # Create server if needed
        if server_id not in child_servers:
            child_servers[server_id] = Server(
                id=server_id,
                max_cpu_cores=template.max_cpu_cores,
                max_ram_gb=template.max_ram_gb,
                max_storage_gb=template.max_storage_gb,
                name=f"Server-{server_id}"
            )

        server = child_servers[server_id]

        # Try to add, if it doesn't fit we'll repair later
        if not server.can_fit(vm):
            unplaced_vms.append(vm)
        else:
            server.add_vm(vm)

    # REPAIR: Place any unplaced VMs
    server_list = list(child_servers.values())
    for vm in unplaced_vms:
        placed = False
        # Try existing servers first
        for server in server_list:
            if server.can_fit(vm):
                server.add_vm(vm)
                placed = True
                break

        # Create new server if needed
        if not placed:
            new_id = max([s.id for s in server_list], default=-1) + 1
            new_server = Server(
                id=new_id,
                max_cpu_cores=template.max_cpu_cores,
                max_ram_gb=template.max_ram_gb,
                max_storage_gb=template.max_storage_gb,
                name=f"Server-{new_id}"
            )
            new_server.add_vm(vm)
            server_list.append(new_server)

    child = Solution(servers=server_list)

    # VALIDATION: Ensure all VMs are present
    if child.total_vms != len(all_vm_ids):
        # Fallback: if we still lost VMs, return a clone of parent1
        return parent1.clone()

    return child


def consolidation_mutation(solution: Solution) -> Solution:
    """
    Aggressive mutation that tries to empty a server and reduce server count.
    """
    mutated = solution.clone()

    servers_with_vms = [s for s in mutated.servers if s.vms]
    if len(servers_with_vms) < 2:
        return mutated

    # Sort by VM count (try to empty smallest servers)
    servers_with_vms.sort(key=lambda s: len(s.vms))

    # Try to empty the smallest server
    source = servers_with_vms[0]
    other_servers = [s for s in mutated.servers if s != source]

    # Try to redistribute all VMs from source to other servers
    vms_to_move = list(source.vms)

    for vm in vms_to_move:
        # Find best fit server
        best_server = None
        min_remaining = float('inf')

        for target in other_servers:
            if target.can_fit(vm):
                # Calculate remaining capacity
                remaining = (target.available_cpu - vm.cpu_cores +
                           (target.available_ram - vm.ram_gb) / 10 +
                           (target.available_storage - vm.storage_gb) / 100)

                if remaining < min_remaining:
                    min_remaining = remaining
                    best_server = target

        if best_server:
            source.remove_vm(vm)
            best_server.add_vm(vm)

    return mutated


def simple_mutation(solution: Solution, mutation_rate: float = 0.3) -> Solution:
    """
    Mixed mutation: sometimes do simple moves, sometimes try consolidation.
    Ensures no VMs are lost during mutation.
    """
    if random.random() > mutation_rate:
        return solution

    original_vm_count = solution.total_vms
    mutated = solution.clone()

    if len(mutated.servers) < 2:
        return mutated

    # 60% chance of consolidation mutation (aggressive server reduction)
    # 40% chance of simple mutation (gradual improvement)
    if random.random() < 0.6:
        mutated = consolidation_mutation(mutated)
    else:
        # Try to move 1-3 VMs
        num_moves = random.randint(1, 3)

        for _ in range(num_moves):
            # Pick two random servers
            servers_with_vms = [s for s in mutated.servers if s.vms]
            if len(servers_with_vms) < 2:
                break

            source = random.choice(servers_with_vms)
            target = random.choice([s for s in mutated.servers if s != source])

            if not source.vms:
                continue

            # Pick a random VM to move
            vm = random.choice(list(source.vms))

            # Try to move it
            if target.can_fit(vm):
                source.remove_vm(vm)
                target.add_vm(vm)

    # VALIDATION: Ensure no VMs were lost
    if mutated.total_vms != original_vm_count:
        # If VMs were lost, return the original
        return solution

    return mutated


def run_simple_ga(vms: List[VirtualMachine],
                 server_template: Server,
                 population_size: int = 30,
                 generations: int = 50,
                 elitism_count: int = 1,
                 mutation_rate: float = 0.3,
                 initial_quality: str = "poor"):
    """
    Simplified GA with clear logic and better debugging.

    Args:
        initial_quality: 'good', 'poor', 'mixed', or 'random' for initial population quality
    """
    print("\n--- Simple GA Starting ---")
    print(f"Problem: {len(vms)} VMs, {population_size} population, {generations} generations")
    print(f"Initial population quality: {initial_quality}\n")

    # Create initial population
    population = create_initial_population(vms, server_template, population_size, quality=initial_quality)

    # Evaluate initial population
    for sol in population:
        calculate_fitness(sol)

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

        # Early stopping (only after many generations of stagnation)
        if stagnation >= 40:
            print(f"\nStopping early after {stagnation} generations without improvement")
            break

        # Create next generation
        new_population = []

        # Elitism
        for i in range(elitism_count):
            elite = population[i].clone()
            elite.generation = gen + 1
            new_population.append(elite)

        # Adaptive mutation rate - increase when stagnating
        current_mutation_rate = mutation_rate
        if stagnation > 10:
            current_mutation_rate = min(0.7, mutation_rate * (1 + stagnation / 20))

        # Crossover and mutation
        while len(new_population) < population_size:
            parent1 = tournament_selection(population, k=3)
            parent2 = tournament_selection(population, k=3)

            child = simple_crossover(parent1, parent2)
            child = simple_mutation(child, current_mutation_rate)

            child.generation = gen + 1
            calculate_fitness(child)

            new_population.append(child)

        population = new_population

    # Final evaluation
    for sol in population:
        calculate_fitness(sol)

    population.sort(key=lambda s: s.fitness)
    best_solution = population[0]

    print("\n--- Simple GA Finished ---")
    print(f"Best solution: {best_solution.num_servers_used} servers")
    print(f"Best fitness: {best_solution.fitness:.4f}")
    print(f"Valid: {best_solution.is_valid()}")

    utils = best_solution.average_utilization
    print(f"Utilization: CPU={utils['cpu']:.1f}%, RAM={utils['ram']:.1f}%, Storage={utils['storage']:.1f}%")

    return best_solution
