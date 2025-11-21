#!/usr/bin/env python3
"""
Update vis_11_convergence_curves.html to include Azure data comparison.

Extracts convergence data from the benchmark log and creates side-by-side
comparison charts showing GA convergence on both synthetic and Azure data.
"""

import re
from pathlib import Path


def extract_convergence_from_log(log_path: str):
    """Extract convergence data from the benchmark log file."""

    with open(log_path, 'r') as f:
        log_content = f.read()

    # Find all "Benchmarking" sections and extract data until the next one
    benchmark_pattern = r'Benchmarking (SMALL|MEDIUM|LARGE|EXTRA_LARGE) scenario with (SYNTHETIC|AZURE) data'

    matches = list(re.finditer(benchmark_pattern, log_content))

    results = {}

    for i, match in enumerate(matches):
        scenario = match.group(1).lower()
        data_source = match.group(2).lower()

        # Skip extra_large for convergence (we only want small/medium/large)
        if scenario == 'extra_large':
            continue

        key = f"{scenario}_{data_source}"

        # Extract content from this match to the next match (or end of file)
        start_pos = match.end()
        end_pos = matches[i+1].start() if i+1 < len(matches) else len(log_content)
        section_content = log_content[start_pos:end_pos]

        # Extract generation data
        gen_pattern = r'Gen\s+(\d+):\s+Best=([\d.]+)\s+\((\d+)s\),\s+Avg=([\d.]+)'

        generations = []
        best_fitness = []
        avg_fitness = []
        servers = []

        for gen_match in re.finditer(gen_pattern, section_content):
            gen = int(gen_match.group(1))
            best_fit = float(gen_match.group(2))
            server_count = int(gen_match.group(3))
            avg_fit = float(gen_match.group(4))

            generations.append(gen)
            best_fitness.append(best_fit)
            servers.append(server_count)
            avg_fitness.append(avg_fit)

        if generations:
            results[key] = {
                'generations': generations,
                'best_fitness': best_fitness,
                'avg_fitness': avg_fitness,
                'servers': servers
            }

    return results


