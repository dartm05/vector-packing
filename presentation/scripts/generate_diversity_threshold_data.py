#!/usr/bin/env python3
"""
Generate diversity threshold data showing immigration events.
"""

import json
import random

def generate_diversity_threshold_data():
    """Generate realistic diversity data with threshold-triggered immigration."""

    generations = []
    diversity_values = []
    immigration_events = []
    immigration_counts = []

    diversity = 1.5  # Start at moderate level
    threshold = 0.15
    population_size = 50

    for gen in range(1, 101):
        generations.append(gen)

        # Natural diversity decline (faster decay)
        if diversity > threshold:
            # Exponential decay - faster to trigger more events
            diversity *= 0.92
            immigration_events.append(None)
            immigration_counts.append(0)
        else:
            # Hit threshold - immigration occurs
            immigration_count = max(2, int(population_size * 0.1))
            immigration_events.append(gen)
            immigration_counts.append(immigration_count)

            # Immigration boosts diversity moderately
            diversity += random.uniform(0.4, 0.8)

            print(f"Gen {gen}: Diversity {diversity:.3f} < {threshold} → Injecting {immigration_count} immigrants")

        diversity_values.append(round(diversity, 3))

    # Filter out None values for immigration markers
    immigration_gen_markers = [g for g in immigration_events if g is not None]
    immigration_div_markers = [diversity_values[g-1] for g in immigration_gen_markers]
    immigration_count_markers = [c for c in immigration_counts if c > 0]

    return {
        'generations': generations,
        'diversity': diversity_values,
        'threshold': threshold,
        'immigration_events': {
            'generations': immigration_gen_markers,
            'diversity_at_event': immigration_div_markers,
            'immigrant_counts': immigration_count_markers
        },
        'population_size': population_size
    }

def main():
    print("="*80)
    print("GENERATING DIVERSITY THRESHOLD DATA")
    print("="*80)

    data = generate_diversity_threshold_data()

    output_file = 'diversity_threshold_data.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✓ Saved data to {output_file}")
    print(f"  Total generations: {len(data['generations'])}")
    print(f"  Immigration events: {len(data['immigration_events']['generations'])}")
    print(f"  Threshold: {data['threshold']}")
    print(f"  Population size: {data['population_size']}")

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
