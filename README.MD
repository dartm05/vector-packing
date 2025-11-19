# Vector Packing Solver - GA + WoC Hybrid Approach

A complete implementation of a hybrid Genetic Algorithm (GA) and Wisdom of Crowds (WoC) approach to solve the Multi-Dimensional Bin Packing Problem, with application to cloud computing resource allocation. Features a simplified GA engine, interactive GUI, and comprehensive visualizations for presentations.

## Problem Overview

### The Challenge
**Multi-Dimensional Bin Packing Problem (MDBPP)** - NP-Complete

In cloud computing environments, we need to efficiently allocate Virtual Machines (VMs) to physical servers while minimizing resource waste and the number of servers used.

- **Items to Pack**: Virtual Machines with resource requirements (CPU cores, RAM GB, Storage GB)
- **Bins**: Physical Servers with capacity constraints
- **Objective**: Minimize the number of servers while maximizing resource utilization
- **Constraints**: No server can exceed its capacity in any dimension

### Why This Matters
Efficient VM placement directly impacts:
- Infrastructure costs (fewer servers = lower costs)
- Energy consumption
- Resource utilization
- System performance

## Solution Approach

### Genetic Algorithm (GA)
Simplified evolutionary optimization with effective operators:
- **Configurable Initialization**: Random, poor, mixed, or good quality strategies
- **Aggressive Consolidation**: 60% consolidation mutations for server reduction
- **Tournament Selection**: k=3 tournament for parent selection
- **Adaptive Mutation**: Rates increase from 0.3 to 0.7 during stagnation
- **Elite Preservation**: Top 2 solutions carried to next generation
- **Early Stopping**: Terminates after 40 generations without improvement

### Wisdom of Crowds (WoC)
Learns from evolved GA populations to build optimized solutions **8-80× faster**:
- **Pattern Analysis**: Analyzes top-performing GA solutions to identify VM co-location patterns
- **Affinity Learning**: Builds co-occurrence matrices showing which VMs work well together
- **Intelligent Construction**: Uses learned patterns with configurable affinity weights
- **Speed Advantage**: Achieves same solution quality in fraction of the time

### Hybrid Strategy
The WoC phase learns from the evolved GA population, leveraging GA's exploration with WoC's pattern recognition to discover optimal or near-optimal solutions quickly.

## Performance Results

### Benchmark Results (seed=42, 100× fitness multiplier)

| Scenario | VMs | GA Time | WoC Time | Servers | Fitness | Speedup |
|----------|-----|---------|----------|---------|---------|---------|
| **Small** | 20 | 0.97s | 0.01s | 5 | 502.60 | **78.4×** |
| **Medium** | 50 | 2.83s | 0.09s | 6 | 601.87 | **32.2×** |
| **Large** | 100 | 7.84s | 0.39s | 8 | 803.30 | **20.0×** |
| **Extra Large** | 200 | 18.88s | 1.90s | 11 | 1104.03 | **10.0×** |

**Key Finding**: WoC achieves identical solution quality while being **8-80× faster** than GA!

### Convergence Performance

With random initialization, GA demonstrates clear improvement:

| Scenario | Initial | Final | Improvement | Generations |
|----------|---------|-------|-------------|-------------|
| **Small** | 8 servers | 5 servers | **37% reduction** | 8 |
| **Medium** | 20 servers | 6 servers | **70% reduction** | 22 |
| **Large** | 41 servers | 8 servers | **80% reduction** | 55 |

## Project Structure

