#!/usr/bin/env python3
"""
Test script to compare GA vs WOC performance
Runs both approaches and analyzes the results
"""

from src.utils.data_generator import DataGenerator
from src.ga.engine import run_ga, create_initial_population
from src.woc.engine import run_woc


def test_ga_vs_woc():
    """Compare GA and WOC on different problem sizes."""
    
    print("="*80)
    print("GENETIC ALGORITHM vs WISDOM OF CROWDS - COMPARISON TEST")
    print("="*80)
    
    scenarios = ['small', 'medium']
    results = []
    
    for scenario_name in scenarios:
        print(f"\n{'='*80}")
        print(f"Testing scenario: {scenario_name.upper()}")
        print(f"{'='*80}\n")
        
        # Generate test data
        scenario = DataGenerator.generate_scenario(scenario_name, seed=42)
        vms = scenario['vms']
        server_template = scenario['server_template']
        
        print(f"Problem size: {len(vms)} VMs")
        print(f"Server capacity: {server_template.max_cpu_cores} cores, "
              f"{server_template.max_ram_gb} GB RAM, "
              f"{server_template.max_storage_gb} GB storage\n")
        
        # --- Run Genetic Algorithm ---
        print("Phase 1: Running Genetic Algorithm...")
        best_ga = run_ga(
            vms=vms,
            server_template=server_template,
            population_size=50,
            generations=50,
            elitism_count=2,
            mutation_rate=0.3,
            tournament_k=3,
            use_local_search=False
        )
        
        # --- Run Wisdom of Crowds ---
        print("\nPhase 2: Running Wisdom of Crowds...")
        
        # Create population for WOC to learn from
        ga_population = create_initial_population(vms, server_template, 50)
        
        best_woc = run_woc(
            vms=vms,
            server_template=server_template,
            ga_population=ga_population,
            top_n=20,
            num_solutions=30
        )
        
        # --- Compare Results ---
        print(f"\n{'='*80}")
        print(f"RESULTS COMPARISON - {scenario_name.upper()}")
        print(f"{'='*80}")
        
        print(f"\n{'Metric':<30} {'GA':<20} {'WOC':<20} {'Winner':<10}")
        print("-" * 80)
        
        # Servers used
        ga_servers = best_ga.num_servers_used
        woc_servers = best_woc.num_servers_used
        server_winner = "WOC" if woc_servers < ga_servers else ("GA" if ga_servers < woc_servers else "TIE")
        print(f"{'Servers Used':<30} {ga_servers:<20} {woc_servers:<20} {server_winner:<10}")
        
        # Fitness score
        ga_fitness = best_ga.fitness
        woc_fitness = best_woc.fitness
        fitness_winner = "WOC" if woc_fitness < ga_fitness else ("GA" if ga_fitness < woc_fitness else "TIE")
        print(f"{'Fitness Score (lower=better)':<30} {ga_fitness:<20.2f} {woc_fitness:<20.2f} {fitness_winner:<10}")
        
        # Utilization
        ga_util = best_ga.average_utilization
        woc_util = best_woc.average_utilization
        ga_avg_util = (ga_util['cpu'] + ga_util['ram'] + ga_util['storage']) / 3
        woc_avg_util = (woc_util['cpu'] + woc_util['ram'] + woc_util['storage']) / 3
        util_winner = "WOC" if woc_avg_util > ga_avg_util else ("GA" if ga_avg_util > woc_avg_util else "TIE")
        print(f"{'Average Utilization (%)':<30} {ga_avg_util:<20.2f} {woc_avg_util:<20.2f} {util_winner:<10}")
        
        # CPU utilization
        cpu_winner = "WOC" if woc_util['cpu'] > ga_util['cpu'] else ("GA" if ga_util['cpu'] > woc_util['cpu'] else "TIE")
        print(f"{'  - CPU Utilization (%)':<30} {ga_util['cpu']:<20.2f} {woc_util['cpu']:<20.2f} {cpu_winner:<10}")
        
        # RAM utilization
        ram_winner = "WOC" if woc_util['ram'] > ga_util['ram'] else ("GA" if ga_util['ram'] > woc_util['ram'] else "TIE")
        print(f"{'  - RAM Utilization (%)':<30} {ga_util['ram']:<20.2f} {woc_util['ram']:<20.2f} {ram_winner:<10}")
        
        # Storage utilization
        storage_winner = "WOC" if woc_util['storage'] > ga_util['storage'] else ("GA" if ga_util['storage'] > woc_util['storage'] else "TIE")
        print(f"{'  - Storage Utilization (%)':<30} {ga_util['storage']:<20.2f} {woc_util['storage']:<20.2f} {storage_winner:<10}")
        
        # Validity
        print(f"{'Valid Solution':<30} {'YES' if best_ga.is_valid() else 'NO':<20} {'YES' if best_woc.is_valid() else 'NO':<20} {'-':<10}")
        
        # Store results
        results.append({
            'scenario': scenario_name,
            'ga': {
                'servers': ga_servers,
                'fitness': ga_fitness,
                'utilization': ga_avg_util
            },
            'woc': {
                'servers': woc_servers,
                'fitness': woc_fitness,
                'utilization': woc_avg_util
            },
            'winner': fitness_winner
        })
        
        print()
    
    # --- Overall Summary ---
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}\n")
    
    ga_wins = sum(1 for r in results if r['winner'] == 'GA')
    woc_wins = sum(1 for r in results if r['winner'] == 'WOC')
    ties = sum(1 for r in results if r['winner'] == 'TIE')
    
    print(f"Scenarios tested: {len(results)}")
    print(f"GA wins: {ga_wins}")
    print(f"WOC wins: {woc_wins}")
    print(f"Ties: {ties}")
    
    if woc_wins > ga_wins:
        print(f"\n🏆 WISDOM OF CROWDS performed better overall!")
    elif ga_wins > woc_wins:
        print(f"\n🏆 GENETIC ALGORITHM performed better overall!")
    else:
        print(f"\n🤝 Both approaches performed equally well!")
    
    print("\nKey Insights:")
    print("- GA uses evolutionary search to explore the solution space")
    print("- WOC learns patterns from successful solutions and builds new ones")
    print("- Combining both approaches can leverage their respective strengths")
    print("- For harder problems, WOC may discover patterns GA missed")
    
    print(f"\n{'='*80}")
    print("✨ Test Complete!")
    print(f"{'='*80}")


if __name__ == "__main__":
    test_ga_vs_woc()
