#!/usr/bin/env python3
"""
Generate complexity comparison graph for GA vs GA+WOC
Shows theoretical complexity curves and empirical execution times
"""

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib/numpy not available. Will only print summary.")

# Empirical data from experiments
problem_sizes = [20, 50, 100, 200]  # Number of VMs
ga_times = [0.32, 0.85, 1.59, 3.60]  # GA execution times (seconds)
woc_times = [0.09, 0.07, 0.16, 0.54]  # WOC execution times (seconds)

# Theoretical complexity parameters
# GA: O(G * P * N^2) where G=generations, P=population_size
# For our experiments: G≈50, P=50
G = 50
P = 50
k_ga = 0.000001  # Scaling constant for GA (fitted)
k_woc = 0.000002  # Scaling constant for WOC (fitted)

if not HAS_MATPLOTLIB:
    print("\n" + "="*60)
    print("COMPLEXITY ANALYSIS SUMMARY (Text Mode)")
    print("="*60)
    print(f"\nEmpirical Speedup Factors:")
    for n, ga_t, woc_t in zip(problem_sizes, ga_times, woc_times):
        speedup = ga_t / woc_t
        print(f"  N={n:3d} VMs: {speedup:.1f}× faster ({ga_t:.2f}s → {woc_t:.2f}s)")
    
    print(f"\nTheoretical Complexity:")
    print(f"  GA:  O(G·P·N²) = O({G}·{P}·N²) = O({G*P}·N²)")
    print(f"  WOC: O(N²)")
    print(f"  Ratio: GA/WOC ≈ {G*P}:1 for same N")
    print("\n" + "="*60)
    exit(0)

# Generate smooth curve for theoretical complexity
N_theory = np.linspace(20, 200, 100)

# GA theoretical: O(G * P * N^2)
ga_theoretical = k_ga * G * P * (N_theory ** 2)

# WOC theoretical: O(N^2) for pattern analysis + O(N^2) for solution building
woc_theoretical = k_woc * (N_theory ** 2)

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Plot theoretical curves
ax.plot(N_theory, ga_theoretical, 'b--', linewidth=2, alpha=0.7, 
        label='GA Theoretical: O(G·P·N²)')
ax.plot(N_theory, woc_theoretical, 'r--', linewidth=2, alpha=0.7,
        label='WOC Theoretical: O(N²)')

# Plot empirical data points
ax.plot(problem_sizes, ga_times, 'bo-', linewidth=2, markersize=10,
        label='GA Empirical', markeredgecolor='darkblue', markeredgewidth=1.5)
ax.plot(problem_sizes, woc_times, 'ro-', linewidth=2, markersize=10,
        label='WOC Empirical', markeredgecolor='darkred', markeredgewidth=1.5)

# Add data labels
for i, (n, ga_t, woc_t) in enumerate(zip(problem_sizes, ga_times, woc_times)):
    # GA labels
    ax.annotate(f'{ga_t}s', xy=(n, ga_t), xytext=(5, 10), 
                textcoords='offset points', fontsize=9, color='darkblue',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))
    # WOC labels
    ax.annotate(f'{woc_t}s', xy=(n, woc_t), xytext=(5, -15), 
                textcoords='offset points', fontsize=9, color='darkred',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))

# Add speedup annotations
for i, (n, ga_t, woc_t) in enumerate(zip(problem_sizes, ga_times, woc_times)):
    speedup = ga_t / woc_t
    mid_y = (ga_t + woc_t) / 2
    if i == len(problem_sizes) - 1:  # Only annotate the last one
        ax.annotate(f'{speedup:.1f}× faster', xy=(n, mid_y), 
                    xytext=(20, 0), textcoords='offset points',
                    fontsize=10, color='green', weight='bold',
                    arrowprops=dict(arrowstyle='->', color='green', lw=1.5))

# Styling
ax.set_xlabel('Problem Size (Number of VMs)', fontsize=12, weight='bold')
ax.set_ylabel('Execution Time (seconds)', fontsize=12, weight='bold')
ax.set_title('Complexity Analysis: GA vs GA+WOC\nTheoretical Complexity and Empirical Performance', 
             fontsize=14, weight='bold', pad=20)
ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
ax.grid(True, alpha=0.3, linestyle='--')

# Add text box with complexity formulas
textstr = 'Complexity:\n'
textstr += 'GA: O(G·P·N²)\n'
textstr += '     G=50, P=50\n'
textstr += 'WOC: O(N²)\n'
textstr += '     (Pattern + Build)'

props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
ax.text(0.98, 0.35, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment='right', bbox=props,
        family='monospace')

# Add shaded region showing WOC advantage
ax.fill_between(problem_sizes, woc_times, ga_times, alpha=0.2, color='green',
                label='WOC Time Savings')

plt.tight_layout()

# Save the figure
output_file = 'complexity_comparison.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✅ Graph saved as: {output_file}")

# Also save as PDF for LaTeX
output_pdf = 'complexity_comparison.pdf'
plt.savefig(output_pdf, dpi=300, bbox_inches='tight')
print(f"✅ PDF saved as: {output_pdf}")

plt.show()

print("\n" + "="*60)
print("COMPLEXITY ANALYSIS SUMMARY")
print("="*60)
print(f"\nEmpirical Speedup Factors:")
for n, ga_t, woc_t in zip(problem_sizes, ga_times, woc_times):
    speedup = ga_t / woc_t
    print(f"  N={n:3d} VMs: {speedup:.1f}× faster ({ga_t:.2f}s → {woc_t:.2f}s)")

print(f"\nTheoretical Complexity:")
print(f"  GA:  O(G·P·N²) = O({G}·{P}·N²) = O({G*P}·N²)")
print(f"  WOC: O(N²)")
print(f"  Ratio: GA/WOC ≈ {G*P}:1 for same N")

print("\n" + "="*60)