```
final-project/
├── src/
│   ├── models/                    # Core data models
│   │   ├── __init__.py
│   │   ├── virtual_machine.py    # VM with resource requirements
│   │   ├── server.py              # Server with capacity tracking
│   │   └── solution.py            # Complete packing solution
│   │
│   ├── ga/                        # Genetic Algorithm components
│   │   ├── __init__.py
│   │   ├── simple_engine.py       # Simplified GA engine (ACTIVE)
│   │   ├── engine.py              # Original GA engine
│   │   ├── simple_fitness.py      # Fitness evaluation
│   │   ├── concrete_operators.py  # Selection, crossover, mutation
│   │   ├── fitness.py             # Base class for fitness evaluation
│   │   └── operators.py           # Base classes for GA operators
│   │
│   ├── woc/                       # Wisdom of Crowds components
│   │   ├── __init__.py
│   │   ├── crowd_analyzer.py      # Discovers VM co-location patterns
│   │   └── crowd_builder.py       # Builds solutions using learned patterns
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── data_generator.py      # Generate test datasets
│       └── logger.py              # Logging configuration
│
├── presentation_visuals/          # Visualizations for presentations
│   ├── vis_11_convergence_curves.html  # GA convergence curves
│   ├── vis_14_performance_comparison.html  # Performance comparison
│   └── slide_*.html               # Presentation slides (3)
│
├── presentation_scripts/          # Speaking scripts for presentations
│   ├── script_1_results_comparison.md
│   ├── script_2_medium_convergence.md
│   └── script_3_large_convergence.md
│
├── gui.py                         #  Main GUI application (tkinter)
├── main.py                        #  CLI entry point
├── generate_updated_results.py    # Benchmark all scenarios
├── capture_convergence_simple.py  # Capture convergence data
├── update_convergence_visual.py   # Update convergence HTML
├── requirements.txt               # Python dependencies
├── LICENSE
└── README.MD                      # This file
```

## Getting Started

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/dartm05/vector-packing.git
cd vector-packing

# Install dependencies
pip install -r requirements.txt
```

**Requirements:**
- Python 3.9+
- NumPy 2.0+
- tkinter (included with Python on most systems)

### 2. Quick Start - GUI Mode (Recommended)

Launch the graphical interface:

```bash
python gui.py
```

**How to Use:**
1. Select a test scenario (small, medium, large, extra_large)
2. Configure GA parameters (population size, generations, mutation rate)
3. Click "Run GA" to evolve solutions
4. Click "Run WoC" to apply wisdom of crowds (uses GA results)
5. Click "Compare Results" to see detailed side-by-side comparison

### 3. CLI Mode

Run from command line with custom parameters:

```bash
# Run with default settings (small scenario)
python main.py

# Run medium scenario with more generations
python main.py --scenario medium --generations 100

# Run with different initialization quality
python main.py --scenario large --init-quality random
```

**Available CLI Options:**
- `--scenario`: Test scenario (small/medium/large/extra_large)
- `--population`: Population size (default: 50)
- `--generations`: Number of generations (default: 100)
- `--mutation-rate`: Mutation rate (default: 0.3)
- `--elitism`: Elite solutions preserved (default: 2)
- `--tournament-k`: Tournament size (default: 3)
- `--init-quality`: Initial quality (random/poor/mixed/good, default: random)
- `--seed`: Random seed for reproducibility (default: 42)

### 4. Programmatic Usage

Use the algorithms directly in your Python code:

```python
from src.utils.data_generator import DataGenerator
from src.ga.simple_engine import run_simple_ga
from src.woc import CrowdAnalyzer, CrowdBuilder
from src.ga.simple_engine import calculate_fitness

# Generate test scenario
scenario = DataGenerator.generate_scenario('medium', seed=42)
vms = scenario['vms']
server = scenario['server_template']

# Run GA
best_ga = run_simple_ga(
    vms=vms,
    server_template=server,
    population_size=50,
    generations=100,
    elitism_count=2,
    mutation_rate=0.3,
    initial_quality="random"
)

print(f"GA Result: {best_ga.num_servers_used} servers, fitness={best_ga.fitness:.2f}")

