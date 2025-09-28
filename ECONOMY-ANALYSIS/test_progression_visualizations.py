#!/usr/bin/env python3
"""
Test Progression Visualizations

This script creates example progression data to demonstrate the new
parameter and score progression visualizations.
"""

import json
import random
from visualization_engine import FYNDRVisualizationEngine

def create_example_progression_data():
    """Create example progression data for testing visualizations"""
    
    # Base parameter ranges (doubled as requested)
    base_config = {
        'owner_base_points': 2.0,
        'scanner_base_points': 1.0,
        'unique_scanner_bonus': 1.0,
        'diminishing_threshold': 3,
        'geo_diversity_radius': 500.0,
        'geo_diversity_bonus': 1.0,
        'venue_variety_bonus': 1.0,
        'social_sneeze_threshold': 3,
        'social_sneeze_bonus': 3.0,
        'social_sneeze_cap': 1,
        'points_per_level': 100,
        'max_level': 20,
        'pack_price_points': 300,
        'pack_price_dollars': 1.0,
        'points_per_dollar': 150.0,
        'wallet_topup_min': 5.0,
        'wallet_topup_max': 50.0,
        'weekly_earn_cap': 500,
        'daily_passive_cap': 100,
        'sticker_scan_cooldown_hours': 11,
        'churn_probability_base': 0.001,
        'churn_probability_whale': 0.0005,
        'churn_probability_grinder': 0.0008,
        'churn_probability_casual': 0.002,
        'streak_bonus_days': 7,
        'streak_bonus_multiplier': 1.5,
        'comeback_bonus_days': 3,
        'comeback_bonus_multiplier': 2.0,
        'new_player_bonus_days': 7,
        'new_player_bonus_multiplier': 2.0,
        'new_player_free_packs': 1,
        'event_frequency_days': 30,
        'event_duration_days': 7,
        'event_bonus_multiplier': 1.5
    }
    
    # Create 16 test configurations for each player type
    all_results = []
    
    for player_type in ['whale', 'grinder', 'casual']:
        player_results = []
        
        for test_num in range(16):
            config = base_config.copy()
            
            # Vary key parameters based on player type
            if player_type == 'whale':
                # Whale-focused variations
                config['owner_base_points'] = 1.0 + (test_num * 0.5)  # 1.0 to 8.5
                config['pack_price_dollars'] = 0.5 + (test_num * 1.0)  # 0.5 to 15.5
                config['points_per_dollar'] = 200.0 - (test_num * 10.0)  # 200 to 50
                config['churn_probability_whale'] = 0.0001 + (test_num * 0.005)  # 0.0001 to 0.075
                config['geo_diversity_bonus'] = 1.0 + (test_num * 0.2)  # 1.0 to 4.0
                config['social_sneeze_bonus'] = 3.0 + (test_num * 0.3)  # 3.0 to 7.5
                
            elif player_type == 'grinder':
                # Grinder-focused variations
                config['owner_base_points'] = 1.5 + (test_num * 0.3)  # 1.5 to 6.0
                config['pack_price_dollars'] = 1.0 + (test_num * 0.8)  # 1.0 to 13.0
                config['geo_diversity_bonus'] = 1.0 + (test_num * 0.4)  # 1.0 to 7.0
                config['venue_variety_bonus'] = 1.0 + (test_num * 0.4)  # 1.0 to 7.0
                config['churn_probability_grinder'] = 0.0001 + (test_num * 0.004)  # 0.0001 to 0.06
                config['weekly_earn_cap'] = 500 + (test_num * 50)  # 500 to 1250
                
            else:  # casual
                # Casual-focused variations
                config['owner_base_points'] = 1.0 + (test_num * 0.4)  # 1.0 to 7.0
                config['pack_price_dollars'] = 1.0 + (test_num * 0.6)  # 1.0 to 10.0
                config['social_sneeze_bonus'] = 3.0 + (test_num * 0.5)  # 3.0 to 10.5
                config['social_sneeze_cap'] = 1 + (test_num // 4)  # 1 to 4
                config['churn_probability_casual'] = 0.0001 + (test_num * 0.003)  # 0.0001 to 0.045
                config['new_player_bonus_multiplier'] = 2.0 + (test_num * 0.2)  # 2.0 to 5.0
            
            # Generate realistic scores based on parameter values
            if player_type == 'whale':
                whale_score = 400 + (config['owner_base_points'] * 20) - (config['churn_probability_whale'] * 10000)
                grinder_score = 200 + (config['geo_diversity_bonus'] * 30)
                casual_score = 100 + (config['social_sneeze_bonus'] * 20)
            elif player_type == 'grinder':
                whale_score = 300 + (config['owner_base_points'] * 15)
                grinder_score = 500 + (config['geo_diversity_bonus'] * 50) + (config['venue_variety_bonus'] * 40)
                casual_score = 150 + (config['social_sneeze_bonus'] * 15)
            else:  # casual
                whale_score = 250 + (config['owner_base_points'] * 10)
                grinder_score = 300 + (config['geo_diversity_bonus'] * 25)
                casual_score = 200 + (config['social_sneeze_bonus'] * 30) + (config['new_player_bonus_multiplier'] * 20)
            
            overall_score = (whale_score + grinder_score + casual_score) / 3
            
            # Generate realistic revenue and userbase
            revenue = 1000 + (overall_score * 2) + random.uniform(-200, 200)
            userbase = 300 + (overall_score * 0.5) + random.uniform(-50, 50)
            
            result = {
                'config': config,
                'summary': {
                    'total_revenue': revenue,
                    'total_players': int(userbase),
                    f'{player_type}_purchases': int(100 + (overall_score * 0.3))
                },
                'whale_score': whale_score,
                'grinder_score': grinder_score,
                'casual_score': casual_score,
                'overall_score': overall_score,
                'revenue': revenue,
                'userbase': int(userbase),
                'player_type_focus': player_type
            }
            
            player_results.append(result)
            all_results.append(result)
    
    return all_results

def main():
    """Main function to test progression visualizations"""
    print("Testing Progression Visualizations")
    print("=" * 50)
    
    # Create example data
    print("Creating example progression data...")
    all_results = create_example_progression_data()
    
    # Create visualization engine
    viz_engine = FYNDRVisualizationEngine()
    
    print("Generating progression visualizations...")
    
    try:
        # Create test data structure
        test_data = {
            'all_simulation_results': all_results
        }
        
        # Generate visualizations
        viz_files = viz_engine.generate_all_visualizations(test_data)
        
        print("\n" + "=" * 50)
        print("PROGRESSION VISUALIZATION TEST COMPLETE")
        print("=" * 50)
        print("Generated files:")
        
        for viz_type, filepath in viz_files.items():
            print(f"  ✓ {viz_type}: {filepath}")
        
        print(f"\nAll visualizations saved in: {viz_engine.output_dir}/")
        print("\nNew Visualization Types:")
        print("  1. Parameter Progression - Shows how each parameter changes across 16 test configurations")
        print("  2. Score Progression - Shows how scores change across test configurations")
        print("  3. Parameter vs Score correlations - Shows relationships between parameters and outcomes")
        
        print("\nKey Features:")
        print("  - X-axis: Test Configuration (1-16)")
        print("  - Y-axis: Parameter values or scores")
        print("  - Each parameter gets its own subplot")
        print("  - Value labels on each data point")
        print("  - Grid lines for easy reading")
        
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
