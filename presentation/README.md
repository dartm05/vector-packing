# Presentation Materials

This folder contains all materials for presenting the Vector Packing Solver project results.

## 📁 Folder Structure

```
presentation/
├── visuals/          # HTML visualizations (interactive charts & slides)
├── scripts/          # Python scripts to generate data
├── data/             # JSON data files used by visualizations
└── README.md         # This file
```

## 🎯 Quick Start

### View Visualizations

Open the main landing page:
```bash
open visuals/index.html
```

Or open individual visualizations directly from the `visuals/` folder.

### Generate Fresh Data

If you need to regenerate the data files:

```bash
# Generate Azure benchmark comparison data
cd scripts/
python3 generate_azure_comparison.py

# Generate co-occurrence matrix and convergence data
python3 generate_azure_cooccurrence_diversity.py

# Generate diversity threshold data
python3 generate_diversity_threshold_data.py
```

## 📊 Available Visualizations

### Main Results
- **vis_14_performance_comparison.html** - GA vs WoC performance on Azure data (4 scenarios)
- **vis_11_convergence_curves.html** - GA convergence on Azure data (small/medium/large)

### Detailed Analysis
- **vis_12_cooccurrence_matrix.html** - 50×50 heatmap showing VM co-location patterns
- **vis_13_convergence_diversity.html** - Population diversity with immigration events
- **comparison_synthetic_vs_azure.html** - Comparison between synthetic and Azure data

### Conceptual Slides
- **vis_1_problem_context.html** - Problem definition and motivation
- **vis_3_hybrid_architecture.html** - GA + WoC hybrid architecture
- **vis_4_ga_chromosome.html** - Chromosome representation
- **vis_5_fitness_function.html** - Fitness function details
- **vis_9_mutation_operators.html** - Mutation operators

## 📈 Data Files

### `data/azure_benchmark_results.json`
Benchmark results for GA and WoC on 4 Azure scenarios:
- Small (20 VMs)
- Medium (50 VMs)
- Large (100 VMs)
- Extra Large (200 VMs)

Contains execution time, server count, fitness, and utilization metrics.

### `data/azure_cooccurrence_diversity.json`
Co-occurrence matrix (50×50) extracted from GA population analysis on Azure medium scenario.
Shows which VMs frequently co-locate in top solutions.

### `data/diversity_threshold_data.json`
Population diversity tracking over 100 generations showing:
- Natural diversity decline
- Immigration events when threshold (0.15) is reached
- Diversity spikes after immigration

## 🔧 Scripts

### Core Generation Scripts
- **generate_azure_comparison.py** - Runs GA and WoC on Azure data, generates benchmark comparison
- **generate_azure_cooccurrence_diversity.py** - Extracts co-occurrence matrix from GA population
- **generate_diversity_threshold_data.py** - Generates diversity threshold simulation data

### Legacy/Utility Scripts
- **generate_all_visuals.py** - Old script for generating multiple visualizations
- **generate_complexity_graph.py** - Complexity analysis visualization
- **generate_convergence_visual.py** - Convergence curve generation
- **generate_updated_results.py** - Results comparison generation
- **update_presentation_visuals.py** - Batch update script for visualizations

## 🎨 Presentation Tips

1. **Full-Screen Mode**: Press F11 in your browser
2. **Interactive Charts**: Hover over data points for details
3. **Export to PDF**: Ctrl+P (Cmd+P on Mac) → Save as PDF
4. **Offline Use**: All slides work without internet (after first load)

## 🔑 Key Findings to Highlight

- **6-67× Speedup**: WoC dramatically outperforms GA in execution time
- **Better Solutions**: WoC finds superior solutions in ALL 4 Azure scenarios
- **Real-World Data**: Tested on Microsoft Azure production traces (5.5M VMs, OSDI 2020)
- **Example**: Large scenario - WoC uses 10 servers vs GA's 21 (52% improvement!)
- **Adaptive Diversity**: Immigration mechanism prevents premature convergence

## 📝 Notes

- All visualizations use Plotly.js for interactive charts
- Data is embedded directly in HTML files for offline use
- Azure data sourced from: "Azure Public Dataset" (OSDI 2020)
- Threshold for diversity-triggered immigration: 0.15
- Immigration rate: 10% of population size
