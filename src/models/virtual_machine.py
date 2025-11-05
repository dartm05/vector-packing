"""
Virtual Machine (VM) Model
Represents an item to be packed with resource requirements
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class VirtualMachine:
    """
    Represents a Virtual Machine with resource requirements.
    
    Attributes:
        id: Unique identifier for the VM
        cpu_cores: Number of CPU cores required
        ram_gb: Amount of RAM required in GB
        storage_gb: Amount of storage required in GB
        name: Optional human-readable name
        metadata: Additional metadata for the VM
    """
    id: int
    cpu_cores: float
    ram_gb: float
    storage_gb: float
    name: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.name:
            self.name = f"VM-{self.id}"
    
    @property
    def resource_vector(self) -> tuple:
        """Returns the resource requirements as a vector"""
        return (self.cpu_cores, self.ram_gb, self.storage_gb)
    
    def __repr__(self) -> str:
        return f"VM({self.name}: CPU={self.cpu_cores}, RAM={self.ram_gb}GB, Storage={self.storage_gb}GB)"
    
    def to_dict(self) -> Dict:
        """Convert VM to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'cpu_cores': self.cpu_cores,
            'ram_gb': self.ram_gb,
            'storage_gb': self.storage_gb,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VirtualMachine':
        """Create VM from dictionary representation"""
        return cls(**data)
