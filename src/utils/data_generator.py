"""
Test Data Generator for Vector Packing Problems
"""

import random
from typing import List, Dict, Tuple
from ..models import VirtualMachine, Server


class DataGenerator:
    """
    Generates realistic test data for cloud VM packing scenarios.
    """
    
    @staticmethod
    def generate_vms(num_vms: int,
                    cpu_range: Tuple[float, float] = (1, 16),
                    ram_range: Tuple[float, float] = (2, 64),
                    storage_range: Tuple[float, float] = (20, 500),
                    seed: int = None) -> List[VirtualMachine]:
        """
        Generate a list of VMs with random resource requirements.
        
        Args:
            num_vms: Number of VMs to generate
            cpu_range: (min, max) CPU cores
            ram_range: (min, max) RAM in GB
            storage_range: (min, max) storage in GB
            seed: Random seed for reproducibility
            
        Returns:
            List of VirtualMachine objects
        """
        if seed is not None:
            random.seed(seed)
        
        vms = []
        for i in range(num_vms):
            vm = VirtualMachine(
                id=i,
                cpu_cores=random.uniform(*cpu_range),
                ram_gb=random.uniform(*ram_range),
                storage_gb=random.uniform(*storage_range),
                name=f"VM-{i}"
            )
            vms.append(vm)
        
        return vms
    
    @staticmethod
    def generate_vms_with_patterns(num_vms: int,
                                   pattern_type: str = 'mixed',
                                   seed: int = None) -> List[VirtualMachine]:
        """
        Generate VMs with specific patterns (useful for testing affinity detection).
        
        Args:
            num_vms: Number of VMs to generate
            pattern_type: Type of pattern ('small', 'medium', 'large', 'mixed')
            seed: Random seed
            
        Returns:
            List of VirtualMachine objects
        """
        if seed is not None:
            random.seed(seed)
        
        patterns = {
            'small': (1, 4, 2, 8, 20, 100),      # CPU, RAM, Storage ranges
            'medium': (4, 8, 8, 16, 100, 200),
            'large': (8, 16, 32, 64, 200, 500)
        }
        
        vms = []
        
        if pattern_type == 'mixed':
            # Create equal mix of all types
            types = ['small', 'medium', 'large']
            vms_per_type = num_vms // len(types)
            
            for idx, vm_type in enumerate(types):
                cpu_min, cpu_max, ram_min, ram_max, storage_min, storage_max = patterns[vm_type]
                for i in range(vms_per_type):
                    vm_id = idx * vms_per_type + i
                    vm = VirtualMachine(
                        id=vm_id,
                        cpu_cores=random.uniform(cpu_min, cpu_max),
                        ram_gb=random.uniform(ram_min, ram_max),
                        storage_gb=random.uniform(storage_min, storage_max),
                        name=f"VM-{vm_type}-{i}",
                        metadata={'type': vm_type}
                    )
                    vms.append(vm)
            
            # Fill remaining VMs
            remaining = num_vms - len(vms)
            for i in range(remaining):
                vm_type = random.choice(types)
                cpu_min, cpu_max, ram_min, ram_max, storage_min, storage_max = patterns[vm_type]
                vm = VirtualMachine(
                    id=len(vms),
                    cpu_cores=random.uniform(cpu_min, cpu_max),
                    ram_gb=random.uniform(ram_min, ram_max),
                    storage_gb=random.uniform(storage_min, storage_max),
                    name=f"VM-{vm_type}-extra-{i}",
                    metadata={'type': vm_type}
                )
                vms.append(vm)
        else:
            # Single pattern type
            cpu_min, cpu_max, ram_min, ram_max, storage_min, storage_max = patterns[pattern_type]
            for i in range(num_vms):
                vm = VirtualMachine(
                    id=i,
                    cpu_cores=random.uniform(cpu_min, cpu_max),
                    ram_gb=random.uniform(ram_min, ram_max),
                    storage_gb=random.uniform(storage_min, storage_max),
                    name=f"VM-{pattern_type}-{i}",
                    metadata={'type': pattern_type}
                )
                vms.append(vm)
        
        return vms
    
    @staticmethod
    def create_server_template(cpu_cores: float = 64,
                              ram_gb: float = 256,
                              storage_gb: float = 2000) -> Server:
        """
        Create a server template with specified capacity.
        
        Args:
            cpu_cores: Maximum CPU cores
            ram_gb: Maximum RAM in GB
            storage_gb: Maximum storage in GB
            
        Returns:
            Server template object
        """
        return Server(
            id=0,
            max_cpu_cores=cpu_cores,
            max_ram_gb=ram_gb,
            max_storage_gb=storage_gb,
            name="Server-Template"
        )
    
    @staticmethod
    def generate_scenario(scenario_name: str, seed: int = None) -> Dict:
        """
        Generate predefined scenarios for testing.
        
        Args:
            scenario_name: Name of the scenario
            seed: Random seed
            
        Returns:
            Dictionary with VMs and server template
        """
        scenarios = {
            'small': {
                'num_vms': 20,
                'server': DataGenerator.create_server_template(32, 128, 1000),
                'pattern': 'mixed'
            },
            'medium': {
                'num_vms': 50,
                'server': DataGenerator.create_server_template(64, 256, 2000),
                'pattern': 'mixed'
            },
            'large': {
                'num_vms': 100,
                'server': DataGenerator.create_server_template(96, 512, 4000),
                'pattern': 'mixed'
            },
            'extra_large': {
                'num_vms': 200,
                'server': DataGenerator.create_server_template(128, 1024, 8000),
                'pattern': 'mixed'
            }
        }
        
        if scenario_name not in scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}. "
                           f"Available: {list(scenarios.keys())}")
        
        config = scenarios[scenario_name]
        vms = DataGenerator.generate_vms_with_patterns(
            config['num_vms'],
            config['pattern'],
            seed
        )
        
        return {
            'vms': vms,
            'server_template': config['server'],
            'scenario_name': scenario_name,
            'num_vms': len(vms)
        }
    
    @staticmethod
    def save_dataset(vms: List[VirtualMachine], filename: str):
        """Save VM dataset to JSON file"""
        import json
        data = [vm.to_dict() for vm in vms]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_dataset(filename: str) -> List[VirtualMachine]:
        """Load VM dataset from JSON file"""
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
        return [VirtualMachine.from_dict(vm_data) for vm_data in data]

    @staticmethod
    def load_azure_scenario(scenario_name: str,
                           db_path: str = None,
                           seed: int = None) -> Dict:
        """
        Load a scenario from Azure Packing Trace 2020 dataset.

        Args:
            scenario_name: 'small', 'medium', 'large', or 'extra_large'
            db_path: Path to SQLite database (defaults to datasets/packing_trace_zone_a_v1.sqlite)
            seed: Random seed for reproducibility

        Returns:
            Dictionary with VMs and server template
        """
        from .azure_data_loader import AzureDataLoader
        from pathlib import Path

        # Default database path
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / 'datasets' / 'packing_trace_zone_a_v1.sqlite'
            db_path = str(db_path)

        loader = AzureDataLoader(db_path)
        return loader.generate_scenario_from_azure(scenario_name, seed=seed)
