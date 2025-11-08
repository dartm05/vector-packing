# Wisdom of Crowds (WoC) Implementation

## Overview

The Wisdom of Crowds (WoC) module provides intelligent solution construction by learning from successful solutions in the Genetic Algorithm population. It implements two key components:

1. **CrowdAnalyzer**: Discovers patterns in successful solutions
2. **CrowdBuilder**: Constructs new solutions using discovered patterns

## How It Works

### The Intuition

When solving the vector packing problem, certain VMs naturally work well together because they have complementary resource profiles. For example:
- A CPU-heavy VM pairs well with a storage-heavy VM
- VMs with similar resource requirements may not fit well on the same server

The WoC approach observes which VMs are frequently placed together in high-quality solutions and uses this "crowd wisdom" to guide the construction of new solutions.

### CrowdAnalyzer

**Purpose**: Learn VM co-location patterns from successful solutions

**Key Features**:
- Tracks co-occurrence frequencies for VM pairs
- Calculates affinity scores between VMs
- Identifies which VMs work well together
- Provides statistics about discovered patterns

**Usage Example**:
```python
from src.woc import CrowdAnalyzer

analyzer = CrowdAnalyzer()
analyzer.analyze_solutions(population, top_k=20)  # Analyze top 20 solutions

# Get affinity between two VMs
score = analyzer.get_affinity_score(vm1_id, vm2_id)

# Find best companions for a VM
companions = analyzer.get_best_companions(vm_id, candidate_ids, top_n=5)

# Get analysis statistics
stats = analyzer.get_statistics()
```

**Affinity Calculation**:
The affinity score uses a Jaccard-like similarity:
```
affinity(VM_i, VM_j) = co_occurrences / (freq_i + freq_j - co_occurrences)
```
This gives a score between 0 and 1, where:
- 1.0 = VMs always appear together
- 0.0 = VMs never appear together

### CrowdBuilder

**Purpose**: Construct new solutions using learned patterns

**Key Features**:
- Builds solutions with affinity-guided VM placement
- Balances exploitation (using patterns) vs exploration (randomness)
- Generates diverse solutions with varying affinity weights
- Falls back gracefully when patterns aren't available

**Usage Example**:
```python
from src.woc import CrowdBuilder

builder = CrowdBuilder(analyzer)

# Build a single solution
solution = builder.build_solution(
    vms=vms,
    server_template=server_template,
    affinity_weight=0.7  # 70% pattern-based, 30% random
)

# Build multiple diverse solutions
solutions = builder.build_multiple_solutions(
    vms=vms,
    server_template=server_template,
    num_solutions=10,
    affinity_weight=0.7
)
```

**Affinity Weight Parameter**:
- `1.0`: Pure exploitation (always follow patterns)
- `0.5`: Balanced (50/50 patterns vs random)
- `0.0`: Pure exploration (ignore patterns)

## Integration with Genetic Algorithm

### Basic Integration

The simplest integration is to use WoC after GA completes:

```python
# 1. Run GA
best_solution = run_ga(vms, server_template, population_size=50, generations=20)

# 2. Create population for analysis
population = create_initial_population(vms, server_template, 30)
# Evaluate population...

# 3. Analyze with WoC
analyzer = CrowdAnalyzer()
analyzer.analyze_solutions(population, top_k=15)

# 4. Build new solutions
builder = CrowdBuilder(analyzer)
woc_solutions = builder.build_multiple_solutions(vms, server_template, 10)

# 5. Compare best solutions
```

### Advanced Integration (Hybrid GA+WoC)

For more sophisticated integration, you could:

1. **Periodic Injection**: Every N generations, inject WoC solutions into GA population
2. **Seeded Initial Population**: Use WoC to generate part of initial population
3. **Guided Mutation**: Use affinity patterns to guide mutation operators
4. **Adaptive Strategy**: Switch between GA and WoC based on progress

Example conceptual flow:
```python
for generation in range(max_generations):
    # Standard GA operations
    evaluate_population(population)
    new_population = evolve(population)
    
    # Every 5 generations, inject WoC solutions
    if generation % 5 == 0:
        analyzer.analyze_solutions(population, top_k=10)
        builder = CrowdBuilder(analyzer)
        woc_solutions = builder.build_multiple_solutions(vms, server, 5)
        new_population = replace_worst(new_population, woc_solutions)
    
    population = new_population
```

## When WoC Works Best

**Ideal Scenarios**:
- Large problem instances (many VMs)
- Clear resource complementarity patterns
- Sufficient diversity in GA population
- After GA has converged (to exploit discovered patterns)

**Less Effective When**:
- Very small problems (< 10 VMs)
- All VMs have similar resource profiles
- GA population lacks diversity
- Insufficient analysis (too few solutions analyzed)

## Performance Considerations

### Time Complexity

**CrowdAnalyzer**:
- `analyze_solutions(n solutions)`: O(n × s × v²)
  - n = number of solutions
  - s = average servers per solution
  - v = average VMs per server
- `get_affinity_score()`: O(1)
- `get_best_companions()`: O(c) where c = number of candidates

**CrowdBuilder**:
- `build_solution()`: O(v × s × c)
  - v = number of VMs
  - s = number of servers created
  - c = companion search operations

### Memory Usage

The co-occurrence matrix stores up to O(V²) VM pairs, where V is the total number of unique VMs across all analyzed solutions.

For typical problems:
- 100 VMs: ~10,000 pairs max
- 1000 VMs: ~1,000,000 pairs max

## Examples

See `examples/woc_example.py` for a complete demonstration of WoC usage.

To run:
```bash
cd /path/to/vector-packing
python examples/woc_example.py
```

## Extending the Implementation

### Custom Affinity Metrics

You could implement alternative affinity calculations:

```python
def get_resource_complementarity_affinity(self, vm1_id, vm2_id):
    """Affinity based on complementary resource profiles"""
    # Custom logic here
    pass
```

### Pattern-Based Mutation

Use affinity patterns in mutation operators:

```python
class AffinityGuidedMutation(MutationOperator):
    def __init__(self, analyzer):
        self.analyzer = analyzer
    
    def mutate(self, solution):
        # Use analyzer.get_best_companions() to guide VM moves
        pass
```

### Multi-Objective Affinity

Track patterns for multiple objectives:

```python
class MultiObjectiveAnalyzer(CrowdAnalyzer):
    def __init__(self):
        super().__init__()
        self.low_server_patterns = {}
        self.high_utilization_patterns = {}
```

## References

The Wisdom of Crowds concept in optimization:
- Combines collective intelligence from multiple solutions
- Similar to Ant Colony Optimization's pheromone trails
- Related to Estimation of Distribution Algorithms (EDAs)

Key insight: Good solutions share common structural patterns that can be extracted and reused.
