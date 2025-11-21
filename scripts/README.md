# Scripts Directory

This directory contains utility scripts for benchmarking, data processing, and demos.

## Structure

```
scripts/
├── benchmarks/       # Performance benchmarking and data capture scripts
├── data/            # Data download and preprocessing scripts
└── demos/           # Demo applications
```

## Running Scripts

**Important:** All scripts should be run from the project root directory to ensure proper paths:

```bash
# From project root
python scripts/benchmarks/benchmark_production_scenarios.py
python scripts/data/download_azure_dataset.py
python scripts/demos/demo_gui_with_azure.py
```

## Benchmarks

- `benchmark_production_scenarios.py` - Runs comprehensive benchmarks on production-scale scenarios (500, 750, 1000 VMs)
  - Outputs: `results/benchmarks/production_benchmark_results.json`

- `capture_convergence_data.py` - Captures detailed GA convergence data across multiple runs
  - Outputs: `results/convergence/convergence_data.json`

- `capture_convergence_simple.py` - Simplified convergence data capture
  - Outputs: `results/convergence/convergence_data.json`

## Data

- `download_azure_dataset.py` - Downloads Microsoft Azure VM allocation dataset (Azure Packing Trace 2020)
  - Source: Azure Public Dataset (OSDI 2020 - Protean paper)
  - License: CC-BY Attribution
  - Download size: ~51 MB, Extracted: ~173 MB
  - Outputs: `datasets/` directory with SQLite database

## Demos

- `demo_gui_with_azure.py` - Interactive GUI demo with Azure dataset integration
  - Demonstrates the GA and WoC algorithms with real Azure data