def create_updated_html(convergence_data):
    """Create updated HTML with synthetic and Azure comparison."""

    html = '''<!DOCTYPE html>
<html>
<head>
    <title>GA Convergence: Synthetic vs Azure Data</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body { font-family: Arial; max-width: 1800px; margin: 0 auto; padding: 20px; background: #f0f0f0; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #2c3e50; }
        h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 40px; }
        .note { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #2196f3; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
        .chart { background: #f8f9fa; padding: 20px; border-radius: 8px; }
        .insight { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }
        .comparison { background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #4caf50; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; margin: 0 5px; }
        .badge-syn { background: #2196f3; color: white; }
        .badge-azure { background: #ff9800; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>GA Convergence: Synthetic vs Azure Production Data</h1>

        <div class="note">
            <strong>Comparing Evolutionary Behavior:</strong> How does GA convergence differ between controlled
            synthetic data and real-world Azure production traces?<br><br>
            <span class="badge badge-syn">SYNTHETIC</span> Pattern-based generation with balanced VM distributions<br>
            <span class="badge badge-azure">AZURE</span> Real Microsoft production data (5.5M VMs, OSDI 2020)
        </div>

        <h2>Small Scenario (20 VMs)</h2>
        <div class="grid">
            <div class="chart">
                <div id="small-fitness"></div>
            </div>
            <div class="chart">
                <div id="small-servers"></div>
            </div>
        </div>

        <div class="comparison">
            <strong>Convergence Comparison:</strong><br>
            • <span class="badge badge-syn">SYNTHETIC</span> 8 → 5 servers in 8 generations (final: 502.6 fitness)<br>
            • <span class="badge badge-azure">AZURE</span> 9 → 4 servers in 20 generations (final: 403.6 fitness)<br>
            → Azure data converges to fewer servers but takes longer to find optimal solution
        </div>

        <h2>Medium Scenario (50 VMs)</h2>
        <div class="grid">
            <div class="chart">
                <div id="medium-fitness"></div>
            </div>
            <div class="chart">
                <div id="medium-servers"></div>
            </div>
        </div>

        <div class="comparison">
            <strong>Convergence Comparison:</strong><br>
            • <span class="badge badge-syn">SYNTHETIC</span> 20 → 6 servers in 22 generations (final: 601.9 fitness)<br>
            • <span class="badge badge-azure">AZURE</span> 23 → 12 servers in 91 generations (final: 1205.2 fitness)<br>
            → Azure requires more servers due to unbalanced resource profiles, takes longer to converge
        </div>

        <h2>Large Scenario (100 VMs)</h2>
        <div class="grid">
            <div class="chart">
                <div id="large-fitness"></div>
            </div>
            <div class="chart">
                <div id="large-servers"></div>
            </div>
        </div>

        <div class="comparison">
            <strong>Convergence Comparison:</strong><br>
            • <span class="badge badge-syn">SYNTHETIC</span> 41 → 8 servers in 55 generations (final: 803.3 fitness)<br>
            • <span class="badge badge-azure">AZURE</span> 44 → 21 servers in 76 generations (final: 2106.0 fitness)<br>
            → Both show steady improvement, but Azure's real-world complexity requires significantly more servers
        </div>

        <div class="note">
            <h3>Key Insights from Convergence Comparison:</h3>
            <ul>
                <li><strong>Convergence Speed:</strong> Synthetic data converges faster (fewer generations needed)</li>
                <li><strong>Final Server Count:</strong> Azure often requires 2-3× more servers due to resource imbalances</li>
                <li><strong>Fitness Difference:</strong> Azure has higher final fitness due to challenging resource constraints</li>
                <li><strong>Optimization Difficulty:</strong> Real-world data shows more gradual improvement, suggesting harder optimization landscape</li>
                <li><strong>Algorithm Robustness:</strong> GA successfully optimizes both data types, demonstrating generalization ability</li>
            </ul>
        </div>
    </div>

    <script>
'''

    # Add JavaScript charts for each scenario
    # Small Scenario
    small_syn = convergence_data.get('small_synthetic', {})
    small_az = convergence_data.get('small_azure', {})

    html += f'''
        // Small Scenario - Fitness Convergence
        var smallFitnessData = [
            {{
                x: {small_syn.get('generations', [])},
                y: {small_syn.get('best_fitness', [])},
                mode: 'lines+markers',
                name: 'Synthetic - Best',
                line: {{color: '#2196f3', width: 3}},
                marker: {{size: 6}}
            }},
            {{
                x: {small_syn.get('generations', [])},
                y: {small_syn.get('avg_fitness', [])},
                mode: 'lines',
                name: 'Synthetic - Avg',
                line: {{color: '#64b5f6', width: 2, dash: 'dash'}}
            }},
            {{
                x: {small_az.get('generations', [])},
                y: {small_az.get('best_fitness', [])},
                mode: 'lines+markers',
                name: 'Azure - Best',
                line: {{color: '#ff9800', width: 3}},
                marker: {{size: 6}}
            }},
            {{
                x: {small_az.get('generations', [])},
                y: {small_az.get('avg_fitness', [])},
                mode: 'lines',
                name: 'Azure - Avg',
                line: {{color: '#ffb74d', width: 2, dash: 'dash'}}
            }}
        ];

        var smallFitnessLayout = {{
            title: 'Small (20 VMs) - Fitness Convergence',
            xaxis: {{title: 'Generation'}},
            yaxis: {{title: 'Fitness (lower is better)'}},
            showlegend: true,
            legend: {{orientation: 'h', y: -0.2}}
        }};

        Plotly.newPlot('small-fitness', smallFitnessData, smallFitnessLayout, {{responsive: true}});

        // Small Scenario - Server Count
        var smallServersData = [
            {{
                x: {small_syn.get('generations', [])},
                y: {small_syn.get('servers', [])},
                mode: 'lines+markers',
                name: 'Synthetic',
                line: {{color: '#2196f3', width: 3}},
                marker: {{size: 8}}
            }},
            {{
                x: {small_az.get('generations', [])},
                y: {small_az.get('servers', [])},
                mode: 'lines+markers',
                name: 'Azure',
                line: {{color: '#ff9800', width: 3}},
                marker: {{size: 8}}
            }}
        ];

        var smallServersLayout = {{
            title: 'Small (20 VMs) - Server Count Reduction',
            xaxis: {{title: 'Generation'}},
            yaxis: {{title: 'Number of Servers', dtick: 1}},
            showlegend: true,
            legend: {{orientation: 'h', y: -0.2}}
        }};

        Plotly.newPlot('small-servers', smallServersData, smallServersLayout, {{responsive: true}});
'''

    # Medium Scenario
    medium_syn = convergence_data.get('medium_synthetic', {})
    medium_az = convergence_data.get('medium_azure', {})

    html += f'''
        // Medium Scenario - Fitness Convergence
        var mediumFitnessData = [
            {{
                x: {medium_syn.get('generations', [])},
                y: {medium_syn.get('best_fitness', [])},
                mode: 'lines+markers',
                name: 'Synthetic - Best',
                line: {{color: '#2196f3', width: 3}},
                marker: {{size: 6}}
            }},
            {{
                x: {medium_syn.get('generations', [])},
                y: {medium_syn.get('avg_fitness', [])},
                mode: 'lines',
                name: 'Synthetic - Avg',
                line: {{color: '#64b5f6', width: 2, dash: 'dash'}}
            }},
            {{
                x: {medium_az.get('generations', [])},
                y: {medium_az.get('best_fitness', [])},
                mode: 'lines+markers',
                name: 'Azure - Best',
                line: {{color: '#ff9800', width: 3}},
                marker: {{size: 6}}
            }},
            {{
                x: {medium_az.get('generations', [])},
                y: {medium_az.get('avg_fitness', [])},
                mode: 'lines',
                name: 'Azure - Avg',
                line: {{color: '#ffb74d', width: 2, dash: 'dash'}}
            }}
        ];

        var mediumFitnessLayout = {{
            title: 'Medium (50 VMs) - Fitness Convergence',
            xaxis: {{title: 'Generation'}},
            yaxis: {{title: 'Fitness (lower is better)'}},
            showlegend: true,
            legend: {{orientation: 'h', y: -0.2}}
        }};

        Plotly.newPlot('medium-fitness', mediumFitnessData, mediumFitnessLayout, {{responsive: true}});

        // Medium Scenario - Server Count
        var mediumServersData = [
            {{
                x: {medium_syn.get('generations', [])},
                y: {medium_syn.get('servers', [])},
                mode: 'lines+markers',
                name: 'Synthetic',
                line: {{color: '#2196f3', width: 3}},
                marker: {{size: 8}}
            }},
            {{
                x: {medium_az.get('generations', [])},
                y: {medium_az.get('servers', [])},
                mode: 'lines+markers',
                name: 'Azure',
                line: {{color: '#ff9800', width: 3}},
                marker: {{size: 8}}
            }}
        ];

        var mediumServersLayout = {{
            title: 'Medium (50 VMs) - Server Count Reduction',
            xaxis: {{title: 'Generation'}},
            yaxis: {{title: 'Number of Servers', dtick: 2}},
            showlegend: true,
            legend: {{orientation: 'h', y: -0.2}}
        }};

        Plotly.newPlot('medium-servers', mediumServersData, mediumServersLayout, {{responsive: true}});
'''

    # Large Scenario
    large_syn = convergence_data.get('large_synthetic', {})
    large_az = convergence_data.get('large_azure', {})

    html += f'''
        // Large Scenario - Fitness Convergence
        var largeFitnessData = [
            {{
                x: {large_syn.get('generations', [])},
                y: {large_syn.get('best_fitness', [])},
                mode: 'lines+markers',
                name: 'Synthetic - Best',
                line: {{color: '#2196f3', width: 3}},
                marker: {{size: 5}}
            }},
            {{
                x: {large_syn.get('generations', [])},
                y: {large_syn.get('avg_fitness', [])},
                mode: 'lines',
                name: 'Synthetic - Avg',
                line: {{color: '#64b5f6', width: 2, dash: 'dash'}}
            }},
            {{
                x: {large_az.get('generations', [])},
                y: {large_az.get('best_fitness', [])},
                mode: 'lines+markers',
                name: 'Azure - Best',
                line: {{color: '#ff9800', width: 3}},
                marker: {{size: 5}}
            }},
            {{
                x: {large_az.get('generations', [])},
                y: {large_az.get('avg_fitness', [])},
                mode: 'lines',
                name: 'Azure - Avg',
                line: {{color: '#ffb74d', width: 2, dash: 'dash'}}
            }}
        ];

        var largeFitnessLayout = {{
            title: 'Large (100 VMs) - Fitness Convergence',
            xaxis: {{title: 'Generation'}},
            yaxis: {{title: 'Fitness (lower is better)'}},
            showlegend: true,
            legend: {{orientation: 'h', y: -0.2}}
        }};

        Plotly.newPlot('large-fitness', largeFitnessData, largeFitnessLayout, {{responsive: true}});

        // Large Scenario - Server Count
        var largeServersData = [
            {{
                x: {large_syn.get('generations', [])},
                y: {large_syn.get('servers', [])},
                mode: 'lines+markers',
                name: 'Synthetic',
                line: {{color: '#2196f3', width: 3}},
                marker: {{size: 7}}
            }},
            {{
                x: {large_az.get('generations', [])},
                y: {large_az.get('servers', [])},
                mode: 'lines+markers',
                name: 'Azure',
                line: {{color: '#ff9800', width: 3}},
                marker: {{size: 7}}
            }}
        ];

        var largeServersLayout = {{
            title: 'Large (100 VMs) - Server Count Reduction',
            xaxis: {{title: 'Generation'}},
            yaxis: {{title: 'Number of Servers', dtick: 5}},
            showlegend: true,
            legend: {{orientation: 'h', y: -0.2}}
        }};

        Plotly.newPlot('large-servers', largeServersData, largeServersLayout, {{responsive: true}});
'''

    html += '''
    </script>
</body>
</html>
'''

    return html


