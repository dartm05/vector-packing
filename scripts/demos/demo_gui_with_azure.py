#!/usr/bin/env python3
"""
Demo Script: GUI with Azure Data

This script demonstrates using the enhanced GUI with Azure data support.
It provides instructions for comparing synthetic vs Azure data.
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys

# Check if Azure dataset exists
azure_db_path = 'datasets/packing_trace_zone_a_v1.sqlite'
azure_exists = os.path.exists(azure_db_path)

def show_instructions():
    """Show instructions before launching GUI"""
    root = tk.Tk()
    root.withdraw()  # Hide main window

    instructions = """
╔════════════════════════════════════════════════════════════════╗
║          Vector Packing GUI - Azure Data Enabled!              ║
╚════════════════════════════════════════════════════════════════╝

WHAT'S NEW:
• Data Source selector: Choose "synthetic" or "azure"
• Real Azure production VM data (5.5M VMs from OSDI 2020)
• Visual indicators showing which data source is active
• Enhanced statistics including theoretical minimum servers

HOW TO USE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: SELECT DATA SOURCE
   • Scenario: small, medium, large, or extra_large
   • Data Source: "synthetic" (your designed patterns)
                   "azure" (real Microsoft data)
   • Random Seed: 42 (for reproducibility)

Step 2: RUN EXPERIMENTS
   • "Run GA" - Run Genetic Algorithm only
   • "Run WoC" - Run Wisdom of Crowds (needs GA first)
   • "Run Both" - Run GA then WoC automatically

Step 3: COMPARE RESULTS
   • Click "Compare Results" to see side-by-side analysis
   • Note the data source badge:  SYNTHETIC or AZURE

EXPERIMENT IDEAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. COMPARE DATA SOURCES (Same Algorithm):
   a) Run GA on synthetic small scenario
   b) Run GA on azure small scenario
   c) Compare: How do results differ?

2. COMPARE ALGORITHMS (Same Data):
   a) Select azure medium data
   b) Run Both (GA + WoC)
   c) Compare: WoC speed vs quality

3. PATTERN DISCOVERY TEST:
   a) Run GA on synthetic data (has known patterns)
   b) Check console for "VM affinity patterns"
   c) Run WoC - does it discover small/medium/large groups?

4. SCALABILITY TEST:
   a) Run azure small → medium → large
   b) Observe: How do times scale?
   c) Compare: GA vs WoC speedup at each scale

AZURE DATA CHARACTERISTICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Small scenario (20 VMs):
  - Sampled from 860K active Azure VMs
  - 90% small VMs (microservices)
  - Real production resource patterns
  - Theoretical min: ~3 servers

• Medium scenario (50 VMs):
  - Greater variance in VM sizes
  - Mixed CPU/RAM/storage requirements
  - Theoretical min: ~7 servers

• Large & Extra Large:
  - Even more realistic heterogeneity
  - Tests algorithm scalability

CONSOLE OUTPUT GUIDE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When loading Azure data, you'll see:
  ✓ Loaded REAL Azure production data
  Source: Azure Packing Trace 2020
  Original pool: 799,479 VMs    ← Size of full dataset
  VMs loaded: 20               ← Your sample size
  Total demand: ...            ← Resource requirements
  Theoretical minimum: 2.74 servers (~3 required)

When running GA/WoC:
  • Generation-by-generation progress
  • Best fitness improvements
  • Final server count and utilization
  • Execution time

TIPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Start with "small" scenarios for quick testing
✓ Use seed=42 for reproducible experiments
✓ Watch the console for detailed progress
✓ Azure data takes slightly longer to load (database query)
✓ Compare fitness values between synthetic and Azure
✓ Notice how WoC speedup varies with data source

TROUBLESHOOTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If Azure dataset not found:
  1. Run: python3 test_azure_loader.py
  2. This downloads the dataset automatically
  3. Then restart the GUI

If results seem odd:
  • Check seed value (use 42 for consistency)
  • Verify data source selector matches intent
  • Check console for error messages

═══════════════════════════════════════════════════════════════

Ready to launch GUI?
"""

    if not azure_exists:
        instructions += """
 WARNING: Azure dataset not found!

The Azure dataset is not yet downloaded. You can still use
synthetic data, but Azure data won't be available.

To download Azure data:
  1. Click OK to close this dialog
  2. Open a terminal
  3. Run: python3 test_azure_loader.py
  4. Wait for download (~51 MB)
  5. Restart the GUI

Or click OK now to launch with synthetic data only.
"""
    else:
        instructions += f"""
✓ Azure dataset found! ({os.path.getsize(azure_db_path) / (1024*1024):.1f} MB)
  Both synthetic and Azure data are ready to use.

Click OK to launch the GUI!
"""

    messagebox.showinfo("GUI Demo - Instructions", instructions)
    root.destroy()


if __name__ == '__main__':
    # Show instructions
    show_instructions()

    # Launch the GUI
    print("\n" + "="*70)
    print("LAUNCHING VECTOR PACKING GUI WITH AZURE DATA SUPPORT")
    print("="*70)

    if azure_exists:
        print("✓ Azure dataset: AVAILABLE")
        print(f"  Location: {azure_db_path}")
        print(f"  Size: {os.path.getsize(azure_db_path) / (1024*1024):.1f} MB")
    else:
        print("✗ Azure dataset: NOT FOUND")
        print("  Run 'python3 test_azure_loader.py' to download")

    print("\n" + "="*70)
    print("TIP: Select 'azure' from the Data Source dropdown to use real data")
    print("="*70 + "\n")

    # Import and launch GUI
    import gui
    root = tk.Tk()
    app = gui.VectorPackingGUI(root)
    root.mainloop()
