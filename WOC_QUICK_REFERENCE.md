# WoC Quick Reference Card

## 🚀 Quick Start

### Run Console Demo
```bash
python examples/woc_example.py
```

### Run GUI
```bash
python examples/woc_example.py --gui
```

### Run Tests
```bash
pytest tests/test_woc.py -v
```

## 💻 Code Usage

### Basic WoC Workflow
```python
from src.woc import CrowdAnalyzer, CrowdBuilder

# 1. Analyze solutions
analyzer = CrowdAnalyzer()
analyzer.analyze_solutions(population, top_k=20)

# 2. Build new solutions
builder = CrowdBuilder(analyzer)
new_solutions = builder.build_multiple_solutions(
    vms, server_template, num_solutions=10, affinity_weight=0.7
)
```

### Get Affinity Information
```python
# Check affinity between two VMs
score = analyzer.get_affinity_score(vm1_id, vm2_id)

# Find best companions
companions = analyzer.get_best_companions(vm_id, candidate_ids, top_n=5)

# Get statistics
stats = analyzer.get_statistics()
print(f"Analyzed {stats['solutions_analyzed']} solutions")
print(f"Found {stats['vm_pairs_found']} VM pairs")
```

### Visualize Results
```python
from examples.woc_example import (
    visualize_solution,
    visualize_affinity_matrix,
    compare_solutions_visual
)

# Visualize a solution
visualize_solution(solution, "My Solution")
plt.show()

# Show affinity patterns
visualize_affinity_matrix(analyzer, vms, top_n=15)
plt.show()

# Compare GA vs WoC
compare_solutions_visual(ga_solution, woc_solution)
plt.show()
```

## 🎛️ GUI Controls

| Button | Function |
|--------|----------|
| 🚀 Run GA | Execute Genetic Algorithm |
| 🧠 Run WoC | Run Wisdom of Crowds analysis |
| 📊 Show GA Solution | Visualize GA results |
| 📈 Show WoC Solution | Visualize WoC results |
| 🔍 Show Affinity | Display affinity heatmap |
| ⚖️ Compare | Compare GA vs WoC |

## ⚙️ Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| num_vms | 30 | Number of virtual machines |
| generations | 20 | GA generations to run |
| population_size | 50 | GA population size |
| affinity_weight | 0.7 | Pattern vs random (0.0-1.0) |
| top_k | 20 | Top solutions to analyze |

### Affinity Weight Guide
- `1.0` - Pure exploitation (always follow patterns)
- `0.7` - Mostly patterns, some exploration
- `0.5` - Balanced approach
- `0.3` - Mostly exploration, some patterns
- `0.0` - Pure exploration (random)

## 📊 Interpreting Results

### Affinity Score
- `1.0` = VMs always placed together (perfect affinity)
- `0.5` = VMs together half the time
- `0.0` = VMs never together (no affinity)

### Fitness Score
- **Lower is better** (minimization problem)
- Primary factor: Number of servers (×100)
- Secondary: Resource waste
- Tertiary: Balance penalty

### Good Solution Signs
- ✅ High average utilization (>60%)
- ✅ Balanced CPU/RAM/Storage usage
- ✅ Few servers used
- ✅ Valid (no capacity violations)

## 🔍 Troubleshooting

### "Please run GA first!"
→ WoC requires GA to complete before analyzing

### GUI won't launch
→ Check tkinter installation: `python -m tkinter`

### No affinity patterns found
→ Run with larger population or more solutions

### Poor WoC performance
→ Try adjusting affinity_weight or analyzing more solutions

## 📁 File Locations

```
vector-packing/
├── src/woc/
│   ├── crowd_analyzer.py    # Pattern discovery
│   ├── crowd_builder.py     # Solution construction
│   └── __init__.py           # Module exports
├── examples/
│   ├── woc_example.py        # Main example (GUI + console)
│   └── GUI_README.md         # GUI documentation
├── tests/
│   └── test_woc.py           # Unit tests
└── WOC_DOCUMENTATION.md      # Full documentation
```

## 📚 Documentation

- **Technical docs**: `WOC_DOCUMENTATION.md`
- **GUI guide**: `examples/GUI_README.md`
- **Summary**: `WOC_IMPLEMENTATION_SUMMARY.md`
- **This card**: `WOC_QUICK_REFERENCE.md`

## 🎯 Common Tasks

### Task: Compare GA and WoC
```bash
python examples/woc_example.py --gui
# Click: Run GA → Run WoC → Compare
```

### Task: See VM patterns
```bash
python examples/woc_example.py --gui
# Click: Run GA → Run WoC → Show Affinity
```

### Task: Export visualization
```python
fig = visualize_solution(solution)
fig.savefig('my_solution.png', dpi=300, bbox_inches='tight')
```

### Task: Batch analyze
```python
for i in range(10):
    solution = builder.build_solution(vms, server_template, affinity_weight=i/10)
    print(f"Weight {i/10}: {solution.num_servers_used} servers")
```

---

**Quick Help**: Run `python examples/woc_example.py --gui` for interactive exploration!
