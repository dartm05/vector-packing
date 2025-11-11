# WoC Example with Visualization & GUI

This enhanced version of the WoC example includes comprehensive visualizations and an interactive GUI for exploring the Wisdom of Crowds algorithm.

## Features

### 📊 Visualizations

1. **Solution Visualization**
   - Server resource utilization (CPU, RAM, Storage)
   - VM distribution across servers
   - Average utilization pie chart
   - Detailed solution statistics

2. **Affinity Matrix Heatmap**
   - Visual representation of VM co-location patterns
   - Color-coded affinity scores
   - Helps identify which VMs work well together

3. **Comparison Charts**
   - Side-by-side GA vs WoC comparison
   - Server count, fitness score, and utilization metrics
   - Easy visual assessment of solution quality

### 🖥️ Interactive GUI

The GUI provides an intuitive interface to:
- Configure parameters (VM count, generations, population size, affinity weight)
- Run GA and WoC algorithms with real-time feedback
- View and compare results
- Generate visualizations on demand

## Usage

### Console Mode (Default)
Run the standard demonstration with text output:
```bash
python examples/woc_example.py
```

### GUI Mode
Launch the interactive GUI:
```bash
python examples/woc_example.py --gui
```

## GUI Instructions

1. **Set Parameters**:
   - Number of VMs: How many virtual machines to pack (default: 30)
   - GA Generations: Number of GA generations (default: 20)
   - Population Size: GA population size (default: 50)
   - Affinity Weight: Balance between pattern-based (1.0) and random (0.0) placement (default: 0.7)

2. **Run Algorithms**:
   - Click "🚀 Run GA" to execute the Genetic Algorithm
   - Click "🧠 Run WoC" to run Wisdom of Crowds analysis (requires GA to run first)

3. **View Results**:
   - "📊 Show GA Solution": Visualize the GA solution
   - "📈 Show WoC Solution": Visualize the WoC solution
   - "🔍 Show Affinity": Display VM affinity heatmap
   - "⚖️ Compare": Side-by-side comparison of GA vs WoC

4. **Monitor Progress**:
   - Results panel shows detailed output in real-time
   - Status bar indicates current operation

## Visualizations Explained

### Solution Visualization
- **Top Left**: Bar chart showing CPU, RAM, and Storage utilization per server
- **Top Right**: Horizontal bar chart of VM count per server
- **Bottom Left**: Pie chart of average resource utilization
- **Bottom Right**: Text box with detailed statistics

### Affinity Matrix
- **Heatmap**: Shows affinity scores between VM pairs
- **Color**: Red = high affinity (VMs frequently together), Yellow = low affinity
- **Values**: Scores from 0.0 (never together) to 1.0 (always together)

### Comparison View
- **Left Column**: GA solution metrics
- **Right Column**: WoC solution metrics
- **Metrics**: Server count, fitness score, and resource utilization

## Requirements

The visualization features require additional Python packages:
```bash
pip install matplotlib numpy
```

These are already included if you installed from `requirements.txt`.

## Tips

- Start with smaller VM counts (20-30) for faster experimentation
- Higher affinity weights (0.7-0.9) rely more on learned patterns
- Lower affinity weights (0.3-0.5) add more randomness/exploration
- The affinity matrix is most useful with 10-20 VMs for readability
- Compare multiple runs to see how WoC performs with different random seeds

## Example Workflow

1. Launch GUI: `python examples/woc_example.py --gui`
2. Adjust parameters as desired
3. Click "Run GA" and wait for completion
4. Click "Show GA Solution" to visualize
5. Click "Run WoC" to analyze and build WoC solutions
6. Click "Show WoC Solution" to visualize
7. Click "Show Affinity" to see learned patterns
8. Click "Compare" for side-by-side analysis

## Troubleshooting

**"Please run GA first!" warning**: 
- WoC requires GA to complete first to analyze solutions

**GUI won't launch**:
- Ensure matplotlib and tkinter are installed
- On some systems, tkinter requires separate installation

**Visualizations not showing**:
- Check that matplotlib is properly installed
- Try running in console mode first to verify the core logic works

## Extending the GUI

The `WoCGUI` class can be extended with:
- Real-time generation-by-generation visualization
- Export results to files
- Load/save configurations
- Batch processing multiple parameter sets
- Animation of solution evolution
