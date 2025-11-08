"""
Crowd Analyzer - Discovers patterns in successful solutions

This module analyzes a collection of good solutions to identify
which VMs tend to be placed together on the same server.
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict
from ..models import Solution, VirtualMachine


class CrowdAnalyzer:
    """
    Analyzes patterns in successful solutions to discover VM co-location preferences.
    
    The "wisdom" comes from observing which VMs are frequently packed together
    in high-quality solutions, suggesting they have complementary resource profiles.
    """
    
    def __init__(self):
        """Initialize the analyzer with empty co-occurrence tracking"""
        self.co_occurrence_matrix: Dict[Tuple[int, int], int] = defaultdict(int)
        self.vm_frequency: Dict[int, int] = defaultdict(int)
        self.solutions_analyzed: int = 0
        
    def analyze_solutions(self, solutions: List[Solution], top_k: int = None) -> None:
        """
        Analyze a population of solutions to identify VM co-location patterns.
        
        Args:
            solutions: List of solutions to analyze
            top_k: If specified, only analyze the top_k best solutions
        """
        # Sort by fitness (lower is better) and take top_k if specified
        sorted_solutions = sorted(solutions, key=lambda s: s.fitness if s.fitness else float('inf'))
        
        if top_k:
            sorted_solutions = sorted_solutions[:top_k]
        
        # Analyze each solution
        for solution in sorted_solutions:
            self._analyze_single_solution(solution)
            self.solutions_analyzed += 1
    
    def _analyze_single_solution(self, solution: Solution) -> None:
        """
        Analyze a single solution to record VM co-locations.
        
        For each server with multiple VMs, we record that those VMs
        appear together, incrementing their co-occurrence count.
        """
        for server in solution.servers:
            if len(server.vms) < 2:
                continue  # Skip servers with 0 or 1 VM
            
            vm_ids = [vm.id for vm in server.vms]
            
            # Record each VM's frequency
            for vm_id in vm_ids:
                self.vm_frequency[vm_id] += 1
            
            # Record co-occurrences between all pairs on this server
            for i, vm_id1 in enumerate(vm_ids):
                for vm_id2 in vm_ids[i+1:]:
                    # Use sorted tuple as key to avoid duplication (e.g., (1,2) and (2,1))
                    pair = tuple(sorted([vm_id1, vm_id2]))
                    self.co_occurrence_matrix[pair] += 1
    
    def get_affinity_score(self, vm1_id: int, vm2_id: int) -> float:
        """
        Calculate how often two VMs appear together relative to their individual frequencies.
        
        Returns:
            A score between 0 and 1, where higher means stronger affinity.
            Uses Jaccard-like similarity: co-occurrences / (freq1 + freq2 - co-occurrences)
        """
        pair = tuple(sorted([vm1_id, vm2_id]))
        co_count = self.co_occurrence_matrix.get(pair, 0)
        
        if co_count == 0:
            return 0.0
        
        freq1 = self.vm_frequency.get(vm1_id, 0)
        freq2 = self.vm_frequency.get(vm2_id, 0)
        
        # Avoid division by zero
        denominator = freq1 + freq2 - co_count
        if denominator == 0:
            return 0.0
        
        return co_count / denominator
    
    def get_best_companions(self, vm_id: int, candidate_ids: List[int], top_n: int = 5) -> List[int]:
        """
        Find the VMs with highest affinity to a given VM from a list of candidates.
        
        Args:
            vm_id: The VM to find companions for
            candidate_ids: List of VM IDs to consider as potential companions
            top_n: Number of top companions to return
            
        Returns:
            List of VM IDs sorted by affinity score (highest first)
        """
        if not candidate_ids:
            return []
        
        # Calculate affinity scores for all candidates
        scores = []
        for candidate_id in candidate_ids:
            if candidate_id != vm_id:  # Don't compare VM with itself
                score = self.get_affinity_score(vm_id, candidate_id)
                scores.append((candidate_id, score))
        
        # Sort by score (descending) and return top_n
        scores.sort(key=lambda x: x[1], reverse=True)
        return [vm_id for vm_id, _ in scores[:top_n]]
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about the analyzed patterns.
        
        Returns:
            Dictionary with analysis statistics
        """
        if not self.co_occurrence_matrix:
            return {
                'solutions_analyzed': self.solutions_analyzed,
                'unique_vms': 0,
                'vm_pairs_found': 0,
                'avg_co_occurrence': 0.0
            }
        
        total_co_occurrences = sum(self.co_occurrence_matrix.values())
        num_pairs = len(self.co_occurrence_matrix)
        
        return {
            'solutions_analyzed': self.solutions_analyzed,
            'unique_vms': len(self.vm_frequency),
            'vm_pairs_found': num_pairs,
            'avg_co_occurrence': total_co_occurrences / num_pairs if num_pairs > 0 else 0.0,
            'max_co_occurrence': max(self.co_occurrence_matrix.values()) if self.co_occurrence_matrix else 0
        }
    
    def reset(self) -> None:
        """Clear all analyzed data and start fresh"""
        self.co_occurrence_matrix.clear()
        self.vm_frequency.clear()
        self.solutions_analyzed = 0
