# Vector Packing Solver - GA + WoC Hybrid Approach

A complete implementation of a hybrid Genetic Algorithm (GA) and Wisdom of Crowds (WoC) approach to solve the Multi-Dimensional Bin Packing Problem, with application to cloud computing resource allocation. Features a user-friendly GUI, advanced diversity mechanisms, and intelligent pattern learning.

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
Advanced evolutionary optimization with multiple features:
- **8 Initialization Strategies**: Random, largest-first, smallest-first, balanced, best-fit, worst-fit, CPU-focused, and RAM-focused
- **5 Mutation Types**: Move, swap, shuffle, consolidate (40%), and empty_server (40%) for smart resource optimization
- **Diversity Mechanisms**: Immigration (5-50 individuals) when diversity drops below 0.15
- **Adaptive Mutation**: Rates increase from 0.3 to 0.7 during stagnation
- **Elite Preservation**: Top 10% of solutions carried to next generation
- **Early Stopping**: Terminates after 30 generations without improvement

### Wisdom of Crowds (WoC)
Learns from evolved GA populations to build optimized solutions:
- **Pattern Analysis**: Analyzes top-performing GA solutions to identify VM co-location patterns
- **Affinity Learning**: Builds co-occurrence matrices showing which VMs work well together
- **Intelligent Construction**: Uses learned patterns with variable affinity weights (0.2-0.95)
- **Diverse Generation**: Creates multiple solutions using different strategies and parameters

### Hybrid Strategy
The WoC phase learns from the evolved GA population (not random solutions), leveraging GA's exploration with WoC's pattern recognition to discover optimal or near-optimal solutions quickly.

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
│   │   ├── engine.py              # ✅ GA evolution engine with diversity mechanisms
│   │   ├── simple_fitness.py      # ✅ Fitness evaluation implementation
│   │   ├── concrete_operators.py  # ✅ Selection, crossover, mutation operators
│   │   ├── fitness.py             # Base class for fitness evaluation
│   │   ├── operators.py           # Base classes for GA operators
│   │   └── chromosome.py          # Chromosome representation
│   │
│   ├── woc/                       # Wisdom of Crowds components
│   │   ├── __init__.py            # Module exports
│   │   ├── crowd_analyzer.py      # ✅ Discovers VM co-location patterns
│   │   └── crowd_builder.py       # ✅ Builds solutions using learned patterns
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── data_generator.py      # Generate test datasets
│       └── logger.py              # Logging configuration
│
├── tests/                         # Unit tests
│   ├── __init__.py
│   ├── test_models.py             # Test data models
│   └── test_utils.py              # Test utilities
│
├── gui.py                         # ✅ Main GUI application (tkinter)
├── main.py                        # ✅ CLI entry point
├── requirements.txt               # Python dependencies
├── LICENSE
└── README.MD                      # This file
```

## Components Status

### ✅ Complete & Production-Ready

**GUI Application (`gui.py`)**
- Full-featured tkinter GUI for both GA and WoC algorithms
- Real-time console output with color-coded messages
- Interactive parameter configuration
- Side-by-side results comparison showing VM placement details
- Non-blocking execution using threading

**Data Models (`src/models/`)**
- `VirtualMachine`: Represents a VM with CPU, RAM, and storage requirements
- `Server`: Represents a physical server with capacity constraints and VM tracking
- `Solution`: Represents a complete packing solution with validation and metrics

**GA Engine (`src/ga/engine.py`)**
- Complete evolution engine with 8 initialization strategies
- Diversity monitoring and immigration mechanism
- Adaptive mutation rates (0.3 → 0.7)
- Elite preservation (10%)
- Early stopping after 30 stagnant generations
- Returns evolved population for WoC learning

**GA Operators (`src/ga/concrete_operators.py`)**
- Tournament selection with configurable size
- VM map crossover preserving valid assignments
- 5 mutation types: move, swap, shuffle, consolidate, empty_server
- Smart consolidation mutations (40% probability) for resource optimization

**Fitness Evaluation (`src/ga/simple_fitness.py`)**
- Weighted fitness function: `100 × servers + wasted_resources`
- Strongly prioritizes minimizing server count
- Secondary optimization on resource utilization

**WoC Components (`src/woc/`)**
- `CrowdAnalyzer`: Pattern analysis from top GA solutions
- `CrowdBuilder`: Solution construction using learned affinities
- Configurable affinity weights and initialization strategies

**Utilities (`src/utils/`)**
- `DataGenerator`: Generate test datasets with various scenarios (small, medium, large, extra_large)
- `Logger`: Logging configuration and utilities

**CLI (`main.py`)**
- Command-line interface for running GA and WoC
- Configurable parameters via command-line arguments

**Tests**
- Unit tests for models
- Unit tests for utilities

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
python3 gui.py
```