# Run WoC using GA's evolved population
# (WoC is integrated in gui.py, see gui.py for full implementation)
```

## Available Test Scenarios

The data generator provides four predefined scenarios:

| Scenario | VMs | Server Capacity | GA Result | WoC Speedup |
|----------|-----|-----------------|-----------|-------------|
| `small` | 20 | 32 cores, 128 GB RAM, 1 TB | ~5 servers | 78× faster |
| `medium` | 50 | 64 cores, 256 GB RAM, 2 TB | ~6 servers | 32× faster |
| `large` | 100 | 96 cores, 512 GB RAM, 4 TB | ~8 servers | 20× faster |
| `extra_large` | 200 | 128 cores, 1 TB RAM, 8 TB | ~11 servers | 10× faster |

## Algorithm Features

### Simplified GA Engine (`src/ga/simple_engine.py`)

**Key Features:**
- **Clear, maintainable code**: Focused on effectiveness over complexity
- **Aggressive consolidation**: 60% of mutations attempt to reduce servers
- **Configurable initialization**: Supports random, poor, mixed, and good quality
- **Early stopping**: Terminates after 40 stagnant generations
- **Effective operators**: Tournament selection, simple crossover, smart mutations

**Initialization Strategies:**
1. **Random**: Completely random VM assignments (shows improvement)
2. **Poor**: Intentionally poor placement (for testing)
3. **Mixed**: Combination of strategies (balanced)
4. **Good**: Heuristic-based placement (fast convergence)

**Mutation Types:**
1. **Consolidation** (60%): Aggressively move VMs to reduce servers
2. **Simple moves** (40%): Move VMs between servers for fine-tuning

### WoC Pattern Learning
- Analyzes top 20 solutions from evolved GA population
- Builds co-occurrence matrix showing VM affinity scores
- Uses configurable affinity weights for diverse solution generation
- Achieves same solution quality as GA in fraction of the time

## Fitness Function

The simplified fitness evaluator uses:

```
fitness = (servers × 100) + (100 - avg_utilization) / 10
```

Where:
- **100× server weight**: Strongly prioritizes minimizing server count
- **Utilization penalty**: Secondary optimization on resource efficiency
- **Result**: Solutions with fewer servers always score better

**Example:**
- 5 servers with 83.9% avg utilization → fitness = 502.60
- 6 servers with 94.8% avg utilization → fitness = 601.87

## Visualizations & Presentation Materials

### Interactive Visualizations

Located in `presentation_visuals/`:

1. **vis_11_convergence_curves.html** - GA convergence curves showing:
   - Fitness improvement over generations
   - Server count reduction
   - Best vs average fitness tracking

2. **vis_14_performance_comparison.html** - Performance comparison:
   - GA vs WoC execution times
   - Speedup factors
   - Solution quality metrics
 

## Regenerating Results

### Run New Benchmarks

```bash
# Benchmark all scenarios (takes ~5 min)
python generate_updated_results.py

# Results saved to: updated_benchmark_results.json
```

### Capture Convergence Data

```bash
# Run experiments to capture generation-by-generation data
python capture_convergence_simple.py

# Update visualization with new data
python update_convergence_visual.py

