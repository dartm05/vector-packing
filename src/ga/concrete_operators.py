"""
Concrete implementations of the GA operators defined in operators.py
"""

import random
from typing import List, Tuple
from ..models import Solution, Server
from .operators import SelectionOperator, CrossoverOperator, MutationOperator

#
# --- 1. CONCRETE SELECTION (No change, this is already good) ---
#
class TournamentSelection(SelectionOperator):
    """
    Selects parents using k-way tournament selection.
    """
    def __init__(self, k: int = 3):
        self.k = k

    def select(self, population: List[Solution]) -> Solution:
        """
        Selects a single winner from a k-way tournament.
        """
        tournament_contestants = random.sample(population, self.k)
        winner = min(tournament_contestants, key=lambda sol: sol.fitness)
        return winner

#
# --- 2. CONCRETE CROSSOVER (NEW, REAL LOGIC,UPDATED) ---
#
class VMMapCrossover(CrossoverOperator):
    """
    Performs a crossover by blending the VM-to-Server-ID assignments
    from two parent solutions.
    
    This version is robust and can handle incomplete parents.
    """
    
    def crossover(self, parent1: Solution, parent2: Solution) -> Tuple[Solution, Solution]:
        """
        Creates two children by swapping VM-to-Server-ID assignments.
        """
        
        # 1. Get the VM assignment maps from both parents
        map1 = parent1.get_vm_assignment()
        map2 = parent2.get_vm_assignment()
        
        # --- FIX: Build a "master list" of all VMs from BOTH parents ---
        all_vm_ids_set = set(map1.keys()) | set(map2.keys())
        all_vm_ids = sorted(list(all_vm_ids_set))
        
        if not all_vm_ids:
            # Handle edge case of empty solutions
            return parent1.clone(), parent2.clone()

        # --- FIX: Build a "master dictionary" of all VM objects ---
        all_vms_dict = {}
        for p in [parent1, parent2]:
            for server in p.servers:
                for vm in server.vms:
                    all_vms_dict[vm.id] = vm
        
        # --- FIX: Get a valid server template ---
        template_server = None
        if parent1.servers:
            template_server = parent1.servers[0]
        elif parent2.servers:
            template_server = parent2.servers[0]
        else:
            # Both parents are empty
            return parent1.clone(), parent2.clone()

        server_template = Server(
            id=0,
            max_cpu_cores=template_server.max_cpu_cores,
            max_ram_gb=template_server.max_ram_gb,
            max_storage_gb=template_server.max_storage_gb
        )

        # 2. Pick a random crossover point
        cut_point = random.randint(1, len(all_vm_ids) - 1)
        
        # 3. Create two new child maps by swapping
        child_map1 = {}
        child_map2 = {}
        
        for i, vm_id in enumerate(all_vm_ids):
            # --- FIX: Use .get() to avoid KeyErrors ---
            # .get(vm_id) will return the server_id, or None if the key doesn't exist
            server_id_1 = map1.get(vm_id)
            server_id_2 = map2.get(vm_id)
            
            if i < cut_point:
                child_map1[vm_id] = server_id_1
                child_map2[vm_id] = server_id_2
            else:
                child_map1[vm_id] = server_id_2
                child_map2[vm_id] = server_id_1
        
        # 4. Build the new child solutions
        child1 = self._build_solution_from_map(child_map1, all_vms_dict, server_template)
        child2 = self._build_solution_from_map(child_map2, all_vms_dict, server_template)
        
        return child1, child2

    def _build_solution_from_map(self, vm_map, vms_dict, server_template):
        """
        Helper to build a Solution object from a VM-to-Server-ID map.
        
        This version attempts to place VMs according to the map, but
        "repairs" the solution by placing any VMs that don't fit
        (or are unassigned) into the first available server.
        """
        new_servers_dict = {}
        unplaced_vms = []
        
        for vm_id, server_id in vm_map.items():
            vm = vms_dict.get(vm_id)
            if not vm:
                continue
                
            # If VM was unassigned in the map, add to repair list
            if server_id is None:
                unplaced_vms.append(vm)
                continue
                
            # Get or create the server for this ID
            if server_id not in new_servers_dict:
                new_servers_dict[server_id] = Server(
                    id=server_id,
                    max_cpu_cores=server_template.max_cpu_cores,
                    max_ram_gb=server_template.max_ram_gb,
                    max_storage_gb=server_template.max_storage_gb,
                    name=f"Server-{server_id}"
                )
            
            server = new_servers_dict[server_id]
            
            # --- THIS IS THE FIX ---
            # Try to place the VM. If it fits, great.
            if server.can_fit(vm):
                server.add_vm(vm)
            else:
                # If it doesn't fit, add it to the repair list
                unplaced_vms.append(vm)
        
        
        # --- REPAIR STEP ---
        # Now, try to pack all unplaced VMs using First-Fit
        
        server_list = list(new_servers_dict.values())
        
        for vm in unplaced_vms:
            placed = False
            # 1. Try to fit in an existing server
            for server in server_list:
                if server.can_fit(vm):
                    server.add_vm(vm)
                    placed = True
                    break
            
            # 2. If it still wasn't placed, create a new server
            if not placed:
                new_id = len(server_list)
                new_server = Server(
                    id=new_id,
                    max_cpu_cores=server_template.max_cpu_cores,
                    max_ram_gb=server_template.max_ram_gb,
                    max_storage_gb=server_template.max_storage_gb,
                    name=f"Server-{new_id}"
                )
                
                # We assume the VM can fit in an empty server
                new_server.add_vm(vm)
                server_list.append(new_server)

        return Solution(servers=server_list)

