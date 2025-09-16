#!/usr/bin/env python3
"""
FYNDR Simulator Configuration Manager

Provides easy-to-use interfaces for configuring and testing different game economy scenarios.
"""

import json
import yaml
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from fyndr_simulator import GameConfig, FYNDRSimulator

@dataclass
class ScenarioConfig:
    """Configuration for a specific scenario"""
    name: str
    description: str
    game_config: GameConfig
    initial_players: Dict[str, int]
    simulation_days: int = 30
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class ConfigManager:
    """Manages different simulation scenarios and configurations"""
    
    def __init__(self):
        self.scenarios: Dict[str, ScenarioConfig] = {}
        self.load_default_scenarios()
    
    def load_default_scenarios(self):
        """Load default scenario configurations"""
        
        # Baseline scenario
        baseline_config = GameConfig()
        self.scenarios['baseline'] = ScenarioConfig(
            name="Baseline Economy",
            description="Standard game economy with balanced whale/grinder/casual distribution",
            game_config=baseline_config,
            initial_players={'whale': 10, 'grinder': 50, 'casual': 100},
            simulation_days=30,
            tags=['baseline', 'balanced']
        )
        
        # Whale-heavy scenario
        whale_config = GameConfig()
        whale_config.pack_price_dollars = 2.5  # Lower price to encourage more purchases
        whale_config.owner_base_points = 2.5   # Higher owner rewards
        self.scenarios['whale_heavy'] = ScenarioConfig(
            name="Whale-Heavy Economy",
            description="Economy optimized for high-spending players",
            game_config=whale_config,
            initial_players={'whale': 25, 'grinder': 30, 'casual': 50},
            simulation_days=30,
            tags=['whale', 'monetization']
        )
        
        # Grinder-friendly scenario
        grinder_config = GameConfig()
        grinder_config.pack_price_points = 250  # Lower point cost
        grinder_config.scanner_base_points = 1.5  # Higher scanner rewards
        grinder_config.daily_scan_cap = 30  # Higher daily cap
        self.scenarios['grinder_friendly'] = ScenarioConfig(
            name="Grinder-Friendly Economy",
            description="Economy that rewards active scanning and grinding",
            game_config=grinder_config,
            initial_players={'whale': 5, 'grinder': 80, 'casual': 50},
            simulation_days=30,
            tags=['grinder', 'f2p']
        )
        
        # High-engagement scenario
        engagement_config = GameConfig()
        engagement_config.social_sneeze_bonus = 5.0  # Higher social rewards
        engagement_config.geo_diversity_bonus = 2.0  # Higher diversity rewards
        engagement_config.venue_variety_bonus = 2.0
        self.scenarios['high_engagement'] = ScenarioConfig(
            name="High-Engagement Economy",
            description="Economy that heavily rewards social and exploration behaviors",
            game_config=engagement_config,
            initial_players={'whale': 15, 'grinder': 60, 'casual': 75},
            simulation_days=30,
            tags=['engagement', 'social']
        )
        
        # Premium pricing scenario
        premium_config = GameConfig()
        premium_config.pack_price_dollars = 5.0  # Higher price
        premium_config.pack_price_points = 500   # Higher point cost
        premium_config.level_multipliers = [1.0, 1.1, 1.2, 1.3, 1.4]  # Higher multipliers
        self.scenarios['premium_pricing'] = ScenarioConfig(
            name="Premium Pricing Economy",
            description="Higher-priced economy with premium features",
            game_config=premium_config,
            initial_players={'whale': 20, 'grinder': 40, 'casual': 60},
            simulation_days=30,
            tags=['premium', 'pricing']
        )
        
        # Long-term scenario
        longterm_config = GameConfig()
        self.scenarios['long_term'] = ScenarioConfig(
            name="Long-Term Economy",
            description="Extended simulation to test economy stability",
            game_config=longterm_config,
            initial_players={'whale': 15, 'grinder': 60, 'casual': 100},
            simulation_days=90,
            tags=['longterm', 'stability']
        )
    
    def create_custom_scenario(self, name: str, description: str, 
                             config_dict: Dict[str, Any], 
                             initial_players: Dict[str, int],
                             simulation_days: int = 30,
                             tags: List[str] = None) -> str:
        """Create a custom scenario from a configuration dictionary"""
        if tags is None:
            tags = ['custom']
        
        # Create GameConfig from dictionary
        game_config = GameConfig(**config_dict)
        
        scenario = ScenarioConfig(
            name=name,
            description=description,
            game_config=game_config,
            initial_players=initial_players,
            simulation_days=simulation_days,
            tags=tags
        )
        
        self.scenarios[name.lower().replace(' ', '_')] = scenario
        return name.lower().replace(' ', '_')
    
    def get_scenario(self, name: str) -> ScenarioConfig:
        """Get a scenario by name"""
        return self.scenarios.get(name)
    
    def list_scenarios(self) -> List[str]:
        """List all available scenarios"""
        return list(self.scenarios.keys())
    
    def run_scenario(self, scenario_name: str) -> FYNDRSimulator:
        """Run a specific scenario and return the simulator"""
        scenario = self.get_scenario(scenario_name)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        print(f"Running scenario: {scenario.name}")
        print(f"Description: {scenario.description}")
        print(f"Tags: {', '.join(scenario.tags)}")
        print(f"Simulation days: {scenario.simulation_days}")
        print(f"Initial players: {scenario.initial_players}")
        print("-" * 50)
        
        simulator = FYNDRSimulator(scenario.game_config)
        simulator.run_simulation(scenario.simulation_days, scenario.initial_players)
        
        return simulator
    
    def compare_scenarios(self, scenario_names: List[str]) -> Dict[str, Any]:
        """Compare multiple scenarios and return comparison data"""
        results = {}
        
        for scenario_name in scenario_names:
            if scenario_name not in self.scenarios:
                print(f"Warning: Scenario '{scenario_name}' not found, skipping...")
                continue
            
            simulator = self.run_scenario(scenario_name)
            summary = simulator.get_economy_summary()
            results[scenario_name] = {
                'summary': summary,
                'scenario': self.scenarios[scenario_name]
            }
        
        return results
    
    def export_scenario_config(self, scenario_name: str, filename: str = None):
        """Export a scenario configuration to JSON"""
        scenario = self.get_scenario(scenario_name)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        if filename is None:
            filename = f"{scenario_name}_config.json"
        
        config_data = {
            'name': scenario.name,
            'description': scenario.description,
            'game_config': asdict(scenario.game_config),
            'initial_players': scenario.initial_players,
            'simulation_days': scenario.simulation_days,
            'tags': scenario.tags
        }
        
        with open(filename, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"Scenario configuration exported to {filename}")
    
    def import_scenario_config(self, filename: str) -> str:
        """Import a scenario configuration from JSON"""
        with open(filename, 'r') as f:
            config_data = json.load(f)
        
        scenario_name = config_data['name'].lower().replace(' ', '_')
        
        # Create GameConfig from imported data
        game_config = GameConfig(**config_data['game_config'])
        
        scenario = ScenarioConfig(
            name=config_data['name'],
            description=config_data['description'],
            game_config=game_config,
            initial_players=config_data['initial_players'],
            simulation_days=config_data.get('simulation_days', 30),
            tags=config_data.get('tags', ['imported'])
        )
        
        self.scenarios[scenario_name] = scenario
        return scenario_name

def main():
    """Main function for testing the configuration manager"""
    manager = ConfigManager()
    
    print("Available scenarios:")
    for name in manager.list_scenarios():
        scenario = manager.get_scenario(name)
        print(f"  {name}: {scenario.name}")
        print(f"    {scenario.description}")
        print(f"    Tags: {', '.join(scenario.tags)}")
        print()
    
    # Run a quick comparison
    print("Running comparison of baseline vs whale_heavy scenarios...")
    results = manager.compare_scenarios(['baseline', 'whale_heavy'])
    
    for scenario_name, data in results.items():
        summary = data['summary']
        print(f"\n{scenario_name.upper()} RESULTS:")
        print(f"  Total Revenue: ${summary['total_revenue']:.2f}")
        print(f"  Total Points: {summary['total_points']:,}")
        print(f"  Avg Revenue per Player: ${summary['avg_revenue_per_player']:.2f}")
        print(f"  Points per Scan: {summary['points_per_scan']:.2f}")

if __name__ == "__main__":
    main()
EOF