# Results saved to: convergence_data.json
# Visualization updated: presentation_visuals/vis_11_convergence_curves.html
```

### All-in-One Regeneration

```bash
# Regenerate everything
./regenerate_all_visualizations.sh
```
 
## Solution Metrics

The `Solution` class provides comprehensive metrics:
- `num_servers_used`: Total servers with at least one VM (primary objective)
- `total_vms`: Total VMs successfully placed
- `average_utilization`: Average resource utilization across CPU, RAM, storage
- `is_valid()`: Validates no capacity constraints are violated
- `fitness`: Evaluated by fitness function (lower is better)

## Understanding Results

### Fitness Values
- **Small (5 servers)**: fitness ~502.60
- **Medium (6 servers)**: fitness ~601.87
- **Large (8 servers)**: fitness ~803.30
- **Extra Large (11 servers)**: fitness ~1104.03

Lower fitness is better. Each additional server adds ~100 to fitness.

### Speedup Factors
WoC achieves dramatic speedup while finding identical solutions:
- Small problems: **70-80× faster**
- Medium problems: **30-40× faster**
- Large problems: **15-25× faster**
- Extra large: **8-12× faster**

### Convergence Patterns
- **Early generations**: Rapid server count reduction
- **Middle generations**: Continued consolidation
- **Late generations**: Fine-tuning utilization
- **Typical convergence**: 5-60 generations depending on problem size

## Troubleshooting

### GUI doesn't launch
- Ensure tkinter is installed: `python3 -m tkinter` (should open a test window)
- On Linux: `sudo apt-get install python3-tk`
- On macOS: tkinter is included with Python

### "No module named 'numpy'"
```bash
pip install numpy
```

### Visualizations don't show data
The HTML visualizations require a modern browser (Chrome, Firefox, Safari, Edge). They use Plotly.js loaded from CDN.

## References

### Core Problem & Complexity
1. **Garey, M. R., & Johnson, D. S. (1979)**. *Computers and Intractability: A Guide to the Theory of NP-Completeness*. W.H. Freeman.

2. **Lodi, A., Martello, S., & Vigo, D. (2002)**. "Recent advances on two-dimensional bin packing problems." *Discrete Applied Mathematics*, 123(1-3), 379-396.

### Genetic Algorithms
3. **Goldberg, D. E. (1989)**. *Genetic Algorithms in Search, Optimization, and Machine Learning*. Addison-Wesley.

4. **Falkenauer, E. (1996)**. "A hybrid grouping genetic algorithm for bin packing." *Journal of Heuristics*, 2(1), 5-30.

5. **Eiben, A. E., & Smith, J. E. (2015)**. *Introduction to Evolutionary Computing* (2nd ed.). Springer.

### Heuristic Approaches
6. **Johnson, D. S. (1973)**. "Near-optimal bin packing algorithms." Doctoral Dissertation, MIT.

7. **Coffman Jr, E. G., Garey, M. R., & Johnson, D. S. (1996)**. "Approximation algorithms for bin packing: A survey." *Approximation Algorithms for NP-hard Problems*, 46-93.

### Wisdom of Crowds & Pattern Learning
8. **Surowiecki, J. (2004)**. *The Wisdom of Crowds: Why the Many Are Smarter Than the Few*. Doubleday.

9. **Nguyen, S., Zhang, M., Johnston, M., & Tan, K. C. (2013)**. "A computational study of representations in genetic programming to evolve dispatching rules for the job shop scheduling problem." *IEEE Transactions on Evolutionary Computation*, 17(5), 621-639.

### Cloud Computing & VM Placement
10. **Beloglazov, A., & Buyya, R. (2012)**. "Optimal online deterministic algorithms and adaptive heuristics for energy and performance efficient dynamic consolidation of virtual machines in cloud data centers." *Concurrency and Computation: Practice and Experience*, 24(13), 1397-1420.

11. **Xu, J., & Fortes, J. A. (2010)**. "Multi-objective virtual machine placement in virtualized data center environments." *2010 IEEE/ACM International Conference on Green Computing and Communications*, 179-188.

### Hybrid Approaches
12. **Talbi, E. G. (2009)**. *Metaheuristics: From Design to Implementation*. Wiley.

13. **Poli, R., Langdon, W. B., & McPhee, N. F. (2008)**. *A Field Guide to Genetic Programming*. Lulu Enterprises. Available free at: http://www.gp-field-guide.org.uk

## Contributing

Contributions are welcome! Areas for enhancement:
- Additional fitness functions (energy efficiency, network locality)
- More sophisticated WoC pattern recognition
- GPU-accelerated fitness evaluation
- Real-world VM workload datasets
- Performance benchmarking suite

## License

See LICENSE file for details.

---
 