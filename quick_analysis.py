#!/usr/bin/env python3
"""
Quick FYNDR Parameter Analysis

This script runs shorter simulations to quickly find optimal parameter ranges.
"""

import sys
import os
import json
from fyndr_simulator import FYNDRSimulator, GameConfig

def run_quick_test(config_name, config_params, days=90):
    """Run a quick test with given configuration"""
    try:
        config = GameConfig(**config_params)
        simulator = FYNDRSimulator(config)
        simulator.run_simulation(days)
        summary = simulator.get_economy_summary()
        
        # Calculate scores
        total_players = summary.get('total_players', 0)
        total_revenue = summary.get('total_revenue', 0)
        avg_points_per_player = summary.get('avg_points_per_player', 0)
        avg_scans_per_player = summary.get('avg_scans_per_player', 0)
        
        growth_score = total_players * 0.7 + (total_revenue / 100) * 0.3
        retention_score = avg_points_per_player * 0.6 + avg_scans_per_player * 0.4
        overall_score = growth_score * 0.6 + retention_score * 0.4
        
        return {
            'name': config_name,
            'players': total_players,
            'revenue': total_revenue,
            'avg_points': avg_points_per_player,
            'avg_scans': avg_scans_per_player,
            'growth_score': growth_score,
            'retention_score': retention_score,
            'overall_score': overall_score
        }
    except Exception as e:
        print(f"Error in {config_name}: {e}")
        return None

def main():
    """Run quick analysis"""
    print("Quick FYNDR Parameter Analysis")
    print("=" * 40)
    
    # Test configurations
    tests = [
        ("Base Config", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("Low Price", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 2.5,
            'pack_price_points': 250,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("High Price", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.5,
            'pack_price_points': 350,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("Low Scoring", {
            'owner_base_points': 1.5,
            'scanner_base_points': 0.75,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("High Scoring", {
            'owner_base_points': 2.5,
            'scanner_base_points': 1.25,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("Low Caps", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 15,
            'weekly_earn_cap': 400,
        }),
        ("High Caps", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 25,
            'weekly_earn_cap': 600,
        }),
    ]
    
    results = []
    for test_name, config_params in tests:
        print(f"Testing {test_name}...")
        result = run_quick_test(test_name, config_params, 90)
        if result:
            results.append(result)
    
    # Sort by overall score
    results.sort(key=lambda x: x['overall_score'], reverse=True)
    
    print("\nResults:")
    print("-" * 40)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['name']}")
        print(f"   Score: {result['overall_score']:.2f}")
        print(f"   Players: {result['players']}")
        print(f"   Revenue: ${result['revenue']:.2f}")
        print(f"   Avg Points: {result['avg_points']:.1f}")
        print(f"   Avg Scans: {result['avg_scans']:.1f}")
        print()
    
    # Export results
    with open('quick_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Results exported to quick_analysis_results.json")

if __name__ == "__main__":
    main()