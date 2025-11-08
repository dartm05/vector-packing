"""
Crowd Builder - Constructs new solutions using crowd wisdom

This module uses patterns discovered by the CrowdAnalyzer to build
new solutions that leverage successful VM groupings.
"""

import random
from typing import List, Set
from ..models import VirtualMachine, Server, Solution
from .crowd_analyzer import CrowdAnalyzer


class CrowdBuilder:
    """
    Builds new solutions using wisdom extracted from successful solutions.
    
    Uses affinity patterns to group VMs together that have historically
    worked well in combination.
    """
    
    def __init__(self, analyzer: CrowdAnalyzer):
        """
        Initialize the builder with a crowd analyzer.
        
        Args:
            analyzer: CrowdAnalyzer containing learned VM affinity patterns
        """
        self.analyzer = analyzer
    
    def build_solution(self, vms: List[VirtualMachine], server_template: Server, 
                      affinity_weight: float = 0.7) -> Solution:
        """
        Build a new solution using crowd wisdom with affinity-guided packing.
        
        Args:
            vms: List of VMs to pack
            server_template: Template server with capacity constraints
            affinity_weight: Weight for affinity vs random (0.0 to 1.0)
                           Higher values = more reliance on learned patterns
        
        Returns:
            A new Solution with VMs packed using crowd wisdom
        """
        # Create copies of VMs to avoid modifying originals
        remaining_vms = list(vms)
        random.shuffle(remaining_vms)  # Add some randomness
        
        solution = Solution(servers=[], generation=0, metadata={'method': 'crowd_wisdom'})
        
        while remaining_vms:
            # Create a new server
            server = Server(
                id=len(solution.servers),
                max_cpu_cores=server_template.max_cpu_cores,
                max_ram_gb=server_template.max_ram_gb,
                max_storage_gb=server_template.max_storage_gb,
                name=f"Server-{len(solution.servers)}"
            )
            
            # Try to fill this server using affinity guidance
            self._fill_server_with_affinity(server, remaining_vms, affinity_weight)
            
            if len(server.vms) > 0:
                solution.servers.append(server)
            else:
                # If we couldn't place anything, force place the first VM
                if remaining_vms:
                    vm = remaining_vms.pop(0)
                    if server.add_vm(vm):
                        solution.servers.append(server)
                break
        
        return solution
    
    def _fill_server_with_affinity(self, server: Server, remaining_vms: List[VirtualMachine], 
                                   affinity_weight: float) -> None:
        """
        Fill a server by selecting VMs based on affinity to already-placed VMs.
        
        Args:
            server: The server to fill
            remaining_vms: List of VMs still to be placed (modified in-place)
            affinity_weight: Weight for affinity-based selection
        """
        placed_vm_ids: Set[int] = set()
        
        while remaining_vms:
            if not placed_vm_ids:
                # First VM: pick randomly from remaining
                vm = remaining_vms.pop(0)
                if server.add_vm(vm):
                    placed_vm_ids.add(vm.id)
                else:
                    # Can't fit even the first VM, put it back and stop
                    remaining_vms.insert(0, vm)
                    break
            else:
                # Subsequent VMs: use affinity guidance
                vm_idx = self._select_next_vm_with_affinity(
                    placed_vm_ids, remaining_vms, affinity_weight
                )
                
                if vm_idx is None:
                    break  # No more VMs can fit
                
                vm = remaining_vms.pop(vm_idx)
                if server.add_vm(vm):
                    placed_vm_ids.add(vm.id)
                else:
                    # Couldn't fit, put it back
                    remaining_vms.insert(vm_idx, vm)
                    # Try other VMs (maybe we can find a smaller one)
                    found_fit = False
                    for i, candidate_vm in enumerate(remaining_vms[:]):
                        if server.add_vm(candidate_vm):
                            placed_vm_ids.add(candidate_vm.id)
                            remaining_vms.pop(i)
                            found_fit = True
                            break
                    
                    if not found_fit:
                        break  # Server is full
    
    def _select_next_vm_with_affinity(self, placed_vm_ids: Set[int], 
                                      remaining_vms: List[VirtualMachine],
                                      affinity_weight: float) -> int:
        """
        Select the next VM to try placing, guided by affinity to already-placed VMs.
        
        Args:
            placed_vm_ids: IDs of VMs already placed on current server
            remaining_vms: List of VMs still available
            affinity_weight: Probability of using affinity vs random selection
        
        Returns:
            Index of selected VM in remaining_vms list, or None if list is empty
        """
        if not remaining_vms:
            return None
        
        # Decide whether to use affinity or random selection
        if random.random() > affinity_weight or self.analyzer.solutions_analyzed == 0:
            # Random selection (exploration)
            return random.randint(0, len(remaining_vms) - 1)
        
        # Affinity-based selection (exploitation)
        remaining_vm_ids = [vm.id for vm in remaining_vms]
        
        # Calculate average affinity of each remaining VM to all placed VMs
        best_idx = 0
        best_score = -1.0
        
        for idx, vm in enumerate(remaining_vms):
            # Calculate average affinity to all placed VMs
            affinity_scores = [
                self.analyzer.get_affinity_score(vm.id, placed_id)
                for placed_id in placed_vm_ids
            ]
            avg_affinity = sum(affinity_scores) / len(affinity_scores) if affinity_scores else 0.0
            
            # Add some randomness to avoid always picking the same VMs
            score = avg_affinity + random.random() * 0.1
            
            if score > best_score:
                best_score = score
                best_idx = idx
        
        return best_idx
    
    def build_multiple_solutions(self, vms: List[VirtualMachine], server_template: Server,
                                num_solutions: int, affinity_weight: float = 0.7) -> List[Solution]:
        """
        Build multiple diverse solutions using crowd wisdom.
        
        Args:
            vms: List of VMs to pack
            server_template: Template server with capacity constraints
            num_solutions: Number of solutions to generate
            affinity_weight: Weight for affinity vs random selection
        
        Returns:
            List of solutions
        """
        solutions = []
        for i in range(num_solutions):
            # Vary affinity weight slightly for diversity
            varied_weight = max(0.5, min(0.9, affinity_weight + random.uniform(-0.1, 0.1)))
            solution = self.build_solution(vms, server_template, varied_weight)
            solution.metadata['crowd_solution_index'] = i
            solutions.append(solution)
        
        return solutions