**GUI Features:**
- 🎮 **Easy Controls**: Select scenario, configure parameters with sliders
- 📊 **Real-Time Console**: Watch algorithm progress with color-coded output
- 🔍 **Detailed Comparison**: See exactly how VMs are distributed across servers
- ⚡ **Non-Blocking**: GUI remains responsive during algorithm execution
- 📈 **Results Display**: View servers used, fitness scores, and resource utilization

**How to Use:**
1. Select a test scenario (small, medium, large, extra_large)
2. Configure GA parameters (population size, generations, mutation rate)
3. Click "Run GA" to evolve solutions
4. Click "Run WoC" to apply wisdom of crowds (uses GA results)
5. Click "Compare Results" to see detailed side-by-side comparison

### 3. CLI Mode

Run from command line with custom parameters:

```bash
# Run with default settings
python3 main.py

# Run with custom parameters
python3 main.py --scenario medium --population 100 --generations 100
```

**Available CLI Options:**
- `--scenario`: Test scenario (small/medium/large/extra_large)
- `--population`: Population size (default: 50)
- `--generations`: Number of generations (default: 100)
- `--mutation-rate`: Initial mutation rate (default: 0.3)
- `--crossover-rate`: Crossover probability (default: 0.8)
- `--elite-size`: Elite preservation count (default: 5)

### 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage
pytest tests/ --cov=src
```

### 5. Programmatic Usage

Use the algorithms directly in your Python code:

```python
from src.utils.data_generator import DataGenerator
from src.ga.engine import run_ga
from src.woc import CrowdAnalyzer, CrowdBuilder
from src.ga.simple_fitness import SimpleFitnessEvaluator

# Generate test scenario
scenario = DataGenerator.generate_scenario('medium', seed=42)
vms = scenario['vms']
server = scenario['server_template']

# Run GA (returns best solution and evolved population)
best_ga, ga_population = run_ga(
    vms=vms,
    server_template=server,
    population_size=50,
    generations=100,
    return_population=True  # Required for WoC
)

print(f"GA Result: {best_ga.num_servers_used} servers")

# Run WoC using GA's evolved population
analyzer = CrowdAnalyzer()
analyzer.analyze_solutions(ga_population, top_k=20)

builder = CrowdBuilder(analyzer)
woc_solutions = builder.build_multiple_solutions(
    vms, server, num_solutions=10, affinity_weight=0.5
)

# Evaluate WoC solutions
evaluator = SimpleFitnessEvaluator()
for sol in woc_solutions:
    evaluator.evaluate(sol)

