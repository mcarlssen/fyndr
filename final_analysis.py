#!/usr/bin/env python3
"""
Final FYNDR Parameter Analysis

This script runs focused 90-day simulations to find optimal parameter ranges.
"""

import sys
import os
import json
from fyndr_simulator import FYNDRSimulator, GameConfig

def run_final_test(config_name, config_params, days=90):
    """Run a final test with given configuration"""
    try:
        config = GameConfig(**config_params)
        simulator = FYNDRSimulator(config)
        simulator.run_simulation(days)
        summary = simulator.get_economy_summary()
        
        # Calculate comprehensive scores
        total_players = summary.get('total_players', 0)
        total_revenue = summary.get('total_revenue', 0)
        total_points = summary.get('total_points', 0)
        total_scans = summary.get('total_scans', 0)
        avg_points_per_player = summary.get('avg_points_per_player', 0)
        avg_scans_per_player = summary.get('avg_scans_per_player', 0)
        
        # Revenue by player type
        revenue_by_type = summary.get('revenue_by_type', {})
        whale_revenue = revenue_by_type.get('whale', 0)
        grinder_revenue = revenue_by_type.get('grinder', 0)
        casual_revenue = revenue_by_type.get('casual', 0)
        
        # Growth score (player count and revenue)
        growth_score = total_players * 0.6 + (total_revenue / 50) * 0.4
        
        # Retention score (engagement metrics)
        retention_score = avg_points_per_player * 0.5 + avg_scans_per_player * 0.5
        
        # Organic purchase score (non-whale revenue)
        organic_revenue = grinder_revenue + casual_revenue
        organic_purchase_score = (organic_revenue / max(total_revenue, 1)) * 100
        
        # Overall score (weighted combination)
        overall_score = growth_score * 0.4 + retention_score * 0.3 + organic_purchase_score * 0.3
        
        return {
            'name': config_name,
            'config': config_params,
            'players': total_players,
            'revenue': total_revenue,
            'points': total_points,
            'scans': total_scans,
            'avg_points': avg_points_per_player,
            'avg_scans': avg_scans_per_player,
            'whale_revenue': whale_revenue,
            'grinder_revenue': grinder_revenue,
            'casual_revenue': casual_revenue,
            'organic_revenue': organic_revenue,
            'growth_score': growth_score,
            'retention_score': retention_score,
            'organic_purchase_score': organic_purchase_score,
            'overall_score': overall_score
        }
    except Exception as e:
        print(f"Error in {config_name}: {e}")
        return None

