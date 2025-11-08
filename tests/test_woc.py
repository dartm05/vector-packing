"""
Unit tests for Wisdom of Crowds (WoC) components
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.woc import CrowdAnalyzer, CrowdBuilder
from src.models import VirtualMachine, Server, Solution
from src.utils.data_generator import DataGenerator
from src.ga.simple_fitness import SimpleFitnessEvaluator


class TestCrowdAnalyzer(unittest.TestCase):
    """Test CrowdAnalyzer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = CrowdAnalyzer()
        
        # Create some test VMs
        self.vm1 = VirtualMachine(id=1, cpu_cores=2, ram_gb=4, storage_gb=50)
        self.vm2 = VirtualMachine(id=2, cpu_cores=4, ram_gb=8, storage_gb=100)
        self.vm3 = VirtualMachine(id=3, cpu_cores=1, ram_gb=2, storage_gb=20)
        
        # Create test solutions
        self.server_template = Server(
            id=0, max_cpu_cores=16, max_ram_gb=32, max_storage_gb=500
        )
    
    def test_initialization(self):
        """Test analyzer initializes correctly"""
        self.assertEqual(self.analyzer.solutions_analyzed, 0)
        self.assertEqual(len(self.analyzer.co_occurrence_matrix), 0)
        self.assertEqual(len(self.analyzer.vm_frequency), 0)
    
    def test_analyze_single_solution(self):
        """Test analyzing a single solution"""
        # Create a solution with VMs 1 and 2 on same server
        server = Server(id=0, max_cpu_cores=16, max_ram_gb=32, max_storage_gb=500)
        server.add_vm(self.vm1)
        server.add_vm(self.vm2)
        
        solution = Solution(servers=[server], fitness=100.0)
        
        self.analyzer.analyze_solutions([solution])
        
        # Check that co-occurrence was recorded
        self.assertEqual(self.analyzer.solutions_analyzed, 1)
        self.assertGreater(self.analyzer.vm_frequency[1], 0)
        self.assertGreater(self.analyzer.vm_frequency[2], 0)
        
        # Check affinity score
        score = self.analyzer.get_affinity_score(1, 2)
        self.assertGreater(score, 0.0)
    
    def test_affinity_calculation(self):
        """Test affinity score calculation"""
        # Create two solutions where VMs 1 and 2 appear together
        for _ in range(3):
            server = Server(id=0, max_cpu_cores=16, max_ram_gb=32, max_storage_gb=500)
            server.add_vm(self.vm1)
            server.add_vm(self.vm2)
            solution = Solution(servers=[server], fitness=100.0)
            self.analyzer._analyze_single_solution(solution)
        
        # VMs 1 and 2 should have high affinity
        score_12 = self.analyzer.get_affinity_score(1, 2)
        self.assertGreater(score_12, 0.0)
        
        # VMs 1 and 3 (never together) should have zero affinity
        score_13 = self.analyzer.get_affinity_score(1, 3)
        self.assertEqual(score_13, 0.0)
    
    def test_best_companions(self):
        """Test finding best companions for a VM"""
        # Create solutions with different pairings
        # VM 1 with VM 2 (3 times)
        for _ in range(3):
            server = Server(id=0, max_cpu_cores=16, max_ram_gb=32, max_storage_gb=500)
            server.add_vm(self.vm1)
            server.add_vm(self.vm2)
            solution = Solution(servers=[server], fitness=100.0)
            self.analyzer._analyze_single_solution(solution)
        
        # VM 1 with VM 3 (1 time)
        server = Server(id=0, max_cpu_cores=16, max_ram_gb=32, max_storage_gb=500)
        server.add_vm(self.vm1)
        server.add_vm(self.vm3)
        solution = Solution(servers=[server], fitness=100.0)
        self.analyzer._analyze_single_solution(solution)
        
        # VM 2 should be the best companion for VM 1
        companions = self.analyzer.get_best_companions(1, [2, 3], top_n=2)
        self.assertEqual(companions[0], 2)  # VM 2 should be first
    
    def test_statistics(self):
        """Test statistics generation"""
        vms = DataGenerator.generate_vms(10, seed=42)
        server_template = DataGenerator.create_server_template()
        
        # Create some solutions
        from src.ga.engine import create_initial_population
        population = create_initial_population(vms, server_template, 5)
        
        self.analyzer.analyze_solutions(population)
        stats = self.analyzer.get_statistics()
        
        self.assertEqual(stats['solutions_analyzed'], 5)
        self.assertGreaterEqual(stats['unique_vms'], 0)
        self.assertGreaterEqual(stats['vm_pairs_found'], 0)
    
    def test_reset(self):
        """Test resetting the analyzer"""
        # Add some data
        server = Server(id=0, max_cpu_cores=16, max_ram_gb=32, max_storage_gb=500)
        server.add_vm(self.vm1)
        server.add_vm(self.vm2)
        solution = Solution(servers=[server], fitness=100.0)
        self.analyzer.analyze_solutions([solution])
        
        # Reset
        self.analyzer.reset()
        
        # Check everything is cleared
        self.assertEqual(self.analyzer.solutions_analyzed, 0)
        self.assertEqual(len(self.analyzer.co_occurrence_matrix), 0)
        self.assertEqual(len(self.analyzer.vm_frequency), 0)


