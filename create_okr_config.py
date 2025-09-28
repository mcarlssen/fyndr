#!/usr/bin/env python3
"""
Create OKR-optimized configuration for FYNDR Life Simulator
"""

import json
from fyndr_life_simulator import load_config_from_okr_results, LifeSimConfig

def main():
    # Load configuration from OKR results
    config = load_config_from_okr_results('ECONOMY-ANALYSIS/okr_v2_optimized_results.json')
    
    # Save the configuration
    with open('fyndr_okr_optimized_config.json', 'w') as f:
        json.dump(config.__dict__, f, indent=2)
    
    print("OKR-optimized configuration saved to fyndr_okr_optimized_config.json")
    print("\nKey parameters:")
    print(f"  Owner Base Points: {config.owner_base_points}")
    print(f"  Pack Price: ${config.pack_price_dollars}")
    print(f"  Geo Diversity Bonus: {config.geo_diversity_bonus}")
    print(f"  Social Sneeze Bonus: {config.social_sneeze_bonus}")
    print(f"  Whale Churn: {config.churn_probability_whale}")
    print(f"  Grinder Churn: {config.churn_probability_grinder}")
    print(f"  Casual Churn: {config.churn_probability_casual}")

if __name__ == "__main__":
    main()
