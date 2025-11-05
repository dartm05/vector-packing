"""
Solution Model
Represents a complete packing solution (chromosome in GA)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .virtual_machine import VirtualMachine
from .server import Server
import copy


@dataclass
class Solution:
    """
    Represents a complete solution to the vector packing problem.
    
    Attributes:
        servers: List of servers with assigned VMs
        fitness: Fitness score of this solution
        generation: Generation number when solution was created
        metadata: Additional metadata about the solution
    """
    servers: List[Server] = field(default_factory=list)
    fitness: Optional[float] = None
    generation: int = 0
    metadata: Dict = field(default_factory=dict)
    
    @property
    def num_servers_used(self) -> int:
        """Number of servers that have at least one VM"""
        return sum(1 for server in self.servers if len(server.vms) > 0)
    
    @property
    def total_vms(self) -> int:
        """Total number of VMs across all servers"""
        return sum(len(server.vms) for server in self.servers)
    
    @property
    def average_utilization(self) -> Dict[str, float]:
        """Calculate average utilization across used servers"""
        used_servers = [s for s in self.servers if len(s.vms) > 0]
        if not used_servers:
            return {'cpu': 0.0, 'ram': 0.0, 'storage': 0.0}
        
        return {
            'cpu': sum(s.utilization_cpu for s in used_servers) / len(used_servers),
            'ram': sum(s.utilization_ram for s in used_servers) / len(used_servers),
            'storage': sum(s.utilization_storage for s in used_servers) / len(used_servers)
        }
    
    def is_valid(self) -> bool:
        """
        Check if solution is valid (no capacity violations)
        
        Returns:
            True if valid, False otherwise
        """
        for server in self.servers:
            if (server.used_cpu > server.max_cpu_cores or
                server.used_ram > server.max_ram_gb or
                server.used_storage > server.max_storage_gb):
                return False
        return True
    
    def clone(self) -> 'Solution':
        """Create a deep copy of this solution"""
        return copy.deepcopy(self)
    
    def get_vm_assignment(self) -> Dict[int, int]:
        """
        Get mapping of VM ID to Server ID
        
        Returns:
            Dictionary mapping VM IDs to Server IDs
        """
        assignment = {}
        for server in self.servers:
            for vm in server.vms:
                assignment[vm.id] = server.id
        return assignment
    
    def to_dict(self) -> Dict:
        """Convert solution to dictionary representation"""
        return {
            'num_servers_used': self.num_servers_used,
            'total_vms': self.total_vms,
            'fitness': self.fitness,
            'generation': self.generation,
            'average_utilization': self.average_utilization,
            'servers': [server.to_dict() for server in self.servers if len(server.vms) > 0],
            'vm_assignments': self.get_vm_assignment(),
            'is_valid': self.is_valid(),
            'metadata': self.metadata
        }
    
    def __repr__(self) -> str:
        return (f"Solution(Servers={self.num_servers_used}, "
                f"VMs={self.total_vms}, "
                f"Fitness={self.fitness:.4f if self.fitness else 'N/A'}, "
                f"Valid={self.is_valid()})")