best_woc = min(woc_solutions, key=lambda s: s.fitness)
print(f"WoC Result: {best_woc.num_servers_used} servers")
```

## Available Test Scenarios

The data generator provides four predefined scenarios:

| Scenario | VMs | Server Capacity | Difficulty | Typical Result |
|----------|-----|-----------------|------------|----------------|
| `small` | 20 | 32 cores, 128 GB RAM, 1 TB storage | Easy | ~5 servers |
| `medium` | 50 | 64 cores, 256 GB RAM, 2 TB storage | Medium | ~11 servers |
| `large` | 100 | 96 cores, 512 GB RAM, 4 TB storage | Hard | ~22 servers |
| `extra_large` | 200 | 128 cores, 1 TB RAM, 8 TB storage | Very Hard | ~45 servers |

## Algorithm Features

### GA Initialization Strategies (8 types)
The engine creates diverse initial populations using:
1. **Random**: Completely random VM assignments
2. **Largest-First**: Place largest VMs first (greedy)
3. **Smallest-First**: Place smallest VMs first
4. **Balanced**: Balance resource dimensions
5. **Best-Fit**: Best-fit decreasing heuristic (minimizes wasted space)
6. **Worst-Fit**: Worst-fit heuristic (balances server loads)
7. **CPU-Focused**: Prioritize CPU utilization
8. **RAM-Focused**: Prioritize RAM utilization

### GA Mutations (5 types with smart weighting)
1. **Move** (normal probability): Move a VM to a different server
2. **Swap** (normal probability): Swap two VMs between servers
3. **Shuffle** (normal probability): Shuffle VMs on a server
4. **Consolidate** (40% probability): Aggressively consolidate VMs to fewer servers
5. **Empty Server** (40% probability): Empty a server and redistribute its VMs

The high probability for consolidate and empty_server mutations drives the algorithm toward fewer servers.

### Diversity Mechanisms
- **Population Diversity**: Calculated as average Hamming distance between solutions
- **Immigration**: When diversity drops below 0.15, inject 5-50 new random individuals
- **Adaptive Mutation**: Mutation rate increases from 0.3 to 0.7 when fitness stagnates
- **Early Stopping**: Terminates after 30 generations without improvement

### WoC Pattern Learning
- Analyzes top 20 solutions from evolved GA population
- Builds co-occurrence matrix showing VM affinity scores
- Uses variable affinity weights (0.2-0.95) for diverse solution generation
- Employs 3 initialization strategies (greedy, balanced, random)

## Performance & Results

### Typical Performance
The enhanced algorithm consistently finds optimal or near-optimal solutions:
- **Small scenarios**: Often finds theoretical optimum in Generation 1
- **Medium scenarios**: Converges to optimal within 5-10 generations
- **Large scenarios**: Achieves near-optimal solutions within 20-30 generations
- **Diversity**: Maintains 0.40-0.65 range throughout evolution
- **Convergence**: Early stopping after 30 stagnant generations prevents wasted computation

### Example Results (Medium Scenario, seed=42)
```
Scenario: 50 VMs, Server: 64 cores, 256GB RAM, 2TB storage

GA Results:
- Best: 11 servers
- Fitness: 1104.25
- Found in: Generation 1
- Final diversity: 0.45