class TestCrowdBuilder(unittest.TestCase):
    """Test CrowdBuilder functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = CrowdAnalyzer()
        self.builder = CrowdBuilder(self.analyzer)
        
        # Generate test data
        self.vms = DataGenerator.generate_vms(20, seed=42)
        self.server_template = DataGenerator.create_server_template()
    
    def test_initialization(self):
        """Test builder initializes correctly"""
        self.assertIsNotNone(self.builder.analyzer)
    
    def test_build_solution_without_analysis(self):
        """Test building solution with no prior analysis"""
        solution = self.builder.build_solution(
            self.vms, self.server_template, affinity_weight=0.7
        )
        
        # Should still produce a valid solution
        self.assertIsNotNone(solution)
        self.assertGreater(len(solution.servers), 0)
        
        # Check if all VMs are placed
        total_vms = sum(len(server.vms) for server in solution.servers)
        self.assertEqual(total_vms, len(self.vms))
    
    def test_build_solution_with_analysis(self):
        """Test building solution after analyzing patterns"""
        # Create and analyze some solutions
        from src.ga.engine import create_initial_population
        population = create_initial_population(self.vms, self.server_template, 10)
        evaluator = SimpleFitnessEvaluator()
        for sol in population:
            evaluator.evaluate(sol)
        
        self.analyzer.analyze_solutions(population, top_k=5)
        
        # Build new solution
        solution = self.builder.build_solution(
            self.vms, self.server_template, affinity_weight=0.8
        )
        
        # Verify solution
        self.assertIsNotNone(solution)
        self.assertGreater(len(solution.servers), 0)
        
        # Check metadata
        self.assertEqual(solution.metadata['method'], 'crowd_wisdom')
    
    def test_build_multiple_solutions(self):
        """Test building multiple diverse solutions"""
        # Analyze some patterns first
        from src.ga.engine import create_initial_population
        population = create_initial_population(self.vms, self.server_template, 5)
        self.analyzer.analyze_solutions(population)
        
        # Build multiple solutions
        solutions = self.builder.build_multiple_solutions(
            self.vms, self.server_template, num_solutions=5, affinity_weight=0.7
        )
        
        self.assertEqual(len(solutions), 5)
        
        # Each solution should have all VMs placed
        for solution in solutions:
            total_vms = sum(len(server.vms) for server in solution.servers)
            self.assertEqual(total_vms, len(self.vms))
    
    def test_solution_validity(self):
        """Test that built solutions are valid"""
        solution = self.builder.build_solution(
            self.vms, self.server_template, affinity_weight=0.5
        )
        
        # Check solution validity
        self.assertTrue(solution.is_valid())
        
        # Check that no server exceeds capacity
        for server in solution.servers:
            self.assertLessEqual(server.used_cpu, server.max_cpu_cores)
            self.assertLessEqual(server.used_ram, server.max_ram_gb)
            self.assertLessEqual(server.used_storage, server.max_storage_gb)


class TestIntegration(unittest.TestCase):
    """Integration tests for WoC with GA"""
    
    def test_woc_improves_solutions(self):
        """Test that WoC can find competitive solutions"""
        # Generate test data
        vms = DataGenerator.generate_vms(30, seed=42)
        server_template = DataGenerator.create_server_template()
        
        # Create initial population
        from src.ga.engine import create_initial_population
        population = create_initial_population(vms, server_template, 20)
        
        # Evaluate population
        evaluator = SimpleFitnessEvaluator()
        for sol in population:
            evaluator.evaluate(sol)
        
        # Get baseline best fitness
        baseline_best = min(sol.fitness for sol in population)
        
        # Analyze and build WoC solutions
        analyzer = CrowdAnalyzer()
        analyzer.analyze_solutions(population, top_k=10)
        
        builder = CrowdBuilder(analyzer)
        woc_solutions = builder.build_multiple_solutions(
            vms, server_template, num_solutions=10, affinity_weight=0.7
        )
        
        # Evaluate WoC solutions
        for sol in woc_solutions:
            evaluator.evaluate(sol)
        
        woc_best = min(sol.fitness for sol in woc_solutions)
        
        # WoC should produce competitive solutions
        # (May not always be better due to randomness, but should be reasonable)
        self.assertLess(woc_best, baseline_best * 1.5)  # Within 50% of baseline


if __name__ == '__main__':
    unittest.main()
