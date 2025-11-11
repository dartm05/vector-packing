"""
Local search improvement for solutions.
Applies hill-climbing to improve solutions found by GA.
"""

import random
from typing import List
from ..models import Solution, VirtualMachine, Server


def local_search_improvement(solution: Solution, max_iterations: int = 10) -> Solution:
    """
    Applies local search to improve a solution.
    Tries to move VMs to better positions or consolidate servers.
    
    Args:
        solution: The solution to improve
        max_iterations: Maximum number of improvement attempts
    
    Returns:
        Improved solution (or original if no improvement found)
    """
    from ..ga.simple_fitness import SimpleFitnessEvaluator
    
    evaluator = SimpleFitnessEvaluator()
    current_solution = solution.clone()
    evaluator.evaluate(current_solution)
    best_fitness = current_solution.fitness
    
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        # Try different improvement strategies
        strategies = [
            _try_consolidate_servers,
            _try_move_to_less_full_server,
            _try_repack_fullest_server
        ]
        
        for strategy in strategies:
            candidate = strategy(current_solution)
            evaluator.evaluate(candidate)
            
            if candidate.fitness < best_fitness:
                current_solution = candidate
                best_fitness = candidate.fitness
                improved = True
                break
    
    return current_solution


def _try_consolidate_servers(solution: Solution) -> Solution:
    """
    Try to move VMs from the least-full server to other servers.
    If successful, reduces server count.
    """
    improved = solution.clone()
    
    # Find servers with VMs, sorted by utilization
    servers_with_vms = [s for s in improved.servers if s.vms]
    if len(servers_with_vms) <= 1:
        return improved
    
    # Try to empty the least utilized server
    servers_with_vms.sort(key=lambda s: len(s.vms))
    source_server = servers_with_vms[0]
    
    # Try to move all VMs from source to other servers
    vms_to_move = list(source_server.vms)
    target_servers = [s for s in servers_with_vms if s.id != source_server.id]
    
    all_moved = True
    for vm in vms_to_move:
        placed = False
        for target in target_servers:
            if target.can_fit(vm):
                source_server.remove_vm(vm)
                target.add_vm(vm)
                placed = True
                break
        
        if not placed:
            all_moved = False
            break
    
    # If we couldn't move all VMs, restore
    if not all_moved:
        return solution.clone()
    
    return improved


def _try_move_to_less_full_server(solution: Solution) -> Solution:
    """
    Try to move VMs from fuller servers to less full servers
    to improve utilization balance.
    """
    improved = solution.clone()
    
    servers_with_vms = [s for s in improved.servers if s.vms]
    if len(servers_with_vms) <= 1:
        return improved
    
    # Sort by utilization (descending)
    servers_with_vms.sort(key=lambda s: s.utilization_cpu, reverse=True)
    
    # Try to move from most full to least full
    source = servers_with_vms[0]
    target = servers_with_vms[-1]
    
    if not source.vms:
        return improved
    
    # Try to move the smallest VM from source to target
    vms_sorted = sorted(source.vms, key=lambda v: v.cpu_cores)
    
    for vm in vms_sorted:
        if target.can_fit(vm):
            source.remove_vm(vm)
            target.add_vm(vm)
            return improved
    
    return solution.clone()


def _try_repack_fullest_server(solution: Solution) -> Solution:
    """
    Try to remove and repack VMs on the fullest server
    in a different order to improve packing.
    """
    improved = solution.clone()
    
    servers_with_vms = [s for s in improved.servers if len(s.vms) > 1]
    if not servers_with_vms:
        return improved
    
    # Find the fullest server
    servers_with_vms.sort(key=lambda s: s.utilization_cpu, reverse=True)
    server = servers_with_vms[0]
    
    # Remove all VMs and try to repack in better order
    vms = list(server.vms)
    for vm in vms:
        server.remove_vm(vm)
    
    # Sort by a different dimension (try to find better packing)
    vms.sort(key=lambda v: v.ram_gb, reverse=True)
    
    for vm in vms:
        if not server.can_fit(vm):
            # If any VM doesn't fit, restore original
            return solution.clone()
        server.add_vm(vm)
    
    return improved
