# Wisdom of Crowds (WOC) Implementation

## Overview

The Wisdom of Crowds module analyzes patterns from successful Genetic Algorithm solutions and uses collective intelligence to generate new solutions. It implements three key strategies:

1. **Affinity Matrix** - Learns which VMs tend to be placed together
2. **Solution Builder** - Constructs new solutions using learned patterns
3. **WOC Engine** - Orchestrates the learning and building process

## How It Works

### Phase 1: Learning
WOC analyzes the top N solutions from the GA population and builds a co-occurrence matrix:
- Tracks which VMs are frequently placed on the same server
- Weights better solutions more heavily
- Identifies affinity groups (VMs that work well together)

### Phase 2: Building
WOC generates new solutions using three strategies:

1. **Greedy Strategy** - Places VMs with highest affinity together
2. **Group-Based Strategy** - Packs pre-identified affinity groups
3. **Iterative Strategy** - Builds solutions iteratively with balanced resources

### Phase 3: Selection
Returns the best solution found across all strategies.

## Usage

### Command Line

```bash
# Run GA + WOC hybrid
python main.py --use-woc

# Customize WOC parameters
python main.py --use-woc --woc-solutions 50

# Run on larger problems
python main.py --scenario medium --use-woc
```

### Programmatic

```python
from src.woc.engine import run_woc
from src.ga.engine import create_initial_population

# Create GA population
ga_population = create_initial_population(vms, server_template, 50)

# Run WOC
best_woc_solution = run_woc(
    vms=vms,
    server_template=server_template,
    ga_population=ga_population,
    top_n=20,  # Learn from top 20 solutions
    num_solutions=30  # Generate 30 new solutions
)
```

## Components

### AffinityMatrix (`affinity_matrix.py`)
- Tracks VM co-occurrence patterns
- Identifies affinity groups
- Provides compatibility scores

### AffinityBasedBuilder (`solution_builder.py`)
- Implements three building strategies
- Uses affinity patterns to guide placement
- Balances affinity with resource constraints

### WisdomOfCrowdsEngine (`engine.py`)
- Main orchestration
- Learns from GA solutions
- Generates and evaluates new solutions

## Testing

```bash
# Compare GA vs WOC
python test_woc_comparison.py

# Test on specific scenario with WOC
python main.py --scenario large --use-woc
```

## Key Insights

### When WOC Helps
- **Pattern Discovery**: Identifies VM combinations that work well together
- **Diversity**: Generates solutions using different strategies
- **Exploitation**: Uses collective knowledge from multiple solutions

### When GA Helps
- **Exploration**: Searches the solution space broadly
- **Evolution**: Improves solutions over time
- **Adaptation**: Adjusts parameters dynamically

### Hybrid Approach
The combination of GA + WOC leverages both:
- GA explores and finds good solutions
- WOC learns patterns and exploits them
- Together they balance exploration and exploitation

## Results

For the test problems:
- Both approaches find optimal or near-optimal solutions
- WOC finds affinity groups (3 for small, 7 for medium problems)
- Solutions use same number of servers with similar utilization
- WOC provides alternative perspective on the problem

## Future Enhancements

1. **Weighted Voting**: Combine multiple WOC solutions
2. **Iterative Refinement**: Use WOC output to seed new GA run
3. **Adaptive Strategies**: Choose strategies based on problem characteristics
4. **Constraint Learning**: Learn which constraints are hardest to satisfy
5. **Meta-Learning**: Learn which building strategy works best for each problem type