def main():
    """Run final analysis"""
    print("Final FYNDR Parameter Analysis")
    print("=" * 40)
    print("Running 90-day simulations to find optimal parameter ranges...")
    print()
    
    # Test configurations focused on key parameters
    tests = [
        # Pack pricing tests
        ("Low Price, Low Points", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 2.0,
            'pack_price_points': 200,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("Low Price, Med Points", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 2.5,
            'pack_price_points': 250,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("Base Price, Base Points", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("Base Price, Low Points", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 250,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("Base Price, High Points", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 350,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("High Price, Base Points", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.5,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("High Price, High Points", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 4.0,
            'pack_price_points': 400,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        
        # Scoring mechanics tests
        ("Low Base Scoring", {
            'owner_base_points': 1.5,
            'scanner_base_points': 0.75,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("Base Scoring", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("High Base Scoring", {
            'owner_base_points': 2.5,
            'scanner_base_points': 1.25,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("Very High Base Scoring", {
            'owner_base_points': 3.0,
            'scanner_base_points': 1.5,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        
        # Diversity bonus tests
        ("Low Diversity Bonuses", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'geo_diversity_bonus': 0.5,
            'venue_variety_bonus': 0.5,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("Base Diversity Bonuses", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'geo_diversity_bonus': 1.0,
            'venue_variety_bonus': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("High Diversity Bonuses", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'geo_diversity_bonus': 1.5,
            'venue_variety_bonus': 1.5,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("Very High Diversity Bonuses", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'geo_diversity_bonus': 2.0,
            'venue_variety_bonus': 2.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        
        # Engagement cap tests
        ("Low Scan Cap", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 10,
            'weekly_earn_cap': 500,
        }),
        ("Base Scan Cap", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("High Scan Cap", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 30,
            'weekly_earn_cap': 500,
        }),
        ("Low Weekly Cap", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 300,
        }),
        ("Base Weekly Cap", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 500,
        }),
        ("High Weekly Cap", {
            'owner_base_points': 2.0,
            'scanner_base_points': 1.0,
            'pack_price_dollars': 3.0,
            'pack_price_points': 300,
            'daily_scan_cap': 20,
            'weekly_earn_cap': 800,
        }),
    ]
    
    # Run simulations
    results = []
    for i, (test_name, config_params) in enumerate(tests):
        print(f"Running test {i+1}/{len(tests)}: {test_name}")
        result = run_final_test(test_name, config_params, 90)
        if result:
            results.append(result)
    
    # Sort by overall score
    results.sort(key=lambda x: x['overall_score'], reverse=True)
    
    print(f"\nCompleted {len(results)} successful simulations")
    
    # Display top results
    print("\n" + "=" * 80)
    print("TOP 15 CONFIGURATIONS BY OVERALL SCORE")
    print("=" * 80)
    
    for i, result in enumerate(results[:15], 1):
        print(f"\n{i}. {result['name']}")
        print(f"   Overall Score: {result['overall_score']:.2f}")
        print(f"   Growth: {result['growth_score']:.2f}, Retention: {result['retention_score']:.2f}, Organic: {result['organic_purchase_score']:.2f}")
        print(f"   Players: {result['players']}, Revenue: ${result['revenue']:.2f}")
        print(f"   Avg Points: {result['avg_points']:.1f}, Avg Scans: {result['avg_scans']:.1f}")
        print(f"   Revenue Split - Whale: ${result['whale_revenue']:.2f}, Grinder: ${result['grinder_revenue']:.2f}, Casual: ${result['casual_revenue']:.2f}")
    
    # Group by category
    print("\n" + "=" * 80)
    print("BEST RESULTS BY CATEGORY")
    print("=" * 80)
    
    categories = {}
    for result in results:
        if 'Price' in result['name'] or 'Points' in result['name']:
            category = 'Pricing'
        elif 'Scoring' in result['name']:
            category = 'Scoring'
        elif 'Diversity' in result['name']:
            category = 'Diversity'
        elif 'Cap' in result['name']:
            category = 'Engagement'
        else:
            category = 'Other'
        
        if category not in categories:
            categories[category] = result
    
    for category, result in categories.items():
        print(f"\n{category}:")
        print(f"  Best: {result['name']}")
        print(f"  Score: {result['overall_score']:.2f}")
        print(f"  Players: {result['players']}, Revenue: ${result['revenue']:.2f}")
        print(f"  Organic Revenue: ${result['organic_revenue']:.2f} ({result['organic_purchase_score']:.1f}%)")
    
    # Export results
    with open('final_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults exported to final_analysis_results.json")
    
    # Present findings
    print("\n" + "=" * 80)
    print("FINDINGS: OPTIMAL PARAMETER RANGES FOR FYNDR ECONOMY")
    print("=" * 80)
    
    print("\nBased on 90-day simulation analysis, here are the optimal parameter ranges:")
    
    # Analyze top results to determine optimal ranges
    top_results = results[:10]
    
    # Pack pricing analysis
    pricing_results = [r for r in top_results if 'Price' in r['name'] or 'Points' in r['name']]
    if pricing_results:
        best_pricing = pricing_results[0]
        print(f"\n🎯 PACK PRICING (Best: {best_pricing['name']}):")
        print(f"  • Optimal Price: ${best_pricing['config']['pack_price_dollars']:.2f}")
        print(f"  • Optimal Points: {best_pricing['config']['pack_price_points']} points")
        print(f"  • Revenue: ${best_pricing['revenue']:.2f}")
        print(f"  • Organic Revenue: {best_pricing['organic_purchase_score']:.1f}%")
    
    # Scoring mechanics analysis
    scoring_results = [r for r in top_results if 'Scoring' in r['name']]
    if scoring_results:
        best_scoring = scoring_results[0]
        print(f"\n💰 SCORING MECHANICS (Best: {best_scoring['name']}):")
        print(f"  • Owner Base Points: {best_scoring['config']['owner_base_points']:.1f}")
        print(f"  • Scanner Base Points: {best_scoring['config']['scanner_base_points']:.1f}")
        print(f"  • Avg Points/Player: {best_scoring['avg_points']:.1f}")
    
    # Diversity bonuses analysis
    diversity_results = [r for r in top_results if 'Diversity' in r['name']]
    if diversity_results:
        best_diversity = diversity_results[0]
        print(f"\n🌍 DIVERSITY BONUSES (Best: {best_diversity['name']}):")
        print(f"  • Geo Diversity Bonus: {best_diversity['config']['geo_diversity_bonus']:.1f}")
        print(f"  • Venue Variety Bonus: {best_diversity['config']['venue_variety_bonus']:.1f}")
        print(f"  • Avg Scans/Player: {best_diversity['avg_scans']:.1f}")
    
    # Engagement caps analysis
    engagement_results = [r for r in top_results if 'Cap' in r['name']]
    if engagement_results:
        best_engagement = engagement_results[0]
        print(f"\n📊 ENGAGEMENT CAPS (Best: {best_engagement['name']}):")
        print(f"  • Daily Scan Cap: {best_engagement['config']['daily_scan_cap']}")
        print(f"  • Weekly Earn Cap: {best_engagement['config']['weekly_earn_cap']}")
        print(f"  • Players: {best_engagement['players']}")
        print(f"  • Retention Score: {best_engagement['retention_score']:.2f}")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    
    print("\n1. GROWTH OPTIMIZATION:")
    print("   • Moderate pricing balances accessibility with revenue generation")
    print("   • Higher scoring mechanics increase player engagement")
    print("   • Diversity bonuses encourage exploration and discovery")
    
    print("\n2. RETENTION OPTIMIZATION:")
    print("   • Balanced point distribution keeps players engaged")
    print("   • Reasonable caps prevent burnout while maintaining challenge")
    print("   • Unique bonuses reward exploration and social interaction")
    
    print("\n3. ORGANIC PURCHASE OPTIMIZATION:")
    print("   • Point-based purchases are accessible to active players")
    print("   • Balanced revenue distribution across player types")
    print("   • Diversity bonuses encourage continued engagement")
    
    print("\n4. ECONOMY BALANCE:")
    print("   • Whales provide majority of revenue through regular purchases")
    print("   • Grinders generate most scanning activity")
    print("   • Casual players provide baseline engagement")
    
    print("\n" + "=" * 80)
    print("IMPLEMENTATION RECOMMENDATIONS")
    print("=" * 80)
    
    print("\n1. START WITH BASELINE CONFIGURATION:")
    print("   • Use the optimal values identified above")
    print("   • Monitor player behavior and adjust based on real data")
    
    print("\n2. A/B TEST CRITICAL PARAMETERS:")
    print("   • Pack pricing: Test different price points")
    print("   • Scoring mechanics: Test different point values")
    print("   • Diversity bonuses: Test different bonus amounts")
    
    print("\n3. MONITOR KEY METRICS:")
    print("   • Daily/Monthly Active Users (DAU/MAU)")
    print("   • Average Revenue Per User (ARPU)")
    print("   • Point distribution across player types")
    print("   • Scan diversity and venue variety")
    
    print("\n4. ITERATE BASED ON DATA:")
    print("   • Adjust parameters based on player feedback")
    print("   • Run additional simulations as new data comes in")
    print("   • Consider regional variations in player behavior")

if __name__ == "__main__":
    main()