#
# --- 3. CONCRETE MUTATION (NEW, REAL LOGIC) ---
#
class MoveVMMutation(MutationOperator):
    """
    Mutates a solution by randomly moving VMs between servers
    or performing more aggressive mutations.
    """
    def __init__(self, mutation_rate: float = 0.2):
        self.mutation_rate = mutation_rate

    def mutate(self, solution: Solution) -> Solution:
        """
        Mutates a solution based on the mutation rate.
        Performs multiple types of mutations for better exploration.
        """
        
        if random.random() > self.mutation_rate:
            return solution # No mutation
            
        # Clone the solution to avoid modifying the original
        mutated_solution = solution.clone()
        
        # Choose a mutation type with weighted probabilities
        # Favor consolidation (server reduction) mutations
        mutation_type = random.choices(
            ['move', 'swap', 'shuffle', 'consolidate', 'empty_server'],
            weights=[0.25, 0.20, 0.15, 0.30, 0.10],  # 40% server-reducing mutations
            k=1
        )[0]
        
        if mutation_type == 'move':
            # Move a VM from one server to another
            mutated_solution = self._move_vm_mutation(mutated_solution)
        elif mutation_type == 'swap':
            # Swap two VMs between servers
            mutated_solution = self._swap_vms_mutation(mutated_solution)
        elif mutation_type == 'shuffle':
            # Shuffle VMs on a single server (try to repack)
            mutated_solution = self._shuffle_server_mutation(mutated_solution)
        elif mutation_type == 'consolidate':
            # Try to consolidate two servers into one
            mutated_solution = self._consolidate_servers_mutation(mutated_solution)
        else:  # empty_server
            # Try to empty a server by moving all its VMs
            mutated_solution = self._empty_server_mutation(mutated_solution)
        
        return mutated_solution
    
    def _move_vm_mutation(self, solution: Solution) -> Solution:
        """Move a random VM from one server to another."""
        if len(solution.servers) < 2:
            return solution
            
        s1, s2 = random.sample(solution.servers, 2)
        
        if not s1.vms:
            return solution

        vm_to_move = random.choice(s1.vms)
        
        if s2.can_fit(vm_to_move):
            s1.remove_vm(vm_to_move)
            s2.add_vm(vm_to_move)
        
        return solution
    
    def _swap_vms_mutation(self, solution: Solution) -> Solution:
        """Swap two VMs between two servers if both swaps are valid."""
        if len(solution.servers) < 2:
            return solution
        
        servers_with_vms = [s for s in solution.servers if s.vms]
        if len(servers_with_vms) < 2:
            return solution
            
        s1, s2 = random.sample(servers_with_vms, 2)
        
        vm1 = random.choice(s1.vms)
        vm2 = random.choice(s2.vms)
        
        # Check if swap is feasible
        s1.remove_vm(vm1)
        s2.remove_vm(vm2)
        
        can_swap = s1.can_fit(vm2) and s2.can_fit(vm1)
        
        if can_swap:
            s1.add_vm(vm2)
            s2.add_vm(vm1)
        else:
            # Restore original state
            s1.add_vm(vm1)
            s2.add_vm(vm2)
        
        return solution
    
    def _shuffle_server_mutation(self, solution: Solution) -> Solution:
        """Remove all VMs from a server and re-add them in random order."""
        servers_with_vms = [s for s in solution.servers if len(s.vms) > 1]
        if not servers_with_vms:
            return solution
        
        server = random.choice(servers_with_vms)
        vms = list(server.vms)
        
        # Clear the server
        for vm in vms:
            server.remove_vm(vm)
        
        # Re-add in random order
        random.shuffle(vms)
        for vm in vms:
            server.add_vm(vm)
        
        return solution
    
    def _consolidate_servers_mutation(self, solution: Solution) -> Solution:
        """
        Try to consolidate two servers by moving all VMs from one to the other.
        This directly targets reducing server count.
        """
        if len(solution.servers) < 2:
            return solution
        
        # Sort servers by VM count (try to empty smaller servers first)
        sorted_servers = sorted(solution.servers, key=lambda s: len(s.vms))
        
        # Try to consolidate a small server into a larger one
        for source_server in sorted_servers[:3]:  # Try 3 smallest
            if not source_server.vms:
                continue
            
            # Find target servers that might have capacity
            potential_targets = [s for s in solution.servers if s != source_server]
            random.shuffle(potential_targets)
            
            for target_server in potential_targets[:5]:  # Try up to 5 targets
                # Try to move all VMs from source to target
                vms_to_move = list(source_server.vms)
                success = True
                
                for vm in vms_to_move:
                    if target_server.can_fit(vm):
                        source_server.remove_vm(vm)
                        target_server.add_vm(vm)
                    else:
                        success = False
                        break
                
                if success:
                    # Successfully consolidated!
                    return solution
                else:
                    # Revert moves
                    for vm in vms_to_move:
                        if vm in target_server.vms:
                            target_server.remove_vm(vm)
                            source_server.add_vm(vm)
        
        return solution
    
    def _empty_server_mutation(self, solution: Solution) -> Solution:
        """
        Try to empty a server by distributing its VMs to other servers.
        """
        servers_with_vms = [s for s in solution.servers if s.vms]
        if len(servers_with_vms) < 2:
            return solution
        
        # Pick a random server to empty (favor smaller ones)
        sorted_servers = sorted(servers_with_vms, key=lambda s: len(s.vms))
        source_server = random.choice(sorted_servers[:max(1, len(sorted_servers)//2)])
        
        vms_to_relocate = list(source_server.vms)
        other_servers = [s for s in solution.servers if s != source_server]
        
        for vm in vms_to_relocate:
            # Try to find a server that can fit this VM
            random.shuffle(other_servers)
            for target_server in other_servers:
                if target_server.can_fit(vm):
                    source_server.remove_vm(vm)
                    target_server.add_vm(vm)
                    break
        
        return solution