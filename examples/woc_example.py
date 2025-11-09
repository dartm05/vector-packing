"""
Example of using Wisdom of Crowds (WoC) with Genetic Algorithm

This script demonstrates how to integrate CrowdAnalyzer and CrowdBuilder
into the GA optimization process, with visualizations and GUI.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import VirtualMachine, Server, Solution
from src.ga.engine import run_ga
from src.woc import CrowdAnalyzer, CrowdBuilder
from src.utils.data_generator import DataGenerator
from src.ga.simple_fitness import SimpleFitnessEvaluator

# Visualization imports
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def demonstrate_woc_integration():
    """
    Demonstrates how to use WoC components with the GA.
    
    Process:
    1. Run GA to get a population of solutions
    2. Use CrowdAnalyzer to learn VM affinity patterns
    3. Use CrowdBuilder to generate new solutions based on patterns
    4. Compare results
    """
    print("=" * 70)
    print("Wisdom of Crowds (WoC) Integration Example")
    print("=" * 70)
    
    # Step 1: Generate test data
    print("\n[1] Generating test data...")
    vms = DataGenerator.generate_vms(num_vms=30, seed=42)
    server_template = DataGenerator.create_server_template()
    
    print(f"  - Generated {len(vms)} VMs")
    print(f"  - Server capacity: {server_template.max_cpu_cores} cores, "
          f"{server_template.max_ram_gb} GB RAM, {server_template.max_storage_gb} GB storage")
    
    # Step 2: Run GA to get initial population
    print("\n[2] Running Genetic Algorithm...")
    best_solution = run_ga(
        vms=vms,
        server_template=server_template,
        population_size=50,
        generations=20
    )
    
    print(f"  - Best GA solution uses {best_solution.num_servers_used} servers")
    print(f"  - Fitness: {best_solution.fitness:.2f}")
    
    # Generate a population to analyze (simulate multiple GA runs)
    print("  - Generating additional solutions for analysis...")
    from src.ga.engine import create_initial_population
    fitness_evaluator = SimpleFitnessEvaluator()
    population = create_initial_population(vms, server_template, 30)
    for sol in population:
        fitness_evaluator.evaluate(sol)
    population.append(best_solution)  # Include the best GA solution
    
    # Step 3: Analyze the population with CrowdAnalyzer
    print("\n[3] Analyzing population with CrowdAnalyzer...")
    analyzer = CrowdAnalyzer()
    analyzer.analyze_solutions(population, top_k=20)  # Analyze top 20 solutions
    
    stats = analyzer.get_statistics()
    print(f"  - Solutions analyzed: {stats['solutions_analyzed']}")
    print(f"  - Unique VMs found: {stats['unique_vms']}")
    print(f"  - VM pairs discovered: {stats['vm_pairs_found']}")
    print(f"  - Avg co-occurrence: {stats['avg_co_occurrence']:.2f}")
    
    # Step 4: Build new solutions using CrowdBuilder
    print("\n[4] Building new solutions with CrowdBuilder...")
    builder = CrowdBuilder(analyzer)
    
    # Build 10 new solutions with different affinity weights
    crowd_solutions = builder.build_multiple_solutions(
        vms=vms,
        server_template=server_template,
        num_solutions=10,
        affinity_weight=0.7
    )
    
    # Evaluate the crowd-built solutions
    for solution in crowd_solutions:
        fitness_evaluator.evaluate(solution)
    
    # Find the best crowd solution
    best_crowd_solution = min(crowd_solutions, key=lambda s: s.fitness)
    
    print(f"  - Generated {len(crowd_solutions)} crowd-based solutions")
    print(f"  - Best crowd solution uses {best_crowd_solution.num_servers_used} servers")
    print(f"  - Fitness: {best_crowd_solution.fitness:.2f}")
    
    # Step 5: Compare results
    print("\n[5] Comparison:")
    print(f"  GA Best:    {best_solution.num_servers_used} servers, fitness = {best_solution.fitness:.2f}")
    print(f"  WoC Best:   {best_crowd_solution.num_servers_used} servers, fitness = {best_crowd_solution.fitness:.2f}")
    
    if best_crowd_solution.fitness < best_solution.fitness:
        improvement = ((best_solution.fitness - best_crowd_solution.fitness) / best_solution.fitness) * 100
        print(f"  🎉 WoC improved by {improvement:.2f}%!")
    elif best_crowd_solution.fitness == best_solution.fitness:
        print(f"  ⚖️  Both approaches achieved the same fitness!")
    else:
        print(f"  📊 GA still ahead, but WoC provides diverse alternatives.")
    
    # Step 6: Show some affinity patterns
    print("\n[6] Sample VM Affinity Patterns:")
    if len(vms) >= 5:
        for i in range(min(3, len(vms))):
            vm = vms[i]
            companions = analyzer.get_best_companions(vm.id, [v.id for v in vms], top_n=3)
            if companions:
                print(f"  VM {vm.id} works well with: {companions}")
                for comp_id in companions[:2]:
                    score = analyzer.get_affinity_score(vm.id, comp_id)
                    print(f"    - VM {comp_id}: affinity score = {score:.3f}")
    
    print("\n" + "=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


def visualize_solution(solution: Solution, title: str = "Solution Visualization"):
    """
    Visualize a single solution showing server utilization.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Extract data
    servers = [s for s in solution.servers if len(s.vms) > 0]
    server_ids = [f"S{s.id}" for s in servers]
    cpu_utils = [s.utilization_cpu for s in servers]
    ram_utils = [s.utilization_ram for s in servers]
    storage_utils = [s.utilization_storage for s in servers]
    
    # 1. Server utilization bar chart
    ax1 = axes[0, 0]
    x = np.arange(len(server_ids))
    width = 0.25
    
    ax1.bar(x - width, cpu_utils, width, label='CPU', color='#FF6B6B')
    ax1.bar(x, ram_utils, width, label='RAM', color='#4ECDC4')
    ax1.bar(x + width, storage_utils, width, label='Storage', color='#45B7D1')
    
    ax1.set_xlabel('Servers')
    ax1.set_ylabel('Utilization (%)')
    ax1.set_title('Resource Utilization per Server')
    ax1.set_xticks(x)
    ax1.set_xticklabels(server_ids, rotation=45)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim(0, 100)
    
    # 2. VM distribution heatmap
    ax2 = axes[0, 1]
    if servers:
        vm_counts = [len(s.vms) for s in servers]
        colors = plt.cm.viridis(np.linspace(0, 1, len(servers)))
        ax2.barh(server_ids, vm_counts, color=colors)
        ax2.set_xlabel('Number of VMs')
        ax2.set_title('VMs per Server')
        ax2.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (count, color) in enumerate(zip(vm_counts, colors)):
            ax2.text(count, i, f' {count}', va='center', fontweight='bold')
    
    # 3. Average utilization pie chart
    ax3 = axes[1, 0]
    avg_utils = solution.average_utilization
    util_data = [avg_utils['cpu'], avg_utils['ram'], avg_utils['storage']]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    wedges, texts, autotexts = ax3.pie(
        util_data, 
        labels=['CPU', 'RAM', 'Storage'],
        autopct='%1.1f%%',
        colors=colors,
        startangle=90
    )
    ax3.set_title('Average Resource Utilization')
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # 4. Solution statistics
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    stats_text = f"""
    Solution Statistics
    {'='*40}
    
    Servers Used: {solution.num_servers_used}
    Total VMs: {solution.total_vms}
    Fitness Score: {solution.fitness:.2f}
    
    Average Utilization:
      • CPU:     {avg_utils['cpu']:.1f}%
      • RAM:     {avg_utils['ram']:.1f}%
      • Storage: {avg_utils['storage']:.1f}%
    
    Solution Valid: {'✓ Yes' if solution.is_valid() else '✗ No'}
    Generation: {solution.generation}
    """
    
    ax4.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
             verticalalignment='center', bbox=dict(boxstyle='round', 
             facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    return fig


def visualize_affinity_matrix(analyzer: CrowdAnalyzer, vms: list, top_n: int = 15):
    """
    Visualize VM affinity matrix as a heatmap.
    """
    # Select top N VMs by frequency
    vm_ids = sorted(analyzer.vm_frequency.keys(), 
                   key=lambda x: analyzer.vm_frequency[x], 
                   reverse=True)[:top_n]
    
    if not vm_ids:
        print("No affinity data to visualize")
        return None
    
    # Build affinity matrix
    n = len(vm_ids)
    matrix = np.zeros((n, n))
    
    for i, vm1 in enumerate(vm_ids):
        for j, vm2 in enumerate(vm_ids):
            if i != j:
                matrix[i, j] = analyzer.get_affinity_score(vm1, vm2)
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 10))
    
    im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)
    
    # Set ticks
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels([f'VM{vid}' for vid in vm_ids], rotation=45, ha='right')
    ax.set_yticklabels([f'VM{vid}' for vid in vm_ids])
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Affinity Score', rotation=270, labelpad=20)
    
    # Add text annotations
    for i in range(n):
        for j in range(n):
            if matrix[i, j] > 0.1:  # Only show significant affinities
                text = ax.text(j, i, f'{matrix[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=8)
    
    ax.set_title('VM Co-location Affinity Matrix\n(Higher scores = VMs work well together)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Virtual Machine ID')
    ax.set_ylabel('Virtual Machine ID')
    
    plt.tight_layout()
    return fig


def compare_solutions_visual(ga_solution: Solution, woc_solution: Solution):
    """
    Visual comparison of GA vs WoC solutions.
    """
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('GA vs WoC Solution Comparison', fontsize=16, fontweight='bold')
    
    solutions = [ga_solution, woc_solution]
    titles = ['GA Solution', 'WoC Solution']
    
    for idx, (solution, title) in enumerate(zip(solutions, titles)):
        # Server count
        ax = axes[idx, 0]
        ax.bar([title], [solution.num_servers_used], color=['#3498db', '#e74c3c'][idx])
        ax.set_ylabel('Number of Servers')
        ax.set_title('Servers Used')
        ax.grid(axis='y', alpha=0.3)
        
        # Fitness score
        ax = axes[idx, 1]
        ax.bar([title], [solution.fitness], color=['#3498db', '#e74c3c'][idx])
        ax.set_ylabel('Fitness Score (lower is better)')
        ax.set_title('Fitness Score')
        ax.grid(axis='y', alpha=0.3)
        
        # Resource utilization
        ax = axes[idx, 2]
        utils = solution.average_utilization
        resources = ['CPU', 'RAM', 'Storage']
        values = [utils['cpu'], utils['ram'], utils['storage']]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        ax.bar(resources, values, color=colors)
        ax.set_ylabel('Utilization (%)')
        ax.set_title('Average Utilization')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(values):
            ax.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    return fig


class WoCGUI:
    """
    Interactive GUI for WoC demonstration.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Wisdom of Crowds (WoC) Visualization")
        self.root.geometry("1400x900")
        
        # Data storage
        self.vms = None
        self.server_template = None
        self.ga_solution = None
        self.woc_solution = None
        self.analyzer = None
        self.population = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the GUI layout."""
        # Control Panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N))
        
        # Title
        title = ttk.Label(control_frame, text="WoC Visualization Tool", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=4, pady=10)
        
        # Parameters
        ttk.Label(control_frame, text="Number of VMs:").grid(row=1, column=0, sticky=tk.W)
        self.vm_count = ttk.Entry(control_frame, width=10)
        self.vm_count.insert(0, "30")
        self.vm_count.grid(row=1, column=1, padx=5)
        
        ttk.Label(control_frame, text="GA Generations:").grid(row=1, column=2, sticky=tk.W)
        self.generations = ttk.Entry(control_frame, width=10)
        self.generations.insert(0, "20")
        self.generations.grid(row=1, column=3, padx=5)
        
        ttk.Label(control_frame, text="Population Size:").grid(row=2, column=0, sticky=tk.W)
        self.pop_size = ttk.Entry(control_frame, width=10)
        self.pop_size.insert(0, "50")
        self.pop_size.grid(row=2, column=1, padx=5)
        
        ttk.Label(control_frame, text="Affinity Weight:").grid(row=2, column=2, sticky=tk.W)
        self.affinity_weight = ttk.Entry(control_frame, width=10)
        self.affinity_weight.insert(0, "0.7")
        self.affinity_weight.grid(row=2, column=3, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="🚀 Run GA", 
                  command=self.run_ga).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧠 Run WoC", 
                  command=self.run_woc).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Show GA Solution", 
                  command=self.show_ga_solution).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📈 Show WoC Solution", 
                  command=self.show_woc_solution).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔍 Show Affinity", 
                  command=self.show_affinity).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⚖️ Compare", 
                  command=self.compare_solutions).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status = ttk.Label(control_frame, text="Ready", 
                               relief=tk.SUNKEN, anchor=tk.W)
        self.status.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(self.root, text="Results", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Text widget with scrollbar
        text_scroll = ttk.Scrollbar(results_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(results_frame, height=15, width=80, 
                                   yscrollcommand=text_scroll.set, font=('Courier', 10))
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.results_text.yview)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
    def log(self, message):
        """Log message to results text."""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update()
        
    def run_ga(self):
        """Run the Genetic Algorithm."""
        try:
            self.status.config(text="Running GA...")
            self.results_text.delete(1.0, tk.END)
            
            # Generate data
            num_vms = int(self.vm_count.get())
            gens = int(self.generations.get())
            pop_size = int(self.pop_size.get())
            
            self.log("=" * 70)
            self.log("GENETIC ALGORITHM")
            self.log("=" * 70)
            self.log(f"\n[1] Generating {num_vms} VMs...")
            
            self.vms = DataGenerator.generate_vms(num_vms=num_vms, seed=42)
            self.server_template = DataGenerator.create_server_template()
            
            self.log(f"  ✓ Generated {len(self.vms)} VMs")
            self.log(f"  ✓ Server capacity: {self.server_template.max_cpu_cores} cores, "
                    f"{self.server_template.max_ram_gb} GB RAM")
            
            # Run GA
            self.log(f"\n[2] Running GA ({gens} generations, population {pop_size})...")
            self.ga_solution = run_ga(
                vms=self.vms,
                server_template=self.server_template,
                population_size=pop_size,
                generations=gens
            )
            
            self.log(f"\n✅ GA Complete!")
            self.log(f"  • Servers used: {self.ga_solution.num_servers_used}")
            self.log(f"  • Fitness: {self.ga_solution.fitness:.2f}")
            self.log(f"  • Valid: {self.ga_solution.is_valid()}")
            
            # Generate population for WoC
            from src.ga.engine import create_initial_population
            fitness_evaluator = SimpleFitnessEvaluator()
            self.population = create_initial_population(self.vms, self.server_template, 30)
            for sol in self.population:
                fitness_evaluator.evaluate(sol)
            self.population.append(self.ga_solution)
            
            self.status.config(text="GA completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"GA failed: {str(e)}")
            self.status.config(text="GA failed!")
            
    def run_woc(self):
        """Run the Wisdom of Crowds analysis."""
        if self.vms is None or self.population is None:
            messagebox.showwarning("Warning", "Please run GA first!")
            return
            
        try:
            self.status.config(text="Running WoC...")
            self.log("\n" + "=" * 70)
            self.log("WISDOM OF CROWDS")
            self.log("=" * 70)
            
            # Analyze
            self.log("\n[1] Analyzing population...")
            self.analyzer = CrowdAnalyzer()
            self.analyzer.analyze_solutions(self.population, top_k=20)
            
            stats = self.analyzer.get_statistics()
            self.log(f"  ✓ Solutions analyzed: {stats['solutions_analyzed']}")
            self.log(f"  ✓ Unique VMs: {stats['unique_vms']}")
            self.log(f"  ✓ VM pairs discovered: {stats['vm_pairs_found']}")
            self.log(f"  ✓ Avg co-occurrence: {stats['avg_co_occurrence']:.2f}")
            
            # Build solutions
            self.log("\n[2] Building WoC solutions...")
            builder = CrowdBuilder(self.analyzer)
            affinity_w = float(self.affinity_weight.get())
            
            crowd_solutions = builder.build_multiple_solutions(
                vms=self.vms,
                server_template=self.server_template,
                num_solutions=10,
                affinity_weight=affinity_w
            )
            
            # Evaluate
            fitness_evaluator = SimpleFitnessEvaluator()
            for solution in crowd_solutions:
                fitness_evaluator.evaluate(solution)
            
            self.woc_solution = min(crowd_solutions, key=lambda s: s.fitness)
            
            self.log(f"\n✅ WoC Complete!")
            self.log(f"  • Solutions generated: {len(crowd_solutions)}")
            self.log(f"  • Best servers used: {self.woc_solution.num_servers_used}")
            self.log(f"  • Best fitness: {self.woc_solution.fitness:.2f}")
            self.log(f"  • Valid: {self.woc_solution.is_valid()}")
            
            # Comparison
            if self.ga_solution:
                self.log("\n" + "=" * 70)
                self.log("COMPARISON")
                self.log("=" * 70)
                self.log(f"  GA:  {self.ga_solution.num_servers_used} servers, "
                        f"fitness = {self.ga_solution.fitness:.2f}")
                self.log(f"  WoC: {self.woc_solution.num_servers_used} servers, "
                        f"fitness = {self.woc_solution.fitness:.2f}")
                
                if self.woc_solution.fitness < self.ga_solution.fitness:
                    improvement = ((self.ga_solution.fitness - self.woc_solution.fitness) / 
                                 self.ga_solution.fitness) * 100
                    self.log(f"  🎉 WoC improved by {improvement:.2f}%!")
                elif self.woc_solution.fitness == self.ga_solution.fitness:
                    self.log(f"  ⚖️ Both achieved the same fitness!")
                else:
                    self.log(f"  📊 GA still ahead, but WoC provides alternatives.")
            
            self.status.config(text="WoC completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"WoC failed: {str(e)}")
            self.status.config(text="WoC failed!")
            
    def show_ga_solution(self):
        """Show GA solution visualization."""
        if self.ga_solution is None:
            messagebox.showwarning("Warning", "Please run GA first!")
            return
        fig = visualize_solution(self.ga_solution, "GA Solution")
        plt.show()
        
    def show_woc_solution(self):
        """Show WoC solution visualization."""
        if self.woc_solution is None:
            messagebox.showwarning("Warning", "Please run WoC first!")
            return
        fig = visualize_solution(self.woc_solution, "WoC Solution")
        plt.show()
        
    def show_affinity(self):
        """Show affinity matrix."""
        if self.analyzer is None:
            messagebox.showwarning("Warning", "Please run WoC first!")
            return
        fig = visualize_affinity_matrix(self.analyzer, self.vms, top_n=15)
        if fig:
            plt.show()
        
    def compare_solutions(self):
        """Compare GA and WoC solutions."""
        if self.ga_solution is None or self.woc_solution is None:
            messagebox.showwarning("Warning", "Please run both GA and WoC first!")
            return
        fig = compare_solutions_visual(self.ga_solution, self.woc_solution)
        plt.show()


def run_gui():
    """Launch the GUI application."""
    root = tk.Tk()
    app = WoCGUI(root)
    root.mainloop()


def run_ga_with_woc_injection(vms, server_template, inject_every=5):
    """
    Advanced integration: Periodically inject WoC solutions into GA population.
    
    This is a conceptual example showing how WoC could be integrated
    during the GA run (not fully implemented in the base engine).
    """
    print("\n[Advanced] GA with periodic WoC injection")
    print("This would inject crowd-based solutions every N generations")
    print("to maintain diversity and leverage learned patterns.")
    print("(Implementation would require modifying the GA engine)")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        # Run console demonstration
        demonstrate_woc_integration()
    else:
        # Launch GUI mode (default)
        print("Launching WoC GUI...")
        run_gui()
