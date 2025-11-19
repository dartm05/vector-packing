#!/usr/bin/env python3
"""
Update visualization HTML files with new benchmark results.
"""

import json
import os

def load_results():
    """Load the benchmark results."""
    with open('updated_benchmark_results.json', 'r') as f:
        return json.load(f)

def update_performance_comparison(results):
    """Update vis_14_performance_comparison.html with new data."""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Performance Comparison: GA vs WOC</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{ font-family: Arial; max-width: 1400px; margin: 0 auto; padding: 20px; background: #f0f0f0; }}
        .container {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ text-align: center; color: #2c3e50; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 30px 0; }}
        .chart {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
        .summary {{ background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 30px 0; }}
        .summary h2 {{ margin-top: 0; color: #27ae60; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: center; border: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; font-weight: bold; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        .speedup {{ color: #27ae60; font-weight: bold; font-size: 18px; }}
        .note {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Performance Comparison: GA vs GA+WOC</h1>

        <div class="note">
            <strong>Note:</strong> Results generated with simplified GA engine using random initialization.
            Fitness values use 10× multiplier (not 100×) for better granularity.
        </div>

        <table>
            <thead>
                <tr>
                    <th>Scenario</th>
                    <th>VMs</th>
                    <th>Method</th>
                    <th>Time (s)</th>
                    <th>Servers</th>
                    <th>Fitness</th>
                    <th>Speedup</th>
                </tr>
            </thead>
            <tbody>
"""

    for result in results:
        scenario = result['scenario'].capitalize()
        vms = result['num_vms']
        ga = result['ga']
        woc = result['woc']

        html += f"""                <tr>
                    <td rowspan="2"><strong>{scenario}</strong></td>
                    <td rowspan="2">{vms}</td>
                    <td>GA</td>
                    <td>{ga['time_seconds']}</td>
                    <td>{ga['servers_used']}</td>
                    <td>{ga['fitness']}</td>
                    <td rowspan="2" class="speedup">{woc['speedup']}×</td>
                </tr>
                <tr>
                    <td>WOC</td>
                    <td style="background: #c8e6c9;">{woc['time_seconds']}</td>
                    <td>{woc['servers_used']}</td>
                    <td>{woc['fitness']}</td>
                </tr>
"""

    html += """            </tbody>
        </table>

        <div class="summary">
            <h2>Key Findings</h2>
            <ul>
                <li><strong>Simplified GA</strong> with random initialization shows clear improvement over generations</li>
                <li><strong>Fitness granularity</strong> improved from 100× to 10× multiplier - utilization changes now visible</li>
                <li><strong>WoC speed advantage</strong> maintained - builds solutions 8-80× faster than GA</li>
                <li><strong>Solution quality</strong> both methods find the same optimal solutions</li>
                <li><strong>Convergence</strong> GA now shows dramatic improvement (200+ servers → 11 servers on extra_large!)</li>
            </ul>
        </div>

        <div class="grid">
            <div class="chart">
                <div id="time-chart"></div>
            </div>
            <div class="chart">
                <div id="servers-chart"></div>
            </div>
        </div>

        <div class="grid">
            <div class="chart">
                <div id="fitness-chart"></div>
            </div>
            <div class="chart">
                <div id="speedup-chart"></div>
            </div>
        </div>
    </div>

    <script>
"""

    # Generate Plotly data from results
    scenarios = [r['scenario'].capitalize() for r in results]
    ga_times = [r['ga']['time_seconds'] for r in results]
    woc_times = [r['woc']['time_seconds'] for r in results]
    ga_servers = [r['ga']['servers_used'] for r in results]
    woc_servers = [r['woc']['servers_used'] for r in results]
    ga_fitness = [r['ga']['fitness'] for r in results]
    woc_fitness = [r['woc']['fitness'] for r in results]
    speedups = [r['woc']['speedup'] for r in results]

    html += f"""
        // Time Comparison
        var timeData = [
            {{
                x: {scenarios},
                y: {ga_times},
                name: 'GA',
                type: 'bar',
                marker: {{color: '#3498db'}}
            }},
            {{
                x: {scenarios},
                y: {woc_times},
                name: 'WOC',
                type: 'bar',
                marker: {{color: '#27ae60'}}
            }}
        ];
        var timeLayout = {{
            title: 'Execution Time Comparison',
            xaxis: {{title: 'Scenario'}},
            yaxis: {{title: 'Time (seconds)', type: 'log'}},
            barmode: 'group'
        }};
        Plotly.newPlot('time-chart', timeData, timeLayout);

        // Servers Comparison
        var serversData = [
            {{
                x: {scenarios},
                y: {ga_servers},
                name: 'GA',
                type: 'bar',
                marker: {{color: '#3498db'}}
            }},
            {{
                x: {scenarios},
                y: {woc_servers},
                name: 'WOC',
                type: 'bar',
                marker: {{color: '#27ae60'}}
            }}
        ];
        var serversLayout = {{
            title: 'Servers Used',
            xaxis: {{title: 'Scenario'}},
            yaxis: {{title: 'Number of Servers'}},
            barmode: 'group'
        }};
        Plotly.newPlot('servers-chart', serversData, serversLayout);

        // Fitness Comparison
        var fitnessData = [
            {{
                x: {scenarios},
                y: {ga_fitness},
                name: 'GA',
                type: 'bar',
                marker: {{color: '#3498db'}}
            }},
            {{
                x: {scenarios},
                y: {woc_fitness},
                name: 'WOC',
                type: 'bar',
                marker: {{color: '#27ae60'}}
            }}
        ];
        var fitnessLayout = {{
            title: 'Fitness Scores (Lower is Better)',
            xaxis: {{title: 'Scenario'}},
            yaxis: {{title: 'Fitness Score'}},
            barmode: 'group'
        }};
        Plotly.newPlot('fitness-chart', fitnessData, fitnessLayout);

        // Speedup Chart
        var speedupData = [
            {{
                x: {scenarios},
                y: {speedups},
                type: 'bar',
                marker: {{
                    color: {speedups},
                    colorscale: 'Greens',
                    showscale: true
                }},
                text: {[f"{s}×" for s in speedups]},
                textposition: 'auto'
            }}
        ];
        var speedupLayout = {{
            title: 'WOC Speedup Factor',
            xaxis: {{title: 'Scenario'}},
            yaxis: {{title: 'Speedup (×)'}},
        }};
        Plotly.newPlot('speedup-chart', speedupData, speedupLayout);
    </script>
</body>
</html>
"""

    return html


def main():
    """Update all visualizations."""

    print("="*70)
    print("UPDATING VISUALIZATIONS WITH NEW RESULTS")
    print("="*70)

    # Load results
    print("\nLoading benchmark results...")
    results = load_results()

    print(f"Loaded results for {len(results)} scenarios")

    # Update performance comparison
    print("\n1. Updating performance comparison visualization...")
    performance_html = update_performance_comparison(results)

    output_file = 'presentation_visuals/vis_14_performance_comparison.html'
    with open(output_file, 'w') as f:
        f.write(performance_html)

    print(f"   ✓ Updated: {output_file}")

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY OF UPDATES")
    print("="*70)
    print("\nUpdated files:")
    print("  ✓ presentation_visuals/vis_14_performance_comparison.html")
    print("\nKey changes:")
    print("  • Fitness values use new 10× multiplier (not 100×)")
    print("  • Results from simplified GA with random initialization")
    print("  • Shows dramatic improvement over generations")
    print("  • WoC speedups range from 8-80×")

    print("\n" + "="*70)
    print("Next steps:")
    print("="*70)
    print("1. Open the updated HTML file in your browser to view")
    print("2. Take screenshots for your presentation")
    print("3. Compare with old results to show the improvement")

    print("\n✅ Visualizations updated successfully!")


if __name__ == "__main__":
    main()
