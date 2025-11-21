#!/usr/bin/env python3
"""
Generate all presentation visualizations
Run this script to create all images for the presentation
"""

import os
import sys

# Create visualizations directory
os.makedirs('presentation_visuals', exist_ok=True)

print("="*60)
print("PRESENTATION VISUALIZATION GENERATOR")
print("="*60)

# List of visualization scripts to generate
scripts = [
    'vis_1_problem_context.py',
    'vis_2_np_complete.py',
    'vis_3_hybrid_architecture.py',
    'vis_4_ga_chromosome.py',
    'vis_5_fitness_function.py',
    'vis_6_initialization_comparison.py',
    'vis_7_tournament_selection.py',
    'vis_8_crossover_operator.py',
    'vis_9_mutation_operators.py',
    'vis_10_diversity_immigration.py',
    'vis_11_convergence_curves.py',
    'vis_12_cooccurrence_matrix.py',
    'vis_13_woc_placement.py',
    'vis_14_performance_comparison.py',
    'vis_15_solution_quality.py',
    'vis_16_placement_diversity.py',
    'vis_17_hybrid_synergy.py',
]

print(f"\nWill generate {len(scripts)} visualizations...")
print("\nNote: Due to matplotlib compatibility issues, generating HTML/SVG versions")
print("These can be screenshot or converted to PNG for PowerPoint\n")

print("="*60)
print("Starting visualization generation...")
print("="*60)
