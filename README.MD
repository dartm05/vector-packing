# Vector Packing Solver - GA + WoC Hybrid Approach

A modular base structure for implementing a hybrid Genetic Algorithm (GA) and Wisdom of Crowds (WoC) approach to solve the Multi-Dimensional Bin Packing Problem, with application to cloud computing resource allocation.

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
Evolutionary optimization technique that mimics natural selection to find good VM-to-server assignments.

### Wisdom of Crowds (WoC)
Analyzes patterns in successful solutions to discover which VMs work well together, then uses this knowledge to build new solutions.

### Hybrid Strategy
Combines GA's exploration capabilities with WoC's pattern recognition to achieve better results than either approach alone.

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
│   │   ├── fitness.py             # Fitness evaluation (base class)
│   │   ├── operators.py           # Selection, crossover, mutation (base classes)
│   │   └── chromosome.py          # Chromosome representation
│   │
│   ├── woc/                       # Wisdom of Crowds components
│   │   └── __init__.py            # (To be implemented)
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
├── config/
│   └── default_config.yaml        # Configuration file
│
├── requirements.txt               # Python dependencies
├── LICENSE
└── README.MD                      # This file
```

## Components Status

### Complete & Ready to Use

**Data Models (`src/models/`)**
- `VirtualMachine`: Represents a VM with CPU, RAM, and storage requirements
- `Server`: Represents a physical server with capacity constraints and VM tracking
- `Solution`: Represents a complete packing solution with validation and metrics

**Utilities (`src/utils/`)**
- `DataGenerator`: Generate test datasets with various scenarios (small, medium, large, extra_large)
- `Logger`: Logging configuration and utilities

**Tests**
- Unit tests for models
- Unit tests for utilities

### Base Classes (To Be Implemented)

**GA Components (`src/ga/`)**
- `FitnessEvaluator`: Abstract base class for fitness functions
- `SelectionOperator`: Abstract base class for selection strategies
- `CrossoverOperator`: Abstract base class for crossover operations
- `MutationOperator`: Abstract base class for mutation operations

**WoC Components (`src/woc/`)**
- Empty module - implement your pattern analysis and solution building here

**Main Script**
- Create `main.py` to orchestrate the complete algorithm

## Getting Started

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Explore the Models

```python
from src.models import VirtualMachine, Server, Solution

# Create a VM
vm = VirtualMachine(id=1, cpu_cores=4, ram_gb=16, storage_gb=100)

# Create a server
server = Server(id=1, max_cpu_cores=64, max_ram_gb=256, max_storage_gb=2000)

# Try to place the VM
if server.can_fit(vm):
    server.add_vm(vm)
    print(f"VM placed! Server utilization: {server.utilization}")
```

### 3. Generate Test Data

```python
from src.utils import DataGenerator

# Use a predefined scenario
scenario = DataGenerator.generate_scenario('medium', seed=42)
vms = scenario['vms']
server_template = scenario['server_template']

print(f"Generated {len(vms)} VMs")
print(f"Server capacity: {server_template.max_cpu_cores} cores, "
      f"{server_template.max_ram_gb} GB RAM, "
      f"{server_template.max_storage_gb} GB storage")
```

### 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage
pytest tests/ --cov=src
```

## Available Test Scenarios

The data generator provides four predefined scenarios:

| Scenario | VMs | Server Capacity | Difficulty |
|----------|-----|-----------------|------------|
| `small` | 20 | 32 cores, 128 GB RAM, 1 TB storage | Easy |
| `medium` | 50 | 64 cores, 256 GB RAM, 2 TB storage | Medium |
| `large` | 100 | 96 cores, 512 GB RAM, 4 TB storage | Hard |
| `extra_large` | 200 | 128 cores, 1 TB RAM, 8 TB storage | Very Hard |

## Implementation Guide

### Step 1: Implement Fitness Function
Create a concrete implementation of `FitnessEvaluator` that considers:
- Number of servers used (primary objective)
- Resource utilization (secondary objective)
- Penalties for invalid solutions

### Step 2: Implement GA Operators
Create concrete implementations of:
- **Selection**: Tournament, roulette wheel, rank-based, etc.
- **Crossover**: Uniform, one-point, two-point, etc.
- **Mutation**: Swap, inversion, scramble, etc.

### Step 3: Build GA Engine
Create `src/ga/ga_engine.py` with:
- Population initialization
- Evolution loop
- Elitism
- Termination conditions

### Step 4: Implement WoC
Create WoC components in `src/woc/`:
- Analyze patterns in successful GA solutions
- Build affinity/co-occurrence matrices
- Construct new solutions from patterns

### Step 5: Create Main Script
Create `main.py` to:
- Load configuration
- Generate or load test data
- Run GA
- Run WoC
- Compare results
- Export results

## Key Concepts

### Solution Metrics
- `num_servers_used`: Total servers with at least one VM
- `total_vms`: Total VMs successfully placed
- `average_utilization`: Average resource utilization across all dimensions
- `is_valid()`: Checks if solution violates any capacity constraints

### Fitness Considerations
Your fitness function should balance:
1. **Minimizing servers** (primary goal)
2. **Maximizing utilization** (efficiency)
3. **Balancing resources** (avoid hotspots)

## References

- **Multi-Dimensional Bin Packing**: NP-Complete optimization problem
- **Genetic Algorithms**: Evolutionary optimization technique
- **Wisdom of Crowds**: Collective intelligence approach
- **Cloud Computing**: VM placement and resource allocation

## License

See LICENSE file for details.

---

**Status**: Base structure complete. Ready for algorithm implementation.
