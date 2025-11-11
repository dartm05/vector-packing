# Quick Reference - Running the Project

## 🚀 Fast Start

```bash
# 1. Install dependencies (first time only)
pip install -r requirements.txt

# 2. Run the solver
python main.py
```

That's it! The GA will solve a VM placement problem and show results.

---

## 📋 Common Commands

```bash
# Small problem (20 VMs) - Quick test
python main.py

# Medium problem (50 VMs)
python main.py --scenario medium

# Large problem (100 VMs) with local search
python main.py --scenario large --local-search

# Custom: Big population, high mutation
python main.py --scenario medium --population 100 --mutation-rate 0.4

# Run tests
python test_ga_convergence.py
pytest tests/ -v
```

---

## ⚙️ Key Parameters

| Parameter | Values | What it does |
|-----------|--------|--------------|
| `--scenario` | small/medium/large/extra_large | Problem size (20-200 VMs) |
| `--population` | 30-200 | More = better exploration, slower |
| `--generations` | 50-300 | More = longer search |
| `--mutation-rate` | 0.2-0.5 | Higher = more random changes |
| `--local-search` | flag | Enable hybrid GA+local search |

---

## 📊 Understanding Output

```
Generation 12/100: Best=532.18 (5 servers), Worst=642.62, Stagnation=11, MutRate=0.46
```
- **Best=532.18**: Best fitness (lower is better)
- **(5 servers)**: Solution uses 5 servers
- **Stagnation=11**: No improvement for 11 generations
- **MutRate=0.46**: Current mutation rate (adapts automatically)

---

## 🎯 What's the Goal?

**Minimize servers** while **maximizing utilization**
- Fewer servers = Lower cost
- High utilization = Less waste
- Valid solution = All VMs fit

---

## 💡 Tips

1. **Quick test**: Use `--generations 20` for faster results
2. **Better results**: Increase `--population` and use `--local-search`
3. **Stuck?**: Try different `--seed` values
4. **Compare**: Run multiple times with different parameters

 