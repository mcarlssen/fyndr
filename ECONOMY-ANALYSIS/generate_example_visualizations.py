#!/usr/bin/env python3
"""
Generate Example Visualizations from Existing Results

This script creates example visualizations using the existing OKR V2 results
to demonstrate the different graph types and their effectiveness.
"""

import json
import sys
import os
from visualization_engine import FYNDRVisualizationEngine

def load_existing_results():
    """Load existing results from the JSON file"""
    try:
        with open('okr_v2_optimized_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: okr_v2_optimized_results.json not found!")
        print("Please run the OKR V2 analyzer first to generate results.")
        return None

def create_example_data():
    """Create example data for demonstration if no real data exists"""
    return {
        'whale_result': {
            'player_type': 'whale',
            'config': {
                'owner_base_points': 2.0,
                'scanner_base_points': 1.0,
                'pack_price_dollars': 1.0,
                'geo_diversity_bonus': 1.0,
                'social_sneeze_bonus': 3.0,
                'churn_probability_whale': 0.0005,
                'churn_probability_grinder': 0.0008,
                'churn_probability_casual': 0.002
            },
            'summary': {
                'total_revenue': 1913.45,
                'total_players': 338,
                'whale_purchases': 317,
                'grinder_purchases': 848,
                'casual_purchases': 1552
            },
            'target_score': 620.16,
            'overall_score': 917.65,
            'revenue': 1913.45,
            'userbase': 338
        },
        'grinder_result': {
            'player_type': 'grinder',
            'config': {
                'owner_base_points': 2.0,
                'scanner_base_points': 1.0,
                'pack_price_dollars': 3.0,
                'geo_diversity_bonus': 2.5,
                'social_sneeze_bonus': 3.0,
                'churn_probability_whale': 0.0005,
                'churn_probability_grinder': 0.0008,
                'churn_probability_casual': 0.002
            },
            'summary': {
                'total_revenue': 3398.80,
                'total_players': 326,
                'whale_purchases': 380,
                'grinder_purchases': 869,
                'casual_purchases': 1744
            },
            'target_score': 2635.57,
            'overall_score': 1172.69,
            'revenue': 3398.80,
            'userbase': 326
        },
        'casual_result': {
            'player_type': 'casual',
            'config': {
                'owner_base_points': 2.0,
                'scanner_base_points': 1.0,
                'pack_price_dollars': 3.0,
                'geo_diversity_bonus': 1.0,
                'social_sneeze_bonus': 6.0,
                'churn_probability_whale': 0.0005,
                'churn_probability_grinder': 0.0008,
                'churn_probability_casual': 0.002
            },
            'summary': {
                'total_revenue': 2497.94,
                'total_players': 330,
                'whale_purchases': 269,
                'grinder_purchases': 909,
                'casual_purchases': 1580
            },
            'target_score': 186.16,
            'overall_score': 892.41,
            'revenue': 2497.94,
            'userbase': 330
        },
        'multiplayer_result': {
            'config': {
                'owner_base_points': 2.0,
                'scanner_base_points': 1.0,
                'pack_price_dollars': 3.0,
                'geo_diversity_bonus': 2.5,
                'social_sneeze_bonus': 6.0,
                'churn_probability_whale': 0.0005,
                'churn_probability_grinder': 0.0008,
                'churn_probability_casual': 0.002
            },
            'summary': {
                'total_revenue': 3016.04,
                'total_players': 344,
                'whale_purchases': 320,
                'grinder_purchases': 875,
                'casual_purchases': 1879
            },
            'whale_score': 494.23,
            'grinder_score': 2531.00,
            'casual_score': 167.99,
            'overall_score': 1125.54,
            'revenue': 3016.04,
            'userbase': 344
        }
    }

def main():
    """Main function to generate example visualizations"""
    print("FYNDR Economy Visualization Generator")
    print("=" * 50)
    
    # Load existing results or create example data
    results = load_existing_results()
    if results is None:
        print("Creating example data for demonstration...")
        results = create_example_data()
    
    # Create visualization engine
    viz_engine = FYNDRVisualizationEngine()
    
    print("Generating example visualizations...")
    
    try:
        # Generate all visualizations
        viz_files = viz_engine.generate_all_visualizations(results)
        
        print("\n" + "=" * 50)
        print("VISUALIZATION GENERATION COMPLETE")
        print("=" * 50)
        print("Generated files:")
        
        for viz_type, filepath in viz_files.items():
            print(f"  ✓ {viz_type}: {filepath}")
        
        print(f"\nAll visualizations saved in: {viz_engine.output_dir}/")
        print("\nVisualization Types Generated:")
        print("  1. Comprehensive Dashboard - Overview of all results")
        print("  2. Parameter Correlation Heatmaps - Shows parameter relationships")
        print("  3. Scatter Plots - Parameter values vs scores")
        print("  4. Distribution Plots - Parameter value distributions")
        print("  5. Multi-Player Analysis - Cross-player type comparisons")
        
        print("\nTo view the visualizations:")
        print("  - Open the SVG files in any modern web browser")
        print("  - Or use a vector graphics editor like Inkscape")
        print("  - SVG format allows for high-quality scaling")
        
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
