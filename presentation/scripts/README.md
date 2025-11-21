# Presentation Scripts

This directory contains all scripts for generating visualizations and presentation materials.

## Running Scripts

**Important:** All visualization scripts should be run from the project root directory:

```bash
# From project root
python presentation/scripts/visualize_production_scenarios.py
python presentation/scripts/generate_all_visuals.py
```

## Script Categories

### Main Visualization Generators

- `generate_all_visuals.py` - Master script that generates all presentation visuals
- `update_presentation_visuals.py` - Updates all presentation visuals with latest data

### Production Scenario Visualizations

- `visualize_production_scenarios.py` - Creates comprehensive visualizations for production scenarios (500, 750, 1000 VMs)
  - Input: `results/benchmarks/production_benchmark_results.json`
  - Output: `presentation_visuals/production_scenarios_analysis.html`

- `generate_azure_comparison.py` - Generates Azure dataset comparison charts
  - Creates performance comparisons between GA and WoC on Azure data
  - Outputs: `results/benchmarks/synthetic_benchmark_results.json`, `presentation/data/azure_benchmark_results.json`, `results/benchmarks/combined_benchmark_results.json`

### Convergence Analysis

- `update_convergence_visual.py` - Updates convergence visualization with latest data
  - Input: `convergence_data.json`
  - Output: Convergence charts in `presentation/visuals/`

- `generate_convergence_visual.py` - Generates detailed GA convergence visualizations
  - Shows fitness progression over generations

### Algorithm Analysis

- `generate_complexity_graph.py` - Creates time complexity analysis graphs
  - Visualizes algorithm performance scaling

- `generate_updated_results.py` - Regenerates result tables and summaries

### Diversity and Cooccurrence Analysis

- `generate_azure_cooccurrence_diversity.py` - Analyzes VM cooccurrence patterns and diversity metrics in Azure data

- `generate_diversity_threshold_data.py` - Generates data for diversity threshold analysis

### Comparison Visualizations

- `create_comparison_visualization.py` - Creates side-by-side algorithm comparisons
  - Compares GA vs WoC performance metrics

- `update_visualizations.py` - Updates all comparative visualizations

## Output Locations

Most scripts output to:
- `presentation/visuals/` - PNG/SVG image files for slides
- `presentation_visuals/` - Interactive HTML visualizations
- `presentation/data/` - Processed data for presentations

## Dependencies

All visualization scripts require:
- `plotly` - Interactive charts
- `matplotlib` - Static charts
- `pandas` - Data processing
- `numpy` - Numerical operations

Install with:
```bash
pip install plotly matplotlib pandas numpy
```
