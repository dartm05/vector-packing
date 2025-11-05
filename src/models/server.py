"""
Server (Physical Host) Model
Represents a bin with maximum capacity constraints
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .virtual_machine import VirtualMachine


@dataclass
class Server:
    """
    Represents a Physical Server (bin) with capacity constraints.
    
    Attributes:
        id: Unique identifier for the server
        max_cpu_cores: Maximum CPU cores available
        max_ram_gb: Maximum RAM available in GB
        max_storage_gb: Maximum storage available in GB
        vms: List of VMs assigned to this server
        name: Optional human-readable name
    """
    id: int
    max_cpu_cores: float
    max_ram_gb: float
    max_storage_gb: float
    vms: List[VirtualMachine] = field(default_factory=list)
    name: str = ""
    
    def __post_init__(self):
        if not self.name:
            self.name = f"Server-{self.id}"
    
    @property
    def used_cpu(self) -> float:
        """Calculate total CPU cores used"""
        return sum(vm.cpu_cores for vm in self.vms)
    
    @property
    def used_ram(self) -> float:
        """Calculate total RAM used in GB"""
        return sum(vm.ram_gb for vm in self.vms)
    
    @property
    def used_storage(self) -> float:
        """Calculate total storage used in GB"""
        return sum(vm.storage_gb for vm in self.vms)
    
    @property
    def available_cpu(self) -> float:
        """Calculate available CPU cores"""
        return self.max_cpu_cores - self.used_cpu
    
    @property
    def available_ram(self) -> float:
        """Calculate available RAM in GB"""
        return self.max_ram_gb - self.used_ram
    
    @property
    def available_storage(self) -> float:
        """Calculate available storage in GB"""
        return self.max_storage_gb - self.used_storage
    
    @property
    def utilization_cpu(self) -> float:
        """Calculate CPU utilization percentage"""
        return (self.used_cpu / self.max_cpu_cores) * 100 if self.max_cpu_cores > 0 else 0
    
    @property
    def utilization_ram(self) -> float:
        """Calculate RAM utilization percentage"""
        return (self.used_ram / self.max_ram_gb) * 100 if self.max_ram_gb > 0 else 0
    
    @property
    def utilization_storage(self) -> float:
        """Calculate storage utilization percentage"""
        return (self.used_storage / self.max_storage_gb) * 100 if self.max_storage_gb > 0 else 0
    
    def can_fit(self, vm: VirtualMachine) -> bool:
        """
        Check if a VM can fit in this server
        
        Args:
            vm: VirtualMachine to check
            
        Returns:
            True if VM can fit, False otherwise
        """
        return (self.available_cpu >= vm.cpu_cores and
                self.available_ram >= vm.ram_gb and
                self.available_storage >= vm.storage_gb)
    
    def add_vm(self, vm: VirtualMachine) -> bool:
        """
        Add a VM to this server if it fits
        
        Args:
            vm: VirtualMachine to add
            
        Returns:
            True if VM was added, False if it doesn't fit
        """
        if self.can_fit(vm):
            self.vms.append(vm)
            return True
        return False
    
    def remove_vm(self, vm: VirtualMachine) -> bool:
        """
        Remove a VM from this server
        
        Args:
            vm: VirtualMachine to remove
            
        Returns:
            True if VM was removed, False if not found
        """
        if vm in self.vms:
            self.vms.remove(vm)
            return True
        return False
    
    def clear(self):
        """Remove all VMs from this server"""
        self.vms.clear()
    
    def __repr__(self) -> str:
        return (f"Server({self.name}: "
                f"CPU={self.used_cpu}/{self.max_cpu_cores}, "
                f"RAM={self.used_ram}/{self.max_ram_gb}GB, "
                f"Storage={self.used_storage}/{self.max_storage_gb}GB, "
                f"VMs={len(self.vms)})")
    
    def to_dict(self) -> Dict:
        """Convert server to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'max_cpu_cores': self.max_cpu_cores,
            'max_ram_gb': self.max_ram_gb,
            'max_storage_gb': self.max_storage_gb,
            'vms': [vm.id for vm in self.vms],
            'utilization': {
                'cpu': self.utilization_cpu,
                'ram': self.utilization_ram,
                'storage': self.utilization_storage
            }
        }
