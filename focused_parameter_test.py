#!/usr/bin/env python3
"""
Focused Parameter Testing for FYNDR Economy

This script focuses on testing the most critical parameters identified from
the spec documents to find optimal ranges for growth, retention, and organic purchases.
"""

import random
import json
import csv
import numpy as np
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from advanced_economy_simulator import AdvancedFYNDRSimulator, AdvancedGameConfig
import statistics
from collections import defaultdict

@dataclass
class FocusedTestResult:
    """Results from a focused parameter test"""
    test_name: str
    config: Dict[str, Any]
    summary: Dict[str, Any]
    growth_score: float
    retention_score: float
    organic_purchase_score: float
    overall_score: float

class FocusedParameterTester:
    """Focused tester for critical parameters"""
    
    def __init__(self):
        self.results = []
    
    def create_base_config(self) -> AdvancedGameConfig:
        """Create a base configuration based on spec recommendations"""
        return AdvancedGameConfig(
            # Core scoring (from spec)
            owner_base_points=2.0,
            scanner_base_points=1.0,
            unique_scanner_bonus=1.0,
            
            # Diminishing returns (from spec)
            diminishing_threshold=3,
            diminishing_rates=[1.0, 0.5, 0.25],
            
            # Diversity bonuses (from spec)
            geo_diversity_radius=500.0,
            geo_diversity_bonus=1.0,
            venue_variety_bonus=1.0,
            
            # Social mechanics (from spec)
            social_sneeze_threshold=3,
            social_sneeze_bonus=3.0,
            social_sneeze_cap=1,
            
            # Progression (from spec)
            level_multipliers=[1.0, 1.05, 1.10, 1.15, 1.20],
            points_per_level=100,
            max_level=20,
            
            # Economy (from spec)
            pack_price_points=300,
            pack_price_dollars=3.0,
            points_per_dollar=100.0,
            
            # Player behavior caps (from spec)
            daily_scan_cap=20,
            weekly_earn_cap=500,
            daily_passive_cap=100,
            
            # Retention mechanics (optimized)
            churn_probability_base=0.001,
            churn_probability_whale=0.0005,
            churn_probability_grinder=0.0008,
            churn_probability_casual=0.002,
            
            # Engagement bonuses (optimized)
            streak_bonus_days=7,
            streak_bonus_multiplier=1.5,
            comeback_bonus_days=3,
            comeback_bonus_multiplier=2.0,
            
            # Sticker decay (optimized)
            sticker_decay_rate=0.1,
            sticker_min_value=0.1,
            
            # New player onboarding (optimized)
            new_player_bonus_days=7,
            new_player_bonus_multiplier=2.0,
            new_player_free_packs=1,
            
            # Seasonal events (optimized)
            event_frequency_days=30,
            event_duration_days=7,
            event_bonus_multiplier=1.5,
        )
    
    def test_pack_pricing(self) -> List[FocusedTestResult]:
        """Test different pack pricing strategies"""
        print("Testing Pack Pricing Strategies...")
        results = []
        
        # Test different pack prices and point costs
        pack_tests = [
            {"pack_price_dollars": 2.0, "pack_price_points": 200, "name": "Low Price, Low Points"},
            {"pack_price_dollars": 2.5, "pack_price_points": 250, "name": "Low Price, Med Points"},
            {"pack_price_dollars": 3.0, "pack_price_points": 300, "name": "Base Price, Base Points"},
            {"pack_price_dollars": 3.0, "pack_price_points": 250, "name": "Base Price, Low Points"},
            {"pack_price_dollars": 3.0, "pack_price_points": 350, "name": "Base Price, High Points"},
            {"pack_price_dollars": 3.5, "pack_price_points": 300, "name": "High Price, Base Points"},
            {"pack_price_dollars": 4.0, "pack_price_points": 400, "name": "High Price, High Points"},
        ]
        
        for test_config in pack_tests:
            config = self.create_base_config()
            for key, value in test_config.items():
                if key != "name":
                    setattr(config, key, value)
            
            result = self._run_single_test(f"Pack Pricing: {test_config['name']}", config)
            results.append(result)
        
        return results
    
    def test_scoring_mechanics(self) -> List[FocusedTestResult]:
        """Test different scoring mechanics"""
        print("Testing Scoring Mechanics...")
        results = []
        
        scoring_tests = [
            {"owner_base_points": 1.5, "scanner_base_points": 0.75, "name": "Low Base Scoring"},
            {"owner_base_points": 2.0, "scanner_base_points": 1.0, "name": "Base Scoring"},
            {"owner_base_points": 2.5, "scanner_base_points": 1.25, "name": "High Base Scoring"},
            {"owner_base_points": 3.0, "scanner_base_points": 1.5, "name": "Very High Base Scoring"},
            {"owner_base_points": 2.0, "scanner_base_points": 1.0, "unique_scanner_bonus": 0.5, "name": "Low Unique Bonus"},
            {"owner_base_points": 2.0, "scanner_base_points": 1.0, "unique_scanner_bonus": 1.5, "name": "High Unique Bonus"},
            {"owner_base_points": 2.0, "scanner_base_points": 1.0, "unique_scanner_bonus": 2.0, "name": "Very High Unique Bonus"},
        ]
        
        for test_config in scoring_tests:
            config = self.create_base_config()
            for key, value in test_config.items():
                if key != "name":
                    setattr(config, key, value)
            
            result = self._run_single_test(f"Scoring: {test_config['name']}", config)
            results.append(result)
        
        return results
    
    def test_diversity_bonuses(self) -> List[FocusedTestResult]:
        """Test different diversity bonus configurations"""
        print("Testing Diversity Bonuses...")
        results = []
        
        diversity_tests = [
            {"geo_diversity_bonus": 0.5, "venue_variety_bonus": 0.5, "name": "Low Diversity Bonuses"},
            {"geo_diversity_bonus": 1.0, "venue_variety_bonus": 1.0, "name": "Base Diversity Bonuses"},
            {"geo_diversity_bonus": 1.5, "venue_variety_bonus": 1.5, "name": "High Diversity Bonuses"},
            {"geo_diversity_bonus": 2.0, "venue_variety_bonus": 2.0, "name": "Very High Diversity Bonuses"},
            {"geo_diversity_radius": 300.0, "name": "Small Geo Radius"},
            {"geo_diversity_radius": 500.0, "name": "Base Geo Radius"},
            {"geo_diversity_radius": 750.0, "name": "Large Geo Radius"},
            {"geo_diversity_radius": 1000.0, "name": "Very Large Geo Radius"},
        ]
        
        for test_config in diversity_tests:
            config = self.create_base_config()
            for key, value in test_config.items():
                if key != "name":
                    setattr(config, key, value)
            
            result = self._run_single_test(f"Diversity: {test_config['name']}", config)
            results.append(result)
        
        return results
    
    def test_retention_mechanics(self) -> List[FocusedTestResult]:
        """Test different retention mechanics"""
        print("Testing Retention Mechanics...")
        results = []
        
        retention_tests = [
            {"churn_probability_base": 0.0005, "churn_probability_casual": 0.001, "name": "Low Churn"},
            {"churn_probability_base": 0.001, "churn_probability_casual": 0.002, "name": "Base Churn"},
            {"churn_probability_base": 0.002, "churn_probability_casual": 0.004, "name": "High Churn"},
            {"streak_bonus_multiplier": 1.2, "name": "Low Streak Bonus"},
            {"streak_bonus_multiplier": 1.5, "name": "Base Streak Bonus"},
            {"streak_bonus_multiplier": 2.0, "name": "High Streak Bonus"},
            {"comeback_bonus_multiplier": 1.5, "name": "Low Comeback Bonus"},
            {"comeback_bonus_multiplier": 2.0, "name": "Base Comeback Bonus"},
            {"comeback_bonus_multiplier": 3.0, "name": "High Comeback Bonus"},
        ]
        
        for test_config in retention_tests:
            config = self.create_base_config()
            for key, value in test_config.items():
                if key != "name":
                    setattr(config, key, value)
            
            result = self._run_single_test(f"Retention: {test_config['name']}", config)
            results.append(result)
        
        return results
    
    def test_engagement_mechanics(self) -> List[FocusedTestResult]:
        """Test different engagement mechanics"""
        print("Testing Engagement Mechanics...")
        results = []
        
        engagement_tests = [
            {"daily_scan_cap": 10, "name": "Low Scan Cap"},
            {"daily_scan_cap": 20, "name": "Base Scan Cap"},
            {"daily_scan_cap": 30, "name": "High Scan Cap"},
            {"weekly_earn_cap": 300, "name": "Low Weekly Cap"},
            {"weekly_earn_cap": 500, "name": "Base Weekly Cap"},
            {"weekly_earn_cap": 800, "name": "High Weekly Cap"},
            {"new_player_bonus_multiplier": 1.5, "name": "Low New Player Bonus"},
            {"new_player_bonus_multiplier": 2.0, "name": "Base New Player Bonus"},
            {"new_player_bonus_multiplier": 3.0, "name": "High New Player Bonus"},
            {"event_bonus_multiplier": 1.2, "name": "Low Event Bonus"},
            {"event_bonus_multiplier": 1.5, "name": "Base Event Bonus"},
            {"event_bonus_multiplier": 2.0, "name": "High Event Bonus"},
        ]
        
        for test_config in engagement_tests:
            config = self.create_base_config()
            for key, value in test_config.items():
                if key != "name":
                    setattr(config, key, value)
            
            result = self._run_single_test(f"Engagement: {test_config['name']}", config)
            results.append(result)
        
        return results
    
    def test_sticker_decay(self) -> List[FocusedTestResult]:
        """Test different sticker decay mechanics"""
        print("Testing Sticker Decay Mechanics...")
        results = []
        
        decay_tests = [
            {"sticker_decay_rate": 0.05, "sticker_min_value": 0.2, "name": "Slow Decay, High Min"},
            {"sticker_decay_rate": 0.1, "sticker_min_value": 0.1, "name": "Base Decay, Base Min"},
            {"sticker_decay_rate": 0.15, "sticker_min_value": 0.05, "name": "Fast Decay, Low Min"},
            {"sticker_decay_rate": 0.2, "sticker_min_value": 0.05, "name": "Very Fast Decay, Low Min"},
        ]
        
        for test_config in decay_tests:
            config = self.create_base_config()
            for key, value in test_config.items():
                if key != "name":
                    setattr(config, key, value)
            
            result = self._run_single_test(f"Decay: {test_config['name']}", config)
            results.append(result)
        
        return results
    
    def _run_single_test(self, test_name: str, config: AdvancedGameConfig) -> FocusedTestResult:
        """Run a single test with given configuration"""
        try:
            simulator = AdvancedFYNDRSimulator(config)
            simulator.run_simulation(270)  # 270 days
            summary = simulator.get_economy_summary()
            
            # Calculate scores
            growth_score = self._calculate_growth_score(summary)
            retention_score = self._calculate_retention_score(summary)
            organic_purchase_score = self._calculate_organic_purchase_score(summary)
            overall_score = self._calculate_overall_score(growth_score, retention_score, organic_purchase_score)
            
            return FocusedTestResult(
                test_name=test_name,
                config=config.__dict__,
                summary=summary,
                growth_score=growth_score,
                retention_score=retention_score,
                organic_purchase_score=organic_purchase_score,
                overall_score=overall_score
            )
        except Exception as e:
            print(f"Error in test {test_name}: {e}")
            return None
    
    def _calculate_growth_score(self, summary: Dict[str, Any]) -> float:
        """Calculate growth score"""
        total_players = summary.get('total_players', 0)
        total_players_ever = summary.get('total_players_ever', 1)
        retention_rate = summary.get('retention_rate', 0)
        
        growth_score = (total_players * 0.7) + (retention_rate * 1000 * 0.3)
        return growth_score
    
    def _calculate_retention_score(self, summary: Dict[str, Any]) -> float:
        """Calculate retention score"""
        retention_rate = summary.get('retention_rate', 0)
        avg_consecutive_days = summary.get('avg_consecutive_days', 0)
        
        retention_score = (retention_rate * 1000) + (avg_consecutive_days * 10)
        return retention_score
    
    def _calculate_organic_purchase_score(self, summary: Dict[str, Any]) -> float:
        """Calculate organic purchase score"""
        organic_purchases = summary.get('organic_purchases', 0)
        grinder_purchases = summary.get('grinder_purchases', 0)
        casual_purchases = summary.get('casual_purchases', 0)
        total_players = summary.get('total_players', 1)
        
        organic_rate = organic_purchases / total_players
        grinder_rate = grinder_purchases / total_players
        casual_rate = casual_purchases / total_players
        
        organic_score = (organic_rate * 100) + (grinder_rate * 50) + (casual_rate * 25)
        return organic_score
    
    def _calculate_overall_score(self, growth_score: float, retention_score: float, organic_purchase_score: float) -> float:
        """Calculate overall score"""
        return (growth_score * 0.4) + (retention_score * 0.3) + (organic_purchase_score * 0.3)
    
    def run_all_tests(self) -> List[FocusedTestResult]:
        """Run all focused tests"""
        print("Running Focused Parameter Tests for FYNDR Economy")
        print("=" * 60)
        
        all_results = []
        
        # Run all test categories
        test_categories = [
            self.test_pack_pricing,
            self.test_scoring_mechanics,
            self.test_diversity_bonuses,
            self.test_retention_mechanics,
            self.test_engagement_mechanics,
            self.test_sticker_decay,
        ]
        
        for test_func in test_categories:
            results = test_func()
            all_results.extend([r for r in results if r is not None])
            print(f"Completed {test_func.__name__}: {len([r for r in results if r is not None])} tests")
        
        # Sort by overall score
        all_results.sort(key=lambda x: x.overall_score, reverse=True)
        self.results = all_results
        
        print(f"\nCompleted all tests: {len(all_results)} total tests")
        return all_results
    
    def export_results(self, filename: str = "focused_test_results.json"):
        """Export results to JSON"""
        export_data = {
            'results': [
                {
                    'test_name': result.test_name,
                    'config': result.config,
                    'summary': result.summary,
                    'growth_score': result.growth_score,
                    'retention_score': result.retention_score,
                    'organic_purchase_score': result.organic_purchase_score,
                    'overall_score': result.overall_score
                }
                for result in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Results exported to {filename}")
    
    def export_csv(self, filename: str = "focused_test_results.csv"):
        """Export results to CSV"""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['test_name', 'overall_score', 'growth_score', 'retention_score', 'organic_purchase_score']
            header.extend(['total_players', 'retention_rate', 'organic_purchases', 'total_revenue'])
            writer.writerow(header)
            
            # Write data
            for result in self.results:
                row = [
                    result.test_name,
                    result.overall_score,
                    result.growth_score,
                    result.retention_score,
                    result.organic_purchase_score,
                    result.summary.get('total_players', 0),
                    result.summary.get('retention_rate', 0),
                    result.summary.get('organic_purchases', 0),
                    result.summary.get('total_revenue', 0)
                ]
                writer.writerow(row)
        
        print(f"Results exported to {filename}")
    
    def print_summary(self):
        """Print summary of results"""
        if not self.results:
            print("No results to display")
            return
        
        print("\n" + "=" * 80)
        print("FOCUSED PARAMETER TEST RESULTS SUMMARY")
        print("=" * 80)
        
        # Top 10 results
        print("\nTop 10 Configurations by Overall Score:")
        print("-" * 80)
        for i, result in enumerate(self.results[:10], 1):
            print(f"\n{i}. {result.test_name}")
            print(f"   Overall Score: {result.overall_score:.2f}")
            print(f"   Growth: {result.growth_score:.2f}, Retention: {result.retention_score:.2f}, Organic: {result.organic_purchase_score:.2f}")
            print(f"   Total Players: {result.summary['total_players']}")
            print(f"   Retention Rate: {result.summary['retention_rate']:.3f}")
            print(f"   Organic Purchases: {result.summary['organic_purchases']}")
            print(f"   Total Revenue: ${result.summary['total_revenue']:.2f}")
        
        # Best results by category
        print("\n" + "=" * 80)
        print("BEST RESULTS BY CATEGORY")
        print("=" * 80)
        
        categories = {}
        for result in self.results:
            category = result.test_name.split(':')[0]
            if category not in categories:
                categories[category] = result
        
        for category, result in categories.items():
            print(f"\n{category}:")
            print(f"  Best: {result.test_name}")
            print(f"  Score: {result.overall_score:.2f}")
            print(f"  Players: {result.summary['total_players']}")
            print(f"  Retention: {result.summary['retention_rate']:.3f}")
            print(f"  Organic Purchases: {result.summary['organic_purchases']}")

def main():
    """Main function to run focused parameter tests"""
    tester = FocusedParameterTester()
    results = tester.run_all_tests()
    tester.print_summary()
    tester.export_results()
    tester.export_csv()

if __name__ == "__main__":
    main()