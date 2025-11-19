"""
Azure Packing Trace 2020 Data Loader

This module loads and preprocesses real VM allocation data from Microsoft Azure's
public dataset for use in bin packing experiments.

Dataset: Azure Traces for Packing 2020
Source: https://github.com/Azure/AzurePublicDataset
Paper: Protean: VM Allocation Service at Scale (OSDI 2020)
"""

import sqlite3
import random
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from ..models import VirtualMachine, Server


class AzureDataLoader:
    """
    Loads and preprocesses Azure VM allocation traces for bin packing experiments.

    The Azure dataset contains fractional resource requirements (0-1) representing
    the fraction of a server's capacity. This loader converts them to concrete values.
    """

    def __init__(self, db_path: str):
        """
        Initialize the loader with path to SQLite database.

        Args:
            db_path: Path to packing_trace_zone_a_v1.sqlite file
        """
        self.db_path = db_path
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

    def get_database_stats(self) -> Dict:
        """
        Get statistics about the Azure dataset.

        Returns:
            Dictionary with dataset statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total VM requests
        cursor.execute("SELECT COUNT(*) FROM vm")
        stats['total_vm_requests'] = cursor.fetchone()[0]

        # Total VM types
        cursor.execute("SELECT COUNT(DISTINCT vmTypeId) FROM vmType")
        stats['total_vm_types'] = cursor.fetchone()[0]

        # Active VMs at time 0 (VMs with starttime <= 0 and (endtime > 0 or endtime is NULL))
        cursor.execute("""
            SELECT COUNT(*)
            FROM vm
            WHERE starttime <= 0 AND (endtime > 0 OR endtime IS NULL)
        """)
        stats['active_vms_at_time_0'] = cursor.fetchone()[0]

        # Time range
        cursor.execute("SELECT MIN(starttime), MAX(starttime) FROM vm WHERE starttime IS NOT NULL")
        min_time, max_time = cursor.fetchone()
        stats['time_range_hours'] = (min_time, max_time)

        # Priority distribution
        cursor.execute("SELECT priority, COUNT(*) FROM vm GROUP BY priority")
        stats['priority_distribution'] = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()
        return stats

    def load_vm_types(self) -> Dict[int, Dict[str, float]]:
        """
        Load all VM types with their fractional resource requirements.

        Returns:
            Dictionary mapping vmTypeId to resource fractions
            {vmTypeId: {'core': float, 'memory': float, 'ssd': float, 'nic': float}}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT vmTypeId, core, memory, hdd, ssd, nic
            FROM vmType
            GROUP BY vmTypeId
        """)

        vm_types = {}
        for row in cursor.fetchall():
            vm_type_id, core, memory, hdd, ssd, nic = row
            vm_types[vm_type_id] = {
                'core': core or 0.0,
                'memory': memory or 0.0,
                'hdd': hdd or 0.0,
                'ssd': ssd or 0.0,
                'nic': nic or 0.0
            }

        conn.close()
        return vm_types

    def load_active_vms_at_time(self,
                                time_point: float = 0.0,
                                priority: Optional[int] = None) -> List[Tuple[int, int]]:
        """
        Load VMs that are active at a specific time point.

        Args:
            time_point: Time in hours (default: 0.0)
            priority: Optional filter by priority level (0 or 1)

        Returns:
            List of (vmId, vmTypeId) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT vmId, vmTypeId
            FROM vm
            WHERE starttime <= ?
              AND (endtime > ? OR endtime IS NULL)
        """
        params = [time_point, time_point]

        if priority is not None:
            query += " AND priority = ?"
            params.append(priority)

        cursor.execute(query, params)
        active_vms = cursor.fetchall()

        conn.close()
        return active_vms

    def convert_to_virtual_machines(self,
                                    vm_list: List[Tuple[int, int]],
                                    vm_types: Dict[int, Dict[str, float]],
                                    server_template: Server,
                                    use_storage_as_ssd: bool = True) -> List[VirtualMachine]:
        """
        Convert Azure VM data to VirtualMachine objects.

        Args:
            vm_list: List of (vmId, vmTypeId) tuples
            vm_types: VM type definitions with fractional resources
            server_template: Server template to scale resources to
            use_storage_as_ssd: If True, use SSD for storage dimension; if False, use HDD

        Returns:
            List of VirtualMachine objects
        """
        virtual_machines = []

        storage_key = 'ssd' if use_storage_as_ssd else 'hdd'

        for vm_id, vm_type_id in vm_list:
            if vm_type_id not in vm_types:
                continue

            vm_type = vm_types[vm_type_id]

            # Convert fractional resources to actual values
            cpu_cores = vm_type['core'] * server_template.max_cpu_cores
            ram_gb = vm_type['memory'] * server_template.max_ram_gb
            storage_gb = vm_type[storage_key] * server_template.max_storage_gb

            # Skip VMs with zero resources (edge case)
            if cpu_cores == 0 or ram_gb == 0 or storage_gb == 0:
                continue

            vm = VirtualMachine(
                id=vm_id,
                cpu_cores=cpu_cores,
                ram_gb=ram_gb,
                storage_gb=storage_gb,
                name=f"Azure-VM-{vm_id}",
                metadata={
                    'vm_type_id': vm_type_id,
                    'source': 'azure_packing_trace_2020',
                    'fractional_core': vm_type['core'],
                    'fractional_memory': vm_type['memory'],
                    'fractional_ssd': vm_type['ssd'],
                    'fractional_hdd': vm_type['hdd']
                }
            )
            virtual_machines.append(vm)

        return virtual_machines

    def sample_vms(self,
                   vms: List[VirtualMachine],
                   num_samples: int,
                   seed: Optional[int] = None) -> List[VirtualMachine]:
        """
        Sample a subset of VMs for manageable experiments.

        Args:
            vms: Full list of VMs
            num_samples: Number of VMs to sample
            seed: Random seed for reproducibility

        Returns:
            Sampled list of VMs with renumbered IDs
        """
        if seed is not None:
            random.seed(seed)

        if len(vms) <= num_samples:
            sampled = vms
        else:
            sampled = random.sample(vms, num_samples)

        # Renumber IDs sequentially for consistency
        for i, vm in enumerate(sampled):
            vm.id = i
            vm.name = f"Azure-VM-{i}"

        return sampled

    def generate_scenario_from_azure(self,
                                     scenario_size: str = 'small',
                                     time_point: float = 0.0,
                                     priority: Optional[int] = None,
                                     seed: Optional[int] = None,
                                     use_storage_as_ssd: bool = True) -> Dict:
        """
        Generate a complete scenario from Azure data matching predefined sizes.

        Args:
            scenario_size: 'small' (20), 'medium' (50), 'large' (100), 'extra_large' (200)
            time_point: Time point in hours to sample from
            priority: Optional priority filter
            seed: Random seed
            use_storage_as_ssd: Use SSD (True) or HDD (False) for storage dimension

        Returns:
            Dictionary with 'vms', 'server_template', 'scenario_name', 'num_vms'
        """
        # Define scenario parameters matching synthetic data generator
        scenario_configs = {
            'small': {
                'num_vms': 20,
                'server_cpu': 32,
                'server_ram': 128,
                'server_storage': 1000
            },
            'medium': {
                'num_vms': 50,
                'server_cpu': 64,
                'server_ram': 256,
                'server_storage': 2000
            },
            'large': {
                'num_vms': 100,
                'server_cpu': 96,
                'server_ram': 512,
                'server_storage': 4000
            },
            'extra_large': {
                'num_vms': 200,
                'server_cpu': 128,
                'server_ram': 1024,
                'server_storage': 8000
            }
        }

        if scenario_size not in scenario_configs:
            raise ValueError(f"Unknown scenario size: {scenario_size}. "
                           f"Available: {list(scenario_configs.keys())}")

        config = scenario_configs[scenario_size]

        # Create server template
        server_template = Server(
            id=0,
            max_cpu_cores=config['server_cpu'],
            max_ram_gb=config['server_ram'],
            max_storage_gb=config['server_storage'],
            name=f"Azure-Server-Template-{scenario_size}"
        )

        # Load VM types
        vm_types = self.load_vm_types()

        # Load active VMs at the specified time
        active_vm_list = self.load_active_vms_at_time(time_point, priority)

        # Convert to VirtualMachine objects
        all_vms = self.convert_to_virtual_machines(
            active_vm_list,
            vm_types,
            server_template,
            use_storage_as_ssd
        )

        # Sample to desired size
        sampled_vms = self.sample_vms(all_vms, config['num_vms'], seed)

        return {
            'vms': sampled_vms,
            'server_template': server_template,
            'scenario_name': f"azure_{scenario_size}",
            'num_vms': len(sampled_vms),
            'metadata': {
                'source': 'Azure Packing Trace 2020',
                'time_point': time_point,
                'priority_filter': priority,
                'original_pool_size': len(all_vms),
                'storage_dimension': 'ssd' if use_storage_as_ssd else 'hdd'
            }
        }

    def generate_multiple_scenarios(self,
                                    seed: Optional[int] = None) -> Dict[str, Dict]:
        """
        Generate all four scenario sizes at once.

        Args:
            seed: Random seed for reproducibility

        Returns:
            Dictionary mapping scenario names to scenario data
        """
        scenarios = {}

        for size in ['small', 'medium', 'large', 'extra_large']:
            scenarios[size] = self.generate_scenario_from_azure(
                scenario_size=size,
                time_point=0.0,
                seed=seed
            )

        return scenarios

    def print_statistics(self):
        """Print detailed statistics about the dataset."""
        stats = self.get_database_stats()

        print("=" * 80)
        print("AZURE PACKING TRACE 2020 - DATASET STATISTICS")
        print("=" * 80)
        print(f"Total VM Requests:       {stats['total_vm_requests']:>12,}")
        print(f"Total VM Types:          {stats['total_vm_types']:>12,}")
        print(f"Active VMs at t=0:       {stats['active_vms_at_time_0']:>12,}")
        print(f"\nTime Range (hours):      {stats['time_range_hours'][0]:>12.2f} to {stats['time_range_hours'][1]:.2f}")

        print(f"\nPriority Distribution:")
        for priority, count in sorted(stats['priority_distribution'].items()):
            priority_label = "High" if priority == 0 else "Low" if priority == 1 else "Unknown"
            print(f"  Priority {priority} ({priority_label:<7}): {count:>12,} VMs")

        print("=" * 80)
