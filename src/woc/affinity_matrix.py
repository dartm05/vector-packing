"""
Affinity Matrix - Analyzes patterns in successful solutions.

This module implements the "Wisdom of Crowds" pattern extraction by
analyzing which VMs are frequently placed together on the same server
in successful solutions.
"""

from typing import List, Dict, Tuple
import numpy as np
from ..models import Solution, VirtualMachine


class AffinityMatrix:
    """
    Builds and maintains a co-occurrence matrix showing which VMs
    tend to be placed together in successful solutions.
    """
    
    def __init__(self, num_vms: int):
        """
        Initialize the affinity matrix.
        
        Args:
            num_vms: Total number of VMs in the problem
        """
        self.num_vms = num_vms
        # Matrix[i][j] = how many times VM i and VM j were on same server
        self.co_occurrence = np.zeros((num_vms, num_vms), dtype=float)
        # Track how many solutions we've analyzed
        self.solution_count = 0
        
    def update(self, solution: Solution, weight: float = 1.0):
        """
        Update the affinity matrix based on a solution.
        Better solutions should have higher weights.
        
        Args:
            solution: Solution to learn from
            weight: Weight to apply (higher for better solutions)
        """
        # For each server in the solution
        for server in solution.servers:
            if not server.vms:
                continue
            
            # Get VM IDs on this server
            vm_ids = [vm.id for vm in server.vms]
            
            # Update co-occurrence for all pairs
            for i, vm1_id in enumerate(vm_ids):
                for vm2_id in vm_ids[i:]:  # Include self and upper triangle
                    self.co_occurrence[vm1_id][vm2_id] += weight
                    if vm1_id != vm2_id:
                        # Symmetric matrix
                        self.co_occurrence[vm2_id][vm1_id] += weight
        
        self.solution_count += 1
    
    def get_affinity(self, vm1_id: int, vm2_id: int) -> float:
        """
        Get the affinity score between two VMs.
        
        Args:
            vm1_id: First VM ID
            vm2_id: Second VM ID
            
        Returns:
            Normalized affinity score (0.0 to 1.0)
        """
        if self.solution_count == 0:
            return 0.0
        
        # Normalize by number of solutions analyzed
        return self.co_occurrence[vm1_id][vm2_id] / self.solution_count
    
    def get_most_compatible_vms(self, vm_id: int, k: int = 5) -> List[Tuple[int, float]]:
        """
        Get the k VMs most compatible with the given VM.
        
        Args:
            vm_id: VM to find compatible VMs for
            k: Number of compatible VMs to return
            
        Returns:
            List of (vm_id, affinity_score) tuples, sorted by affinity
        """
        if self.solution_count == 0:
            return []
        
        # Get affinities for this VM with all others
        affinities = []
        for other_id in range(self.num_vms):
            if other_id == vm_id:
                continue
            affinity = self.get_affinity(vm_id, other_id)
            if affinity > 0:
                affinities.append((other_id, affinity))
        
        # Sort by affinity (descending) and return top k
        affinities.sort(key=lambda x: x[1], reverse=True)
        return affinities[:k]
    
    def get_affinity_groups(self, min_affinity: float = 0.3) -> List[List[int]]:
        """
        Extract groups of VMs that have high affinity with each other.
        Uses simple greedy clustering.
        
        Args:
            min_affinity: Minimum affinity score to consider
            
        Returns:
            List of VM groups (each group is a list of VM IDs)
        """
        if self.solution_count == 0:
            return []
        
        # Normalize the matrix
        normalized = self.co_occurrence / max(self.solution_count, 1)
        
        # Track which VMs have been assigned to groups
        assigned = set()
        groups = []
        
        # Greedy clustering: start with highest affinity pairs
        for vm_id in range(self.num_vms):
            if vm_id in assigned:
                continue
            
            # Start a new group with this VM
            group = [vm_id]
            assigned.add(vm_id)
            
            # Find VMs with high affinity to this group
            candidates = list(range(self.num_vms))
            candidates.sort(key=lambda x: normalized[vm_id][x], reverse=True)
            
            for candidate_id in candidates:
                if candidate_id in assigned:
                    continue
                
                # Check if candidate has good affinity with all group members
                avg_affinity = np.mean([normalized[candidate_id][member_id] 
                                       for member_id in group])
                
                if avg_affinity >= min_affinity:
                    group.append(candidate_id)
                    assigned.add(candidate_id)
            
            if len(group) > 1:  # Only keep groups with multiple VMs
                groups.append(group)
        
        return groups
    
    def to_dict(self) -> Dict:
        """Export affinity matrix data for analysis."""
        return {
            'num_vms': self.num_vms,
            'solution_count': self.solution_count,
            'co_occurrence': self.co_occurrence.tolist()
        }
