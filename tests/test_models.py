"""
Unit tests for data models
"""

import pytest
from src.models import VirtualMachine, Server, Solution


class TestVirtualMachine:
    """Test cases for VirtualMachine class"""
    
    def test_vm_creation(self):
        """Test basic VM creation"""
        vm = VirtualMachine(id=1, cpu_cores=4, ram_gb=16, storage_gb=100)
        assert vm.id == 1
        assert vm.cpu_cores == 4
        assert vm.ram_gb == 16
        assert vm.storage_gb == 100
        assert vm.name == "VM-1"
    
    def test_vm_resource_vector(self):
        """Test resource vector property"""
        vm = VirtualMachine(id=1, cpu_cores=4, ram_gb=16, storage_gb=100)
        assert vm.resource_vector == (4, 16, 100)
    
    def test_vm_to_dict(self):
        """Test VM serialization"""
        vm = VirtualMachine(id=1, cpu_cores=4, ram_gb=16, storage_gb=100)
        vm_dict = vm.to_dict()
        assert vm_dict['id'] == 1
        assert vm_dict['cpu_cores'] == 4
    
    def test_vm_from_dict(self):
        """Test VM deserialization"""
        data = {'id': 1, 'cpu_cores': 4, 'ram_gb': 16, 'storage_gb': 100, 'name': 'Test', 'metadata': {}}
        vm = VirtualMachine.from_dict(data)
        assert vm.id == 1
        assert vm.name == 'Test'


class TestServer:
    """Test cases for Server class"""
    
    def test_server_creation(self):
        """Test basic server creation"""
        server = Server(id=1, max_cpu_cores=64, max_ram_gb=256, max_storage_gb=2000)
        assert server.id == 1
        assert server.max_cpu_cores == 64
        assert len(server.vms) == 0
    
    def test_server_can_fit(self):
        """Test capacity checking"""
        server = Server(id=1, max_cpu_cores=16, max_ram_gb=64, max_storage_gb=500)
        vm = VirtualMachine(id=1, cpu_cores=4, ram_gb=16, storage_gb=100)
        
        assert server.can_fit(vm) is True
        
        # Add VM
        server.add_vm(vm)
        assert server.used_cpu == 4
        assert server.used_ram == 16
        assert server.used_storage == 100
    
    def test_server_add_vm(self):
        """Test adding VMs to server"""
        server = Server(id=1, max_cpu_cores=16, max_ram_gb=64, max_storage_gb=500)
        vm1 = VirtualMachine(id=1, cpu_cores=4, ram_gb=16, storage_gb=100)
        vm2 = VirtualMachine(id=2, cpu_cores=4, ram_gb=16, storage_gb=100)
        
        assert server.add_vm(vm1) is True
        assert server.add_vm(vm2) is True
        assert len(server.vms) == 2
    
    def test_server_overflow(self):
        """Test that oversized VMs are rejected"""
        server = Server(id=1, max_cpu_cores=8, max_ram_gb=32, max_storage_gb=200)
        large_vm = VirtualMachine(id=1, cpu_cores=16, ram_gb=64, storage_gb=500)
        
        assert server.can_fit(large_vm) is False
        assert server.add_vm(large_vm) is False
    
    def test_server_utilization(self):
        """Test utilization calculations"""
        server = Server(id=1, max_cpu_cores=16, max_ram_gb=64, max_storage_gb=500)
        vm = VirtualMachine(id=1, cpu_cores=8, ram_gb=32, storage_gb=250)
        server.add_vm(vm)
        
        assert server.utilization_cpu == 50.0
        assert server.utilization_ram == 50.0
        assert server.utilization_storage == 50.0
    
    def test_server_remove_vm(self):
        """Test removing VMs from server"""
        server = Server(id=1, max_cpu_cores=16, max_ram_gb=64, max_storage_gb=500)
        vm = VirtualMachine(id=1, cpu_cores=4, ram_gb=16, storage_gb=100)
        
        server.add_vm(vm)
        assert len(server.vms) == 1
        
        server.remove_vm(vm)
        assert len(server.vms) == 0


class TestSolution:
    """Test cases for Solution class"""
    
    def test_solution_creation(self):
        """Test basic solution creation"""
        solution = Solution()
        assert len(solution.servers) == 0
        assert solution.fitness is None
    
    def test_solution_num_servers(self):
        """Test counting used servers"""
        solution = Solution()
        server1 = Server(id=1, max_cpu_cores=16, max_ram_gb=64, max_storage_gb=500)
        server2 = Server(id=2, max_cpu_cores=16, max_ram_gb=64, max_storage_gb=500)
        
        vm = VirtualMachine(id=1, cpu_cores=4, ram_gb=16, storage_gb=100)
        server1.add_vm(vm)
        
        solution.servers = [server1, server2]
        assert solution.num_servers_used == 1  # Only server1 has VMs
    
    def test_solution_validity(self):
        """Test solution validation"""
        solution = Solution()
        server = Server(id=1, max_cpu_cores=16, max_ram_gb=64, max_storage_gb=500)
        vm = VirtualMachine(id=1, cpu_cores=4, ram_gb=16, storage_gb=100)
        
        server.add_vm(vm)
        solution.servers = [server]
        
        assert solution.is_valid() is True
    
    def test_solution_clone(self):
        """Test solution cloning"""
        solution = Solution()
        server = Server(id=1, max_cpu_cores=16, max_ram_gb=64, max_storage_gb=500)
        vm = VirtualMachine(id=1, cpu_cores=4, ram_gb=16, storage_gb=100)
        server.add_vm(vm)
        solution.servers = [server]
        
        cloned = solution.clone()
        assert cloned is not solution
        assert len(cloned.servers) == len(solution.servers)
    
    def test_solution_average_utilization(self):
        """Test average utilization calculation"""
        solution = Solution()
        server = Server(id=1, max_cpu_cores=16, max_ram_gb=64, max_storage_gb=500)
        vm = VirtualMachine(id=1, cpu_cores=8, ram_gb=32, storage_gb=250)
        server.add_vm(vm)
        solution.servers = [server]
        
        avg_util = solution.average_utilization
        assert avg_util['cpu'] == 50.0
        assert avg_util['ram'] == 50.0
        assert avg_util['storage'] == 50.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
