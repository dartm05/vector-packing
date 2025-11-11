#!/usr/bin/env python3
"""
GUI Application for GA and WoC Vector Packing Solver

This application provides a graphical user interface to run and compare
Genetic Algorithm and Wisdom of Crowds approaches for VM placement.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import Solution
from src.ga.engine import run_ga, create_initial_population
from src.woc import CrowdAnalyzer, CrowdBuilder
from src.utils.data_generator import DataGenerator
from src.ga.simple_fitness import SimpleFitnessEvaluator


class VectorPackingGUI:
    """Main GUI application for Vector Packing Solver"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Vector Packing Solver - GA & WoC")
        self.root.geometry("1200x800")
        
        # State variables
        self.is_running = False
        self.best_ga_solution = None
        self.best_woc_solution = None
        self.ga_population = None  # Store entire GA population for WoC
        self.vms = None
        self.server_template = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Vector Packing Solver - GA & WoC", 
            font=('Helvetica', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Left panel - Configuration
        self.setup_config_panel(main_frame)
        
        # Right panel - Results and visualization
        self.setup_results_panel(main_frame)
        
        # Bottom panel - Control buttons
        self.setup_control_panel(main_frame)
        
    def setup_config_panel(self, parent):
        """Setup configuration panel"""
        config_frame = ttk.LabelFrame(parent, text="Configuration", padding="10")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        row = 0
        
        # Problem Configuration
        ttk.Label(config_frame, text="Problem Size:", font=('Helvetica', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        ttk.Label(config_frame, text="Scenario:").grid(row=row, column=0, sticky=tk.W)
        self.scenario_var = tk.StringVar(value="small")
        scenario_combo = ttk.Combobox(
            config_frame, 
            textvariable=self.scenario_var,
            values=["small", "medium", "large", "extra_large"],
            state="readonly",
            width=15
        )
        scenario_combo.grid(row=row, column=1, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Label(config_frame, text="Random Seed:").grid(row=row, column=0, sticky=tk.W)
        self.seed_var = tk.StringVar(value="42")
        ttk.Entry(config_frame, textvariable=self.seed_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=2
        )
        row += 1
        
        ttk.Separator(config_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10
        )
        row += 1
        
        # GA Configuration
        ttk.Label(config_frame, text="Genetic Algorithm:", font=('Helvetica', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        ttk.Label(config_frame, text="Population Size:").grid(row=row, column=0, sticky=tk.W)
        self.ga_pop_var = tk.StringVar(value="50")
        ttk.Entry(config_frame, textvariable=self.ga_pop_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=2
        )
        row += 1
        
        ttk.Label(config_frame, text="Generations:").grid(row=row, column=0, sticky=tk.W)
        self.ga_gen_var = tk.StringVar(value="100")
        ttk.Entry(config_frame, textvariable=self.ga_gen_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=2
        )
        row += 1
        
        ttk.Label(config_frame, text="Mutation Rate:").grid(row=row, column=0, sticky=tk.W)
        self.ga_mut_var = tk.StringVar(value="0.3")
        ttk.Entry(config_frame, textvariable=self.ga_mut_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=2
        )
        row += 1
        
        self.ga_local_search_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            config_frame, 
            text="Enable Local Search", 
            variable=self.ga_local_search_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        row += 1
        
        ttk.Separator(config_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10
        )
        row += 1
        
        # WoC Configuration
        ttk.Label(config_frame, text="Wisdom of Crowds:", font=('Helvetica', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        ttk.Label(config_frame, text="Analyze Top:").grid(row=row, column=0, sticky=tk.W)
        self.woc_top_var = tk.StringVar(value="20")
        ttk.Entry(config_frame, textvariable=self.woc_top_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=2
        )
        row += 1
        
        ttk.Label(config_frame, text="Min Confidence:").grid(row=row, column=0, sticky=tk.W)
        self.woc_conf_var = tk.StringVar(value="0.3")
        ttk.Entry(config_frame, textvariable=self.woc_conf_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=2
        )
        row += 1
        
        ttk.Label(config_frame, text="Solutions to Build:").grid(row=row, column=0, sticky=tk.W)
        self.woc_sols_var = tk.StringVar(value="10")
        ttk.Entry(config_frame, textvariable=self.woc_sols_var, width=15).grid(
            row=row, column=1, sticky=tk.W, pady=2
        )
        row += 1
        
    def setup_results_panel(self, parent):
        """Setup results panel"""
        results_frame = ttk.LabelFrame(parent, text="Results", padding="10")
        results_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Summary frame
        summary_frame = ttk.Frame(results_frame)
        summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.columnconfigure(1, weight=1)
        
        # GA Summary
        self.ga_summary_frame = ttk.LabelFrame(summary_frame, text="GA Solution", padding="5")
        self.ga_summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        self.ga_summary_text = tk.Text(self.ga_summary_frame, height=8, width=35, state='disabled')
        self.ga_summary_text.pack(fill=tk.BOTH, expand=True)
        
        # WoC Summary
        self.woc_summary_frame = ttk.LabelFrame(summary_frame, text="WoC Solution", padding="5")
        self.woc_summary_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.woc_summary_text = tk.Text(self.woc_summary_frame, height=8, width=35, state='disabled')
        self.woc_summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Console output
        console_frame = ttk.LabelFrame(results_frame, text="Console Output", padding="5")
        console_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, height=20)
        self.console.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.console.config(state='disabled')
        
    def setup_control_panel(self, parent):
        """Setup control buttons"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.run_ga_btn = ttk.Button(
            control_frame, 
            text="Run GA", 
            command=self.run_ga_only,
            width=15
        )
        self.run_ga_btn.grid(row=0, column=0, padx=5)
        
        self.run_woc_btn = ttk.Button(
            control_frame, 
            text="Run WoC", 
            command=self.run_woc_only,
            width=15,
            state='disabled'
        )
        self.run_woc_btn.grid(row=0, column=1, padx=5)
        
        self.run_both_btn = ttk.Button(
            control_frame, 
            text="Run Both (GA + WoC)", 
            command=self.run_both,
            width=20
        )
        self.run_both_btn.grid(row=0, column=2, padx=5)
        
        self.compare_btn = ttk.Button(
            control_frame, 
            text="Compare Results", 
            command=self.compare_results,
            width=15,
            state='disabled'
        )
        self.compare_btn.grid(row=0, column=3, padx=5)
        
        self.clear_btn = ttk.Button(
            control_frame, 
            text="Clear", 
            command=self.clear_all,
            width=15
        )
        self.clear_btn.grid(row=0, column=4, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate', length=200)
        self.progress.grid(row=1, column=0, columnspan=5, pady=10)
        
    def log(self, message):
        """Add message to console"""
        self.console.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)
        self.console.config(state='disabled')
        self.root.update()
        
    def update_ga_summary(self, solution):
        """Update GA summary display"""
        self.ga_summary_text.config(state='normal')
        self.ga_summary_text.delete(1.0, tk.END)
        
        if solution:
            utils = solution.average_utilization
            text = f"""Valid: {solution.is_valid()}
Servers Used: {solution.num_servers_used}
Total VMs: {solution.total_vms}
Fitness: {solution.fitness:.2f}

Utilization:
  CPU: {utils['cpu']:.1f}%
  RAM: {utils['ram']:.1f}%
  Storage: {utils['storage']:.1f}%
"""
            self.ga_summary_text.insert(1.0, text)
        
        self.ga_summary_text.config(state='disabled')
        
    def update_woc_summary(self, solution):
        """Update WoC summary display"""
        self.woc_summary_text.config(state='normal')
        self.woc_summary_text.delete(1.0, tk.END)
        
        if solution:
            utils = solution.average_utilization
            text = f"""Valid: {solution.is_valid()}
Servers Used: {solution.num_servers_used}
Total VMs: {solution.total_vms}
Fitness: {solution.fitness:.2f}

Utilization:
  CPU: {utils['cpu']:.1f}%
  RAM: {utils['ram']:.1f}%
  Storage: {utils['storage']:.1f}%
"""
            self.woc_summary_text.insert(1.0, text)
        
        self.woc_summary_text.config(state='disabled')
        
    def generate_problem(self):
        """Generate problem data"""
        try:
            scenario = self.scenario_var.get()
            seed = int(self.seed_var.get())
            
            self.log(f"Generating {scenario} scenario (seed={seed})...")
            
            scenario_data = DataGenerator.generate_scenario(scenario, seed=seed)
            self.vms = scenario_data['vms']
            self.server_template = scenario_data['server_template']
            
            self.log(f"Generated {len(self.vms)} VMs")
            self.log(f"Server capacity: {self.server_template.max_cpu_cores} cores, "
                    f"{self.server_template.max_ram_gb} GB RAM, "
                    f"{self.server_template.max_storage_gb} GB storage")
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate problem: {str(e)}")
            return False
            
    def run_ga_only(self):
        """Run only Genetic Algorithm"""
        if self.is_running:
            messagebox.showwarning("Warning", "An operation is already running!")
            return
            
        thread = threading.Thread(target=self._run_ga_thread)
        thread.daemon = True
        thread.start()
        
    def _run_ga_thread(self):
        """Thread for running GA"""
        self.is_running = True
        self.progress.start()
        self.disable_buttons()
        
        try:
            if not self.generate_problem():
                return
                
            # Get GA parameters
            pop_size = int(self.ga_pop_var.get())
            generations = int(self.ga_gen_var.get())
            mutation_rate = float(self.ga_mut_var.get())
            local_search = self.ga_local_search_var.get()
            
            self.log("="*50)
            self.log("Running Genetic Algorithm...")
            self.log(f"Population: {pop_size}, Generations: {generations}")
            self.log(f"Mutation Rate: {mutation_rate}, Local Search: {local_search}")
            self.log("="*50)
            
            start_time = time.time()
            
            self.best_ga_solution, self.ga_population = run_ga(
                vms=self.vms,
                server_template=self.server_template,
                population_size=pop_size,
                generations=generations,
                mutation_rate=mutation_rate,
                use_local_search=local_search,
                return_population=True  # Get the evolved population
            )
            
            elapsed = time.time() - start_time
            
            self.log("="*50)
            self.log(f"GA completed in {elapsed:.2f} seconds")
            self.log(f"Best solution: {self.best_ga_solution.num_servers_used} servers")
            self.log(f"Fitness: {self.best_ga_solution.fitness:.2f}")
            self.log("="*50)
            
            self.update_ga_summary(self.best_ga_solution)
            self.run_woc_btn.config(state='normal')
            self.compare_btn.config(state='normal')
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"GA execution failed: {str(e)}")
            
        finally:
            self.is_running = False
            self.progress.stop()
            self.enable_buttons()
            
    def run_woc_only(self):
        """Run only Wisdom of Crowds"""
        if self.is_running:
            messagebox.showwarning("Warning", "An operation is already running!")
            return
            
        if not self.best_ga_solution:
            messagebox.showwarning("Warning", "Please run GA first!")
            return
            
        thread = threading.Thread(target=self._run_woc_thread)
        thread.daemon = True
        thread.start()
        
    def _run_woc_thread(self):
        """Thread for running WoC"""
        self.is_running = True
        self.progress.start()
        self.disable_buttons()
        
        try:
            # Get WoC parameters
            top_k = int(self.woc_top_var.get())
            min_confidence = float(self.woc_conf_var.get())
            num_solutions = int(self.woc_sols_var.get())
            
            self.log("="*50)
            self.log("Running Wisdom of Crowds...")
            self.log(f"Analyzing top {top_k} solutions")
            self.log(f"Min confidence: {min_confidence}")
            self.log("="*50)
            
            start_time = time.time()
            
            # Create evaluator (needed for WoC solutions)
            evaluator = SimpleFitnessEvaluator()
            
            # Use the evolved GA population for analysis
            if self.ga_population:
                self.log(f"Using evolved GA population ({len(self.ga_population)} solutions)")
                population = self.ga_population
            else:
                # Fallback: Generate population for analysis
                self.log("Generating population for analysis...")
                population = create_initial_population(self.vms, self.server_template, 30)
                for sol in population:
                    evaluator.evaluate(sol)
                population.append(self.best_ga_solution)
            
            # Analyze with CrowdAnalyzer
            self.log("Analyzing patterns from evolved solutions...")
            analyzer = CrowdAnalyzer()
            analyzer.analyze_solutions(population, top_k=top_k)
            
            affinity_count = len(analyzer.co_occurrence_matrix)
            self.log(f"Found {affinity_count} VM co-occurrence patterns")
            
            # Build solution with CrowdBuilder
            self.log(f"Building {num_solutions} solutions from patterns...")
            builder = CrowdBuilder(analyzer)
            woc_solutions = builder.build_multiple_solutions(
                self.vms,
                self.server_template,
                num_solutions=num_solutions,
                affinity_weight=min_confidence
            )
            
            # Evaluate and get best
            for sol in woc_solutions:
                evaluator.evaluate(sol)
            
            woc_solutions.sort(key=lambda s: s.fitness)
            self.best_woc_solution = woc_solutions[0]
            
            elapsed = time.time() - start_time
            
            self.log("="*50)
            self.log(f"WoC completed in {elapsed:.2f} seconds")
            self.log(f"Best solution: {self.best_woc_solution.num_servers_used} servers")
            self.log(f"Fitness: {self.best_woc_solution.fitness:.2f}")
            self.log("="*50)
            
            self.update_woc_summary(self.best_woc_solution)
            self.compare_btn.config(state='normal')
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            messagebox.showerror("Error", f"WoC execution failed: {str(e)}")
            
        finally:
            self.is_running = False
            self.progress.stop()
            self.enable_buttons()
            
    def run_both(self):
        """Run both GA and WoC"""
        if self.is_running:
            messagebox.showwarning("Warning", "An operation is already running!")
            return
            
        thread = threading.Thread(target=self._run_both_thread)
        thread.daemon = True
        thread.start()
        
    def _run_both_thread(self):
        """Thread for running both algorithms"""
        self._run_ga_thread()
        if self.best_ga_solution:
            self._run_woc_thread()
            
    def compare_results(self):
        """Compare GA and WoC results"""
        if not self.best_ga_solution and not self.best_woc_solution:
            messagebox.showwarning("Warning", "No results to compare!")
            return
            
        self.log("="*50)
        self.log("DETAILED COMPARISON:")
        self.log("="*50)
        
        if self.best_ga_solution:
            ga_util = self.best_ga_solution.average_utilization
            self.log(f"GA Solution:")
            self.log(f"  Servers: {self.best_ga_solution.num_servers_used}")
            self.log(f"  Fitness: {self.best_ga_solution.fitness:.2f}")
            self.log(f"  Utilization: CPU={ga_util['cpu']:.1f}%, RAM={ga_util['ram']:.1f}%, Storage={ga_util['storage']:.1f}%")
            self.log(f"  Valid: {self.best_ga_solution.is_valid()}")
                    
        if self.best_woc_solution:
            woc_util = self.best_woc_solution.average_utilization
            self.log(f"\nWoC Solution:")
            self.log(f"  Servers: {self.best_woc_solution.num_servers_used}")
            self.log(f"  Fitness: {self.best_woc_solution.fitness:.2f}")
            self.log(f"  Utilization: CPU={woc_util['cpu']:.1f}%, RAM={woc_util['ram']:.1f}%, Storage={woc_util['storage']:.1f}%")
            self.log(f"  Valid: {self.best_woc_solution.is_valid()}")
                    
        if self.best_ga_solution and self.best_woc_solution:
            self.log(f"\nComparison:")
            server_diff = self.best_woc_solution.num_servers_used - self.best_ga_solution.num_servers_used
            fitness_diff = self.best_woc_solution.fitness - self.best_ga_solution.fitness
            
            if server_diff < 0:
                self.log(f"  ✅ WoC uses {abs(server_diff)} FEWER servers")
            elif server_diff > 0:
                self.log(f"  ⚠️ WoC uses {server_diff} MORE servers")
            else:
                self.log(f"  🔵 Same number of servers ({self.best_ga_solution.num_servers_used})")
            
            if abs(fitness_diff) < 0.01:
                self.log(f"  🔵 Same fitness (likely optimal solution)")
            elif fitness_diff < 0:
                improvement = abs((fitness_diff / self.best_ga_solution.fitness) * 100)
                self.log(f"  ✅ WoC fitness is {improvement:.1f}% BETTER")
            else:
                degradation = (fitness_diff / self.best_woc_solution.fitness) * 100
                self.log(f"  ⚠️ GA fitness is {degradation:.1f}% better")
                
            # Show VM placement differences
            ga_map = self.best_ga_solution.get_vm_assignment()
            woc_map = self.best_woc_solution.get_vm_assignment()
            
            all_vms = set(ga_map.keys()) | set(woc_map.keys())
            differences = sum(1 for vm_id in all_vms if ga_map.get(vm_id) != woc_map.get(vm_id))
            
            self.log(f"\nVM Placement:")
            self.log(f"  Total VMs: {len(all_vms)}")
            self.log(f"  Different placements: {differences} VMs ({(differences/len(all_vms)*100):.1f}%)")
            
            if differences == 0:
                self.log(f"Identical VM assignments (solutions are the same)")
            elif differences < len(all_vms) * 0.3:
                self.log(f"Very similar solutions (minor differences)")
            else:
                self.log(f"Different solutions (WoC explored alternative packing)")
                
        self.log("="*50)
        
    def clear_all(self):
        """Clear all results"""
        self.console.config(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.config(state='disabled')
        
        self.ga_summary_text.config(state='normal')
        self.ga_summary_text.delete(1.0, tk.END)
        self.ga_summary_text.config(state='disabled')
        
        self.woc_summary_text.config(state='normal')
        self.woc_summary_text.delete(1.0, tk.END)
        self.woc_summary_text.config(state='disabled')
        
        self.best_ga_solution = None
        self.best_woc_solution = None
        self.run_woc_btn.config(state='disabled')
        self.compare_btn.config(state='disabled')
        
        self.log("Cleared all results")
        
    def disable_buttons(self):
        """Disable all control buttons"""
        self.run_ga_btn.config(state='disabled')
        self.run_woc_btn.config(state='disabled')
        self.run_both_btn.config(state='disabled')
        self.compare_btn.config(state='disabled')
        
    def enable_buttons(self):
        """Enable control buttons"""
        self.run_ga_btn.config(state='normal')
        if self.best_ga_solution:
            self.run_woc_btn.config(state='normal')
        self.run_both_btn.config(state='normal')
        if self.best_ga_solution or self.best_woc_solution:
            self.compare_btn.config(state='normal')


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = VectorPackingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
