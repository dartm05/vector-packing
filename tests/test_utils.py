"""
Unit tests for utility functions
"""

import pytest
from src.utils import DataGenerator, InitializationStrategy
from src.models import VirtualMachine, Server


class TestDataGenerator:
    """Test cases for DataGenerator"""
    
    def test_generate_vms(self):
        """Test VM generation"""
        vms = DataGenerator.generate_vms(num_vms=10, seed=42)
        assert len(vms) == 10
        assert all(isinstance(vm, VirtualMachine) for vm in vms)
    
    def test_generate_vms_reproducible(self):
        """Test that generation with same seed is reproducible"""
        vms1 = DataGenerator.generate_vms(num_vms=10, seed=42)
        vms2 = DataGenerator.generate_vms(num_vms=10, seed=42)
        
        for vm1, vm2 in zip(vms1, vms2):
            assert vm1.cpu_cores == vm2.cpu_cores
            assert vm1.ram_gb == vm2.ram_gb
            assert vm1.storage_gb == vm2.storage_gb
    
    def test_generate_vms_with_patterns(self):
        """Test pattern-based VM generation"""
        vms = DataGenerator.generate_vms_with_patterns(
            num_vms=20,
            pattern_type='mixed',
            seed=42
        )
        assert len(vms) == 20
    
    def test_create_server_template(self):
        """Test server template creation"""
        server = DataGenerator.create_server_template(
            cpu_cores=64,
            ram_gb=256,
            storage_gb=2000
        )
        assert server.max_cpu_cores == 64
        assert server.max_ram_gb == 256
        assert server.max_storage_gb == 2000
    
    def test_generate_scenario(self):
        """Test scenario generation"""
        scenario = DataGenerator.generate_scenario('small', seed=42)
        
        assert 'vms' in scenario
        assert 'server_template' in scenario
        assert 'scenario_name' in scenario
        assert scenario['scenario_name'] == 'small'
        assert len(scenario['vms']) > 0


class TestInitializationStrategy:
    """Test cases for InitializationStrategy"""
    
    def setup_method(self):
        """Setup test data"""
        self.vms = [
            VirtualMachine(id=i, cpu_cores=4, ram_gb=16, storage_gb=100)
            for i in range(10)
        ]
        self.server_template = Server(
            id=0,
            max_cpu_cores=16,
            max_ram_gb=64,
            max_storage_gb=500
        )
    
    def test_random_initialization(self):
        """Test random initialization"""
        solution = InitializationStrategy.random_initialization(
            self.vms, self.server_template
        )
        assert solution.total_vms == len(self.vms)
        assert solution.is_valid()
    
    def test_first_fit_decreasing(self):
        """Test first-fit decreasing initialization"""
        solution = InitializationStrategy.first_fit_decreasing(
            self.vms, self.server_template, sort_by='cpu'
        )
        assert solution.total_vms == len(self.vms)
        assert solution.is_valid()
    
    def test_best_fit(self):
        """Test best-fit initialization"""
        solution = InitializationStrategy.best_fit(
            self.vms, self.server_template
        )
        assert solution.total_vms == len(self.vms)
        assert solution.is_valid()
    
    def test_get_strategy(self):
        """Test strategy retrieval"""
        strategy = InitializationStrategy.get_strategy('random')
        assert callable(strategy)
        
        solution = strategy(self.vms, self.server_template)
        assert solution.total_vms == len(self.vms)
    
    def test_invalid_strategy(self):
        """Test that invalid strategy name raises error"""
        with pytest.raises(ValueError):
            InitializationStrategy.get_strategy('invalid_strategy')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