def main():
    """Update convergence curves visualization with Azure comparison."""

    print("="*80)
    print("UPDATING vis_11_convergence_curves.html WITH AZURE DATA")
    print("="*80)
    print()

    # Load convergence data from benchmark log
    log_path = 'azure_comparison_log.txt'

    if not Path(log_path).exists():
        print(f"✗ Error: {log_path} not found!")
        print("  Please run generate_azure_comparison.py first.")
        return 1

    print(f"Reading convergence data from {log_path}...")
    convergence_data = extract_convergence_from_log(log_path)

    print(f"✓ Extracted convergence data for {len(convergence_data)} scenarios:")
    for key in sorted(convergence_data.keys()):
        data = convergence_data[key]
        print(f"  • {key}: {len(data['generations'])} generations")
    print()

    # Generate updated HTML
    print("Generating updated HTML...")
    html_content = create_updated_html(convergence_data)

    # Write to presentation_visuals/
    output_path = 'presentation_visuals/vis_11_convergence_curves.html'
    with open(output_path, 'w') as f:
        f.write(html_content)

    print(f"✓ Updated: {output_path}")
    print()

    print("="*80)
    print("✅ CONVERGENCE VISUALIZATION UPDATED!")
    print("="*80)
    print()
    print("View the updated visualization:")
    print(f"  open {output_path}")
    print()

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