WoC Results:
- Best: 11 servers  
- Fitness: 1104.25
- Improved solutions: 3 out of 10
```

### Understanding Results
- **Servers Used**: Primary metric - lower is better
- **Fitness Score**: `100 × servers + wasted_resources` - lower is better
- **Diversity**: 0.15-0.75 is healthy range (triggers immigration if < 0.15)
- **Generation 1 Optimum**: Indicates excellent initialization strategies working

## Solution Metrics

The `Solution` class provides comprehensive metrics:
- `num_servers_used`: Total servers with at least one VM (primary objective)
- `total_vms`: Total VMs successfully placed
- `average_utilization`: Average resource utilization across all dimensions
- `is_valid()`: Validates no capacity constraints are violated
- `fitness`: Evaluated by fitness function (lower is better)

## Fitness Function

The `SimpleFitnessEvaluator` uses a weighted formula:

```
fitness = (100 × num_servers_used) + wasted_resources
```

Where:
- **100× server weight**: Strongly prioritizes minimizing server count
- **wasted_resources**: Sum of unused CPU, RAM, and storage across all servers
- **Result**: Solutions with fewer servers always score better, with utilization as tiebreaker

## Troubleshooting

### GUI doesn't launch
- Ensure tkinter is installed: `python3 -m tkinter` (should open a test window)
- On Linux: `sudo apt-get install python3-tk`
- On macOS: tkinter is included with Python

### "No module named 'numpy'"
```bash
pip install numpy
```

### Results seem too good (finds optimum immediately)
This is expected! The enhanced algorithm with 8 initialization strategies and smart mutations often finds optimal solutions in the first generation, especially for smaller scenarios. This demonstrates the effectiveness of the improvements.

## References

### Core Problem & Complexity
1. **Garey, M. R., & Johnson, D. S. (1979)**. *Computers and Intractability: A Guide to the Theory of NP-Completeness*. W.H. Freeman.
   - Establishes bin packing as NP-Complete problem

2. **Lodi, A., Martello, S., & Vigo, D. (2002)**. "Recent advances on two-dimensional bin packing problems." *Discrete Applied Mathematics*, 123(1-3), 379-396.
   - Multi-dimensional bin packing formalization

### Genetic Algorithms
3. **Goldberg, D. E. (1989)**. *Genetic Algorithms in Search, Optimization, and Machine Learning*. Addison-Wesley.
   - Foundational GA concepts: selection, crossover, mutation, elitism

4. **Falkenauer, E. (1996)**. "A hybrid grouping genetic algorithm for bin packing." *Journal of Heuristics*, 2(1), 5-30.
   - Grouping genetic algorithms for bin packing problems
   - Specialized chromosome representations

5. **Eiben, A. E., & Smith, J. E. (2015)**. *Introduction to Evolutionary Computing* (2nd ed.). Springer.
   - Adaptive mutation rates (Chapter 6)
   - Diversity preservation techniques (Chapter 9)

### Heuristic Approaches
6. **Johnson, D. S. (1973)**. "Near-optimal bin packing algorithms." Doctoral Dissertation, MIT.
   - Best-Fit Decreasing (BFD) heuristic
   - Worst-Fit heuristic
   - First-Fit Decreasing (FFD)

7. **Coffman Jr, E. G., Garey, M. R., & Johnson, D. S. (1996)**. "Approximation algorithms for bin packing: A survey." *Approximation Algorithms for NP-hard Problems*, 46-93.
   - Performance bounds for FFD and BFD heuristics

### Wisdom of Crowds & Pattern Learning
8. **Surowiecki, J. (2004)**. *The Wisdom of Crowds: Why the Many Are Smarter Than the Few*. Doubleday.
   - Collective intelligence principles

9. **Nguyen, S., Zhang, M., Johnston, M., & Tan, K. C. (2013)**. "A computational study of representations in genetic programming to evolve dispatching rules for the job shop scheduling problem." *IEEE Transactions on Evolutionary Computation*, 17(5), 621-639.
   - Learning patterns from evolved solutions
   - Knowledge extraction from populations

### Diversity Mechanisms
10. **Cobb, H. G., & Grefenstette, J. J. (1993)**. "Genetic algorithms for tracking changing environments." *Proceedings of the 5th International Conference on Genetic Algorithms*, 523-530.
    - Immigration as diversity maintenance

11. **Črepinšek, M., Liu, S. H., & Mernik, M. (2013)**. "Exploration and exploitation in evolutionary algorithms: A survey." *ACM Computing Surveys*, 45(3), 1-33.
    - Adaptive parameter control
    - Diversity measures (Hamming distance)

### Cloud Computing & VM Placement
12. **Beloglazov, A., & Buyya, R. (2012)**. "Optimal online deterministic algorithms and adaptive heuristics for energy and performance efficient dynamic consolidation of virtual machines in cloud data centers." *Concurrency and Computation: Practice and Experience*, 24(13), 1397-1420.
    - VM consolidation strategies
    - Resource utilization optimization

13. **Xu, J., & Fortes, J. A. (2010)**. "Multi-objective virtual machine placement in virtualized data center environments." *2010 IEEE/ACM International Conference on Green Computing and Communications*, 179-188.
    - Multi-dimensional resource constraints
    - Fitness function design for VM placement

### Hybrid Approaches
14. **Talbi, E. G. (2009)**. *Metaheuristics: From Design to Implementation*. Wiley.
    - Hybrid metaheuristics (Chapter 9)
    - Combining evolutionary algorithms with constructive heuristics

15. **Poli, R., Langdon, W. B., & McPhee, N. F. (2008)**. *A Field Guide to Genetic Programming*. Lulu Enterprises.
    - Available free at: http://www.gp-field-guide.org.uk
    - Practical implementation guidance

### Implementation-Specific Techniques
- **Tournament Selection**: Goldberg & Deb (1991), "A comparative analysis of selection schemes"
- **Elitism**: De Jong (1975), "An analysis of the behavior of a class of genetic adaptive systems"
- **Early Stopping**: No Free Lunch theorems (Wolpert & Macready, 1997)
- **Co-occurrence Matrices**: Applied from association rule mining (Agrawal & Srikant, 1994)

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
