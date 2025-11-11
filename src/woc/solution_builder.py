"""
Solution Builder - Constructs new solutions using learned patterns.

This module builds solutions using the affinity patterns extracted
from successful solutions, implementing different "crowd" strategies.
"""

from typing import List, Optional
import random
from ..models import VirtualMachine, Server, Solution
from .affinity_matrix import AffinityMatrix


class AffinityBasedBuilder:
    """
    Builds solutions by grouping VMs with high affinity together.
    """
    
    def __init__(self, affinity_matrix: AffinityMatrix):
        """
        Initialize the builder.
        
        Args:
            affinity_matrix: Learned affinity patterns
        """
        self.affinity_matrix = affinity_matrix
    
    def build_solution(self, vms: List[VirtualMachine], 
                      server_template: Server,
                      strategy: str = 'greedy') -> Solution:
        """
        Build a solution using affinity patterns.
        
        Args:
            vms: List of VMs to place
            server_template: Server capacity template
            strategy: Building strategy ('greedy', 'group_based', 'iterative')
            
        Returns:
            New solution based on affinity patterns
        """
        if strategy == 'greedy':
            return self._build_greedy(vms, server_template)
        elif strategy == 'group_based':
            return self._build_from_groups(vms, server_template)
        elif strategy == 'iterative':
            return self._build_iterative(vms, server_template)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _build_greedy(self, vms: List[VirtualMachine], 
                     server_template: Server) -> Solution:
        """
        Greedy: Place VMs with highest affinity together.
        """
        servers = []
        vm_dict = {vm.id: vm for vm in vms}
        remaining_vms = set(vm.id for vm in vms)
        
        while remaining_vms:
            # Create a new server
            server = Server(
                id=len(servers),
                max_cpu_cores=server_template.max_cpu_cores,
                max_ram_gb=server_template.max_ram_gb,
                max_storage_gb=server_template.max_storage_gb
            )
            
            # Pick a starting VM (prioritize largest remaining)
            start_vm_id = max(remaining_vms, 
                            key=lambda vid: vm_dict[vid].cpu_cores + 
                                          vm_dict[vid].ram_gb/10 + 
                                          vm_dict[vid].storage_gb/100)
            
            start_vm = vm_dict[start_vm_id]
            if server.add_vm(start_vm):
                remaining_vms.remove(start_vm_id)
            
            # Keep adding VMs with highest affinity that fit
            while True:
                best_vm_id = None
                best_score = -1
                
                # Find VM with best affinity to current server contents
                for vm_id in remaining_vms:
                    vm = vm_dict[vm_id]
                    
                    if not server.can_fit(vm):
                        continue
                    
                    # Calculate average affinity to VMs already on this server
                    if server.vms:
                        affinity_sum = sum(
                            self.affinity_matrix.get_affinity(vm_id, existing.id)
                            for existing in server.vms
                        )
                        affinity_score = affinity_sum / len(server.vms)
                    else:
                        affinity_score = 0
                    
                    # Combine affinity with fit quality
                    fit_score = min(
                        server.available_cpu / vm.cpu_cores if vm.cpu_cores > 0 else 1,
                        server.available_ram / vm.ram_gb if vm.ram_gb > 0 else 1,
                        server.available_storage / vm.storage_gb if vm.storage_gb > 0 else 1
                    )
                    
                    combined_score = affinity_score * 0.7 + fit_score * 0.3
                    
                    if combined_score > best_score:
                        best_score = combined_score
                        best_vm_id = vm_id
                
                # Add best VM if found
                if best_vm_id is not None:
                    server.add_vm(vm_dict[best_vm_id])
                    remaining_vms.remove(best_vm_id)
                else:
                    break  # No more VMs fit
            
            servers.append(server)
        
        return Solution(servers=servers)
    
    def _build_from_groups(self, vms: List[VirtualMachine], 
                          server_template: Server) -> Solution:
        """
        Group-based: Extract affinity groups and pack them together.
        """
        # Get affinity groups from the matrix
        groups = self.affinity_matrix.get_affinity_groups(min_affinity=0.3)
        
        vm_dict = {vm.id: vm for vm in vms}
        assigned_vms = set()
        servers = []
        
        # First, pack affinity groups
        for group_ids in groups:
            # Get VMs in this group
            group_vms = [vm_dict[vm_id] for vm_id in group_ids if vm_id in vm_dict]
            
            if not group_vms:
                continue
            
            # Sort by size (largest first)
            group_vms.sort(key=lambda v: v.cpu_cores + v.ram_gb/10 + v.storage_gb/100, 
                          reverse=True)
            
            # Try to pack this group into as few servers as possible
            group_servers = []
            
            for vm in group_vms:
                placed = False
                
                # Try existing servers for this group
                for server in group_servers:
                    if server.can_fit(vm):
                        server.add_vm(vm)
                        assigned_vms.add(vm.id)
                        placed = True
                        break
                
                # Create new server if needed
                if not placed:
                    new_server = Server(
                        id=len(servers) + len(group_servers),
                        max_cpu_cores=server_template.max_cpu_cores,
                        max_ram_gb=server_template.max_ram_gb,
                        max_storage_gb=server_template.max_storage_gb
                    )
                    if new_server.add_vm(vm):
                        group_servers.append(new_server)
                        assigned_vms.add(vm.id)
            
            servers.extend(group_servers)
        
        # Pack remaining VMs using first-fit
        remaining_vms = [vm for vm in vms if vm.id not in assigned_vms]
        remaining_vms.sort(key=lambda v: v.cpu_cores + v.ram_gb/10 + v.storage_gb/100, 
                          reverse=True)
        
        for vm in remaining_vms:
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
                    max_storage_gb=server_template.max_storage_gb
                )
                new_server.add_vm(vm)
                servers.append(new_server)
        
        return Solution(servers=servers)
    
    def _build_iterative(self, vms: List[VirtualMachine], 
                        server_template: Server) -> Solution:
        """
        Iterative: Build solution by iteratively selecting best VM for each server.
        """
        servers = []
        vm_dict = {vm.id: vm for vm in vms}
        remaining_vms = set(vm.id for vm in vms)
        
        while remaining_vms:
            # Create a new server
            server = Server(
                id=len(servers),
                max_cpu_cores=server_template.max_cpu_cores,
                max_ram_gb=server_template.max_ram_gb,
                max_storage_gb=server_template.max_storage_gb
            )
            
            # Keep adding best VMs
            while remaining_vms:
                best_vm_id = None
                best_score = -float('inf')
                
                for vm_id in remaining_vms:
                    vm = vm_dict[vm_id]
                    
                    if not server.can_fit(vm):
                        continue
                    
                    # Score based on affinity and resource balance
                    if server.vms:
                        affinity = np.mean([
                            self.affinity_matrix.get_affinity(vm_id, existing.id)
                            for existing in server.vms
                        ])
                    else:
                        affinity = 0
                    
                    # Prefer VMs that balance resource usage
                    cpu_util_after = (server.used_cpu + vm.cpu_cores) / server.max_cpu_cores
                    ram_util_after = (server.used_ram + vm.ram_gb) / server.max_ram_gb
                    storage_util_after = (server.used_storage + vm.storage_gb) / server.max_storage_gb
                    
                    balance = 1.0 - np.std([cpu_util_after, ram_util_after, storage_util_after])
                    
                    score = affinity * 0.6 + balance * 0.4
                    
                    if score > best_score:
                        best_score = score
                        best_vm_id = vm_id
                
                if best_vm_id is not None:
                    server.add_vm(vm_dict[best_vm_id])
                    remaining_vms.remove(best_vm_id)
                else:
                    break  # No more VMs fit
            
            servers.append(server)
        
        return Solution(servers=servers)


import numpy as np  # Import at top but added here for clarity in _build_iterative
