# How to Run This Project

## Quick Start (3 Steps)

### 1. Install Dependencies

```bash
# Option A: Use the setup script (recommended)
chmod +x setup.sh
./setup.sh

# Option B: Manual installation
pip install -r requirements.txt
```

### 2. Run the Main Program

```bash
# Default run (small problem, 20 VMs)
python main.py

# Medium problem (50 VMs)
python main.py --scenario medium

# Large problem with local search
python main.py --scenario large --local-search

# Custom parameters
python main.py --scenario medium --population 100 --generations 200 --mutation-rate 0.4
```

### 3. Run Tests

```bash
# Run the convergence test
python test_ga_convergence.py

# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

---

## Command Line Options

```bash
python main.py [OPTIONS]
```

### Available Options:

| Option | Default | Description |
|--------|---------|-------------|
| `--scenario` | `small` | Problem size: `small`, `medium`, `large`, `extra_large` |
| `--population` | `50` | GA population size |
| `--generations` | `100` | Maximum number of generations |
| `--mutation-rate` | `0.3` | Mutation probability (0.0-1.0) |
| `--elitism` | `2` | Number of best solutions preserved each generation |
| `--tournament-k` | `3` | Tournament selection size |
| `--local-search` | `False` | Enable memetic algorithm (GA + local search) |
| `--seed` | `42` | Random seed for reproducibility |

---

## Examples

### Example 1: Quick Test (Small Problem)
```bash
python main.py
```
**Output**: Solves 20 VMs placement problem with default settings

### Example 2: Medium Problem with More Exploration
```bash
python main.py --scenario medium --population 100 --mutation-rate 0.4
```
**Output**: 50 VMs with larger population and higher mutation

### Example 3: Large Problem with Local Search
```bash
python main.py --scenario large --local-search --generations 200
```
**Output**: 100 VMs using hybrid GA+local search approach

### Example 4: Extra Large with Custom Parameters
```bash
python main.py --scenario extra_large --population 100 --generations 300 \
               --mutation-rate 0.35 --local-search
```
**Output**: 200 VMs with aggressive search settings

---

## Understanding the Output

### During Execution:
```
Generation 1/100: Best=532.18 (5 servers), Worst=642.62, Stagnation=0, MutRate=0.30
```
- **Best**: Fitness score of best solution (lower is better)
- **Servers**: Number of servers used
- **Worst**: Worst solution in population
- **Stagnation**: Generations without improvement
- **MutRate**: Current mutation rate (adapts automatically)

### Final Results:
```
✅ Solution found!
  Valid: True
  Servers used: 5
  Total VMs placed: 20 / 20
  Fitness score: 532.18
  
  Average utilization:
    CPU: 83.87%
    RAM: 64.64%
    Storage: 73.50%
```

---

## Scenario Sizes

| Scenario | VMs | Server Capacity | Difficulty |
|----------|-----|-----------------|------------|
| **small** | 20 | 32 cores, 128 GB RAM, 1 TB storage | Easy - 2-5 minutes |
| **medium** | 50 | 64 cores, 256 GB RAM, 2 TB storage | Medium - 5-10 minutes |
| **large** | 100 | 96 cores, 512 GB RAM, 4 TB storage | Hard - 10-20 minutes |
| **extra_large** | 200 | 128 cores, 1 TB RAM, 8 TB storage | Very Hard - 20-40 minutes |

*Note: Times are approximate and depend on your hardware*

---

## Programming Interface

### Use in Your Own Code

```python
from src.utils.data_generator import DataGenerator
from src.ga.engine import run_ga

# Generate problem data
scenario = DataGenerator.generate_scenario('medium', seed=42)
vms = scenario['vms']
server_template = scenario['server_template']

# Run genetic algorithm
best_solution = run_ga(
    vms=vms,
    server_template=server_template,
    population_size=50,
    generations=100,
    elitism_count=2,
    mutation_rate=0.3,
    tournament_k=3,
    use_local_search=False
)

# Access results
print(f"Servers used: {best_solution.num_servers_used}")
print(f"Valid: {best_solution.is_valid()}")
print(f"Fitness: {best_solution.fitness}")
print(f"Utilization: {best_solution.average_utilization}")
```

### Create Custom VMs

```python
from src.models import VirtualMachine, Server
from src.ga.engine import run_ga

# Create custom VMs
vms = [
    VirtualMachine(id=1, cpu_cores=4, ram_gb=16, storage_gb=100),
    VirtualMachine(id=2, cpu_cores=8, ram_gb=32, storage_gb=200),
    VirtualMachine(id=3, cpu_cores=2, ram_gb=8, storage_gb=50),
    # ... add more VMs
]

# Create server template
server_template = Server(
    id=0,
    max_cpu_cores=64,
    max_ram_gb=256,
    max_storage_gb=2000
)

# Run GA
best = run_ga(vms, server_template, population_size=30, generations=50)
```

---

## Troubleshooting

### ImportError: No module named 'src'
**Solution**: Make sure you're in the project root directory:
```bash
cd /Users/daniellaarteaga/Desktop/C.S-MS/2025-2/AI/final-project
python main.py
```

### ModuleNotFoundError: No module named 'numpy'
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Algorithm converges too quickly
**Solution**: Try these adjustments:
```bash
# Increase mutation rate
python main.py --mutation-rate 0.4

# Use larger population
python main.py --population 100

# Enable local search
python main.py --local-search
```

### Solution is invalid
**Solution**: This shouldn't happen with the fixed algorithm, but if it does:
1. Check that your VMs can fit in servers
2. Verify server capacity is sufficient
3. Try a different random seed: `--seed 123`

---

## Project Structure

```
final-project/
├── main.py                      # ← Main entry point (run this!)
├── test_ga_convergence.py       # Test script
├── requirements.txt             # Dependencies
├── setup.sh                     # Setup script
│
├── src/
│   ├── models/                  # Data models (VM, Server, Solution)
│   ├── ga/                      # Genetic Algorithm implementation
│   │   ├── engine.py           # Main GA loop
│   │   ├── fitness.py          # Fitness evaluation
│   │   ├── operators.py        # GA operators (selection, crossover, mutation)
│   │   ├── concrete_operators.py
│   │   ├── advanced_selection.py
│   │   └── local_search.py     # Local search improvement
│   └── utils/                   # Utilities
│       ├── data_generator.py   # Generate test data
│       └── logger.py            # Logging
│
└── tests/                       # Unit tests
    ├── test_models.py
    └── test_utils.py
```

---

## What's Next?

1. **Run the examples above** to see the algorithm in action
2. **Read** `GA_FIX_COMPLETE_REPORT.md` to understand the improvements made
3. **Experiment** with different parameters to tune performance
4. **Implement** the Wisdom of Crowds component in `src/woc/`
5. **Compare** GA vs WoC performance

---

## Need Help?

- Check `README.MD` for project overview
- Read `GA_FIX_COMPLETE_REPORT.md` for algorithm details
- Look at `test_ga_convergence.py` for more examples
- Run tests: `pytest tests/ -v`

**Happy optimizing!** 🚀
