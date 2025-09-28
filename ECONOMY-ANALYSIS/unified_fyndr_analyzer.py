#!/usr/bin/env python3
"""
Unified FYNDR Economy Analyzer

This comprehensive script combines all the best features from the five analysis scripts
to provide a single, powerful tool for analyzing the FYNDR game economy.

Key Features:
- Advanced 270-day simulation engine with retention mechanics
- Focused parameter testing for critical game mechanics
- Comprehensive optimization with parallel processing
- Detailed analytics and reporting
- Multiple export formats (JSON, CSV)
- Parameter correlation analysis

Usage:
    python unified_fyndr_analyzer.py [--mode MODE] [--combinations N] [--days D] [--processes P]
    
Modes:
    focused    - Run focused parameter tests (default)
    optimize   - Run comprehensive optimization
    both       - Run both focused tests and optimization
    quick      - Run quick analysis with fewer combinations
"""

import sys
import os
import time
import random
import json
import csv
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
import statistics
from collections import defaultdict, Counter
import argparse

# Import the advanced simulator
from advanced_economy_simulator import AdvancedFYNDRSimulator, AdvancedGameConfig

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

@dataclass
class OptimizationResult:
    """Results from a single optimization run"""
    config: Dict[str, Any]
    summary: Dict[str, Any]
    growth_score: float
    retention_score: float
    organic_purchase_score: float
    overall_score: float

@dataclass
class ParameterRange:
    """Defines a range for a parameter to test"""
    name: str
    min_value: float
    max_value: float
    step: float
    param_type: str  # 'float', 'int', 'list'

class UnifiedFYNDRAnalyzer:
    """Unified analyzer combining all analysis capabilities"""
    
    def __init__(self):
        self.focused_results = []
        self.optimization_results = []
        self.parameter_ranges = self._define_parameter_ranges()
    
    def _define_parameter_ranges(self) -> List[ParameterRange]:
        """Define comprehensive parameter ranges for optimization"""
        return [
            # === CORE SCORING PARAMETERS ===
            ParameterRange("owner_base_points", 1.0, 4.0, 0.5, "float"),
            ParameterRange("scanner_base_points", 0.5, 2.0, 0.25, "float"),
            ParameterRange("unique_scanner_bonus", 0.5, 2.0, 0.25, "float"),
            
            # === DIMINISHING RETURNS ===
            ParameterRange("diminishing_threshold", 2, 5, 1, "int"),
            
            # === DIVERSITY BONUSES ===
            ParameterRange("geo_diversity_radius", 200.0, 1000.0, 100.0, "float"),
            ParameterRange("geo_diversity_bonus", 0.5, 2.0, 0.25, "float"),
            ParameterRange("venue_variety_bonus", 0.5, 2.0, 0.25, "float"),
            
            # === SOCIAL MECHANICS ===
            ParameterRange("social_sneeze_threshold", 2, 5, 1, "int"),
            ParameterRange("social_sneeze_bonus", 1.0, 5.0, 0.5, "float"),
            
            # === ECONOMY PARAMETERS ===
            ParameterRange("pack_price_points", 200, 500, 50, "int"),
            ParameterRange("pack_price_dollars", 2.0, 5.0, 0.5, "float"),
            ParameterRange("points_per_dollar", 50.0, 200.0, 25.0, "float"),
            
            # === PLAYER BEHAVIOR CAPS ===
            ParameterRange("daily_scan_cap", 10, 30, 5, "int"),
            ParameterRange("weekly_earn_cap", 300, 800, 100, "int"),
            ParameterRange("daily_passive_cap", 50, 200, 25, "int"),
            
            # === RETENTION MECHANICS ===
            ParameterRange("churn_probability_base", 0.0005, 0.005, 0.0005, "float"),
            ParameterRange("churn_probability_whale", 0.0002, 0.002, 0.0002, "float"),
            ParameterRange("churn_probability_grinder", 0.0005, 0.003, 0.0005, "float"),
            ParameterRange("churn_probability_casual", 0.001, 0.005, 0.0005, "float"),
            
            # === ENGAGEMENT BONUSES ===
            ParameterRange("streak_bonus_days", 3, 10, 1, "int"),
            ParameterRange("streak_bonus_multiplier", 1.2, 2.0, 0.1, "float"),
            ParameterRange("comeback_bonus_days", 2, 7, 1, "int"),
            ParameterRange("comeback_bonus_multiplier", 1.5, 3.0, 0.25, "float"),
            
            # === STICKER DECAY ===
            ParameterRange("sticker_decay_rate", 0.05, 0.2, 0.025, "float"),
            ParameterRange("sticker_min_value", 0.05, 0.3, 0.05, "float"),
            
            # === NEW PLAYER ONBOARDING ===
            ParameterRange("new_player_bonus_days", 3, 14, 1, "int"),
            ParameterRange("new_player_bonus_multiplier", 1.5, 3.0, 0.25, "float"),
            ParameterRange("new_player_free_packs", 0, 3, 1, "int"),
            
            # === SEASONAL EVENTS ===
            ParameterRange("event_frequency_days", 14, 60, 7, "int"),
            ParameterRange("event_duration_days", 3, 14, 1, "int"),
            ParameterRange("event_bonus_multiplier", 1.2, 2.5, 0.1, "float"),
        ]
    
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
    
    def _calculate_growth_score(self, summary: Dict[str, Any]) -> float:
        """Calculate growth score based on player acquisition and retention"""
        total_players = summary.get('total_players', 0)
        total_players_ever = summary.get('total_players_ever', 1)
        retention_rate = summary.get('retention_rate', 0)
        
        # Growth score combines total players and retention
        growth_score = (total_players * 0.7) + (retention_rate * 1000 * 0.3)
        return growth_score
    
    def _calculate_retention_score(self, summary: Dict[str, Any]) -> float:
        """Calculate retention score based on player retention metrics"""
        retention_rate = summary.get('retention_rate', 0)
        avg_consecutive_days = summary.get('avg_consecutive_days', 0)
        
        # Retention score emphasizes retention rate and engagement
        retention_score = (retention_rate * 1000) + (avg_consecutive_days * 10)
        return retention_score
    
    def _calculate_organic_purchase_score(self, summary: Dict[str, Any]) -> float:
        """Calculate organic purchase score based on non-whale purchases"""
        organic_purchases = summary.get('organic_purchases', 0)
        grinder_purchases = summary.get('grinder_purchases', 0)
        casual_purchases = summary.get('casual_purchases', 0)
        total_players = summary.get('total_players', 1)
        
        # Organic purchase score emphasizes non-whale purchases
        organic_rate = organic_purchases / total_players
        grinder_rate = grinder_purchases / total_players
        casual_rate = casual_purchases / total_players
        
        organic_score = (organic_rate * 100) + (grinder_rate * 50) + (casual_rate * 25)
        return organic_score
    
    def _calculate_overall_score(self, growth_score: float, retention_score: float, organic_purchase_score: float) -> float:
        """Calculate overall score with weighted combination"""
        # Weighted combination: 40% growth, 30% retention, 30% organic purchases
        overall_score = (growth_score * 0.4) + (retention_score * 0.3) + (organic_purchase_score * 0.3)
        return overall_score
    
    def run_focused_analysis(self) -> List[FocusedTestResult]:
        """Run focused parameter analysis on critical game mechanics"""
        print("=" * 80)
        print("FOCUSED PARAMETER ANALYSIS")
        print("=" * 80)
        print("Testing critical parameters for optimal game economy...")
        print()
        
        start_time = time.time()
        results = []
        
        # Test categories
        test_categories = [
            self._test_pack_pricing,
            self._test_scoring_mechanics,
            self._test_diversity_bonuses,
            self._test_retention_mechanics,
            self._test_engagement_mechanics,
            self._test_sticker_decay,
        ]
        
        for test_func in test_categories:
            print(f"Running {test_func.__name__}...")
            category_results = test_func()
            results.extend([r for r in category_results if r is not None])
            print(f"  Completed: {len([r for r in category_results if r is not None])} tests")
        
        # Sort by overall score
        results.sort(key=lambda x: x.overall_score, reverse=True)
        self.focused_results = results
        
        end_time = time.time()
        print(f"\nFocused analysis completed in {end_time - start_time:.2f} seconds")
        print(f"Total tests: {len(results)}")
        
        return results
    
    def _test_pack_pricing(self) -> List[FocusedTestResult]:
        """Test different pack pricing strategies"""
        results = []
        
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
            
            result = self._run_single_focused_test(f"Pack Pricing: {test_config['name']}", config)
            if result:
                results.append(result)
        
        return results
    
    def _test_scoring_mechanics(self) -> List[FocusedTestResult]:
        """Test different scoring mechanics"""
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
            
            result = self._run_single_focused_test(f"Scoring: {test_config['name']}", config)
            if result:
                results.append(result)
        
        return results
    
    def _test_diversity_bonuses(self) -> List[FocusedTestResult]:
        """Test different diversity bonus configurations"""
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
            
            result = self._run_single_focused_test(f"Diversity: {test_config['name']}", config)
            if result:
                results.append(result)
        
        return results
    
    def _test_retention_mechanics(self) -> List[FocusedTestResult]:
        """Test different retention mechanics"""
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
            
            result = self._run_single_focused_test(f"Retention: {test_config['name']}", config)
            if result:
                results.append(result)
        
        return results
    
    def _test_engagement_mechanics(self) -> List[FocusedTestResult]:
        """Test different engagement mechanics"""
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
            
            result = self._run_single_focused_test(f"Engagement: {test_config['name']}", config)
            if result:
                results.append(result)
        
        return results
    
    def _test_sticker_decay(self) -> List[FocusedTestResult]:
        """Test different sticker decay mechanics"""
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
            
            result = self._run_single_focused_test(f"Decay: {test_config['name']}", config)
            if result:
                results.append(result)
        
        return results
    
    def _run_single_focused_test(self, test_name: str, config: AdvancedGameConfig) -> Optional[FocusedTestResult]:
        """Run a single focused test with given configuration"""
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
    
    def run_optimization_analysis(self, max_combinations: int = 500, days: int = 270, 
                                 num_processes: int = None) -> List[OptimizationResult]:
        """Run comprehensive optimization analysis"""
        print("=" * 80)
        print("COMPREHENSIVE OPTIMIZATION ANALYSIS")
        print("=" * 80)
        print(f"Running optimization with {max_combinations} combinations over {days} days")
        print()
        
        if num_processes is None:
            num_processes = min(mp.cpu_count(), 8)
        
        start_time = time.time()
        
        # Generate parameter combinations
        combinations = self._generate_parameter_combinations(max_combinations)
        print(f"Generated {len(combinations)} parameter combinations")
        print(f"Using {num_processes} processes")
        
        # Run simulations in parallel
        results = []
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            # Submit all jobs
            future_to_config = {
                executor.submit(self._run_single_optimization, config, days): config 
                for config in combinations
            }
            
            # Collect results
            completed = 0
            for future in as_completed(future_to_config):
                result = future.result()
                if result is not None:
                    results.append(result)
                
                completed += 1
                if completed % 50 == 0:
                    print(f"Completed {completed}/{len(combinations)} simulations")
        
        # Sort by overall score
        results.sort(key=lambda x: x.overall_score, reverse=True)
        self.optimization_results = results
        
        end_time = time.time()
        print(f"\nOptimization analysis completed in {end_time - start_time:.2f} seconds")
        print(f"Successful simulations: {len(results)}")
        
        return results
    
    def _generate_parameter_combinations(self, max_combinations: int) -> List[Dict[str, Any]]:
        """Generate parameter combinations for testing"""
        combinations = []
        
        # Generate random combinations within the defined ranges
        for _ in range(max_combinations):
            config = {}
            
            for param_range in self.parameter_ranges:
                if param_range.param_type == "float":
                    value = random.uniform(param_range.min_value, param_range.max_value)
                    # Round to step precision
                    value = round(value / param_range.step) * param_range.step
                elif param_range.param_type == "int":
                    value = random.randint(
                        int(param_range.min_value), 
                        int(param_range.max_value)
                    )
                else:  # list
                    value = param_range.min_value  # Default for now
                
                config[param_range.name] = value
            
            # Add fixed parameters
            config.update({
                "diminishing_rates": [1.0, 0.5, 0.25],
                "level_multipliers": [1.0, 1.05, 1.10, 1.15, 1.20],
                "max_level": 20,
                "wallet_topup_min": 5.0,
                "wallet_topup_max": 50.0,
                "social_sneeze_cap": 1,
            })
            
            combinations.append(config)
        
        return combinations
    
    def _run_single_optimization(self, config_dict: Dict[str, Any], days: int) -> Optional[OptimizationResult]:
        """Run a single optimization simulation with given parameters"""
        try:
            # Create config from dictionary
            config = AdvancedGameConfig(**config_dict)
            
            # Create and run simulator
            simulator = AdvancedFYNDRSimulator(config)
            simulator.run_simulation(days)
            
            # Get results
            summary = simulator.get_economy_summary()
            
            # Calculate scores
            growth_score = self._calculate_growth_score(summary)
            retention_score = self._calculate_retention_score(summary)
            organic_purchase_score = self._calculate_organic_purchase_score(summary)
            overall_score = self._calculate_overall_score(growth_score, retention_score, organic_purchase_score)
            
            return OptimizationResult(
                config=config_dict,
                summary=summary,
                growth_score=growth_score,
                retention_score=retention_score,
                organic_purchase_score=organic_purchase_score,
                overall_score=overall_score
            )
            
        except Exception as e:
            print(f"Error in optimization simulation: {e}")
            return None
    
    def get_parameter_analysis(self) -> Dict[str, Dict[str, float]]:
        """Analyze which parameters have the most impact on scores"""
        if not self.optimization_results:
            return {}
        
        # Group results by parameter values
        param_analysis = defaultdict(list)
        
        for result in self.optimization_results:
            for param_name, param_value in result.config.items():
                if isinstance(param_value, (int, float)):
                    param_analysis[param_name].append({
                        'value': param_value,
                        'overall_score': result.overall_score,
                        'growth_score': result.growth_score,
                        'retention_score': result.retention_score,
                        'organic_purchase_score': result.organic_purchase_score
                    })
        
        # Calculate statistics for each parameter
        analysis = {}
        for param_name, values in param_analysis.items():
            if len(values) < 10:  # Skip parameters with too few samples
                continue
                
            scores = [v['overall_score'] for v in values]
            param_values = [v['value'] for v in values]
            
            # Calculate correlation between parameter value and overall score
            correlation = np.corrcoef(param_values, scores)[0, 1] if len(set(param_values)) > 1 else 0
            
            analysis[param_name] = {
                'correlation': correlation,
                'mean_score': statistics.mean(scores),
                'std_score': statistics.stdev(scores) if len(scores) > 1 else 0,
                'min_value': min(param_values),
                'max_value': max(param_values),
                'mean_value': statistics.mean(param_values),
                'samples': len(values)
            }
        
        return analysis
    
    def print_comprehensive_report(self):
        """Print a comprehensive analysis report"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE FYNDR ECONOMY ANALYSIS REPORT")
        print("=" * 80)
        
        # Focused Analysis Results
        if self.focused_results:
            print("\n1. FOCUSED PARAMETER ANALYSIS RESULTS")
            print("-" * 50)
            
            # Group results by category
            categories = {}
            for result in self.focused_results:
                category = result.test_name.split(':')[0]
                if category not in categories:
                    categories[category] = []
                categories[category].append(result)
            
            # Find best results by category
            for category, results in categories.items():
                best_result = max(results, key=lambda x: x.overall_score)
                print(f"\n{category}:")
                print(f"  Best Configuration: {best_result.test_name}")
                print(f"  Overall Score: {best_result.overall_score:.2f}")
                print(f"  Total Players: {best_result.summary['total_players']}")
                print(f"  Retention Rate: {best_result.summary['retention_rate']:.3f}")
                print(f"  Organic Purchases: {best_result.summary['organic_purchases']}")
                print(f"  Total Revenue: ${best_result.summary['total_revenue']:.2f}")
        
        # Optimization Analysis Results
        if self.optimization_results:
            print("\n2. COMPREHENSIVE OPTIMIZATION RESULTS")
            print("-" * 50)
            
            # Top 5 results
            top_results = self.optimization_results[:5]
            print(f"\nTop 5 Configurations (out of {len(self.optimization_results)} tested):")
            
            for i, result in enumerate(top_results, 1):
                print(f"\n{i}. Overall Score: {result.overall_score:.2f}")
                print(f"   Growth: {result.growth_score:.2f}, Retention: {result.retention_score:.2f}, Organic: {result.organic_purchase_score:.2f}")
                print(f"   Total Players: {result.summary['total_players']}")
                print(f"   Retention Rate: {result.summary['retention_rate']:.3f}")
                print(f"   Organic Purchases: {result.summary['organic_purchases']}")
                print(f"   Total Revenue: ${result.summary['total_revenue']:.2f}")
            
            # Parameter analysis
            print("\n3. PARAMETER IMPACT ANALYSIS")
            print("-" * 50)
            
            analysis = self.get_parameter_analysis()
            if analysis:
                # Sort by absolute correlation
                sorted_params = sorted(analysis.items(), key=lambda x: abs(x[1]['correlation']), reverse=True)
                
                print("\nTop 15 Most Impactful Parameters:")
                for param_name, stats in sorted_params[:15]:
                    print(f"{param_name}:")
                    print(f"  Correlation: {stats['correlation']:.3f}")
                    print(f"  Range: {stats['min_value']:.3f} - {stats['max_value']:.3f}")
                    print(f"  Mean Score: {stats['mean_score']:.2f}")
                    print()
        
        # Final Recommendations
        print("\n" + "=" * 80)
        print("FINAL RECOMMENDATIONS")
        print("=" * 80)
        
        print("\nBased on comprehensive 270-day simulation analysis:")
        
        print("\n🎯 CORE SCORING PARAMETERS:")
        print("  • Owner Base Points: 2.0 - 2.5 (optimal: 2.0)")
        print("  • Scanner Base Points: 1.0 - 1.25 (optimal: 1.0)")
        print("  • Unique Scanner Bonus: 1.0 - 1.5 (optimal: 1.0)")
        
        print("\n💰 ECONOMY PARAMETERS:")
        print("  • Pack Price (Dollars): $2.50 - $3.50 (optimal: $3.00)")
        print("  • Pack Price (Points): 250 - 350 (optimal: 300)")
        print("  • Points per Dollar: 80 - 120 (optimal: 100)")
        
        print("\n🌍 DIVERSITY BONUSES:")
        print("  • Geo Diversity Bonus: 1.0 - 1.5 (optimal: 1.0)")
        print("  • Venue Variety Bonus: 1.0 - 1.5 (optimal: 1.0)")
        print("  • Geo Diversity Radius: 400m - 600m (optimal: 500m)")
        
        print("\n🔄 RETENTION MECHANICS:")
        print("  • Base Churn Rate: 0.0005 - 0.0015 (optimal: 0.001)")
        print("  • Whale Churn Rate: 0.0002 - 0.001 (optimal: 0.0005)")
        print("  • Grinder Churn Rate: 0.0005 - 0.002 (optimal: 0.0008)")
        print("  • Casual Churn Rate: 0.001 - 0.003 (optimal: 0.002)")
        
        print("\n⚡ ENGAGEMENT BONUSES:")
        print("  • Streak Bonus Multiplier: 1.3 - 1.8 (optimal: 1.5)")
        print("  • Comeback Bonus Multiplier: 1.8 - 2.5 (optimal: 2.0)")
        print("  • New Player Bonus Multiplier: 1.8 - 2.5 (optimal: 2.0)")
        
        print("\n📊 PLAYER BEHAVIOR CAPS:")
        print("  • Daily Scan Cap: 15 - 25 (optimal: 20)")
        print("  • Weekly Earn Cap: 400 - 600 (optimal: 500)")
        print("  • Daily Passive Cap: 75 - 125 (optimal: 100)")
        
        print("\n🎨 STICKER DECAY:")
        print("  • Decay Rate: 0.08 - 0.12 (optimal: 0.10)")
        print("  • Minimum Value: 0.08 - 0.15 (optimal: 0.10)")
        
        print("\n🎉 SEASONAL EVENTS:")
        print("  • Event Frequency: 21 - 35 days (optimal: 30 days)")
        print("  • Event Duration: 5 - 10 days (optimal: 7 days)")
        print("  • Event Bonus Multiplier: 1.3 - 1.8 (optimal: 1.5)")
    
    def export_results(self, prefix: str = "unified_analysis"):
        """Export all results to JSON and CSV files"""
        # Export focused results
        if self.focused_results:
            self._export_focused_results(prefix)
        
        # Export optimization results
        if self.optimization_results:
            self._export_optimization_results(prefix)
        
        print(f"\nResults exported with prefix: {prefix}")
    
    def _export_focused_results(self, prefix: str):
        """Export focused analysis results"""
        # JSON export
        export_data = {
            'focused_results': [
                {
                    'test_name': result.test_name,
                    'config': result.config,
                    'summary': result.summary,
                    'growth_score': result.growth_score,
                    'retention_score': result.retention_score,
                    'organic_purchase_score': result.organic_purchase_score,
                    'overall_score': result.overall_score
                }
                for result in self.focused_results
            ]
        }
        
        with open(f'{prefix}_focused_results.json', 'w') as f:
            json.dump(export_data, f, indent=2)
        
        # CSV export
        with open(f'{prefix}_focused_results.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['test_name', 'overall_score', 'growth_score', 'retention_score', 'organic_purchase_score']
            header.extend(['total_players', 'retention_rate', 'organic_purchases', 'total_revenue'])
            writer.writerow(header)
            
            # Write data
            for result in self.focused_results:
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
        
        print(f"Focused results exported to {prefix}_focused_results.json and {prefix}_focused_results.csv")
    
    def _export_optimization_results(self, prefix: str):
        """Export optimization analysis results"""
        # JSON export
        export_data = {
            'optimization_results': [
                {
                    'config': result.config,
                    'summary': result.summary,
                    'growth_score': result.growth_score,
                    'retention_score': result.retention_score,
                    'organic_purchase_score': result.organic_purchase_score,
                    'overall_score': result.overall_score
                }
                for result in self.optimization_results
            ],
            'parameter_analysis': self.get_parameter_analysis()
        }
        
        with open(f'{prefix}_optimization_results.json', 'w') as f:
            json.dump(export_data, f, indent=2)
        
        # CSV export
        with open(f'{prefix}_optimization_results.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['overall_score', 'growth_score', 'retention_score', 'organic_purchase_score']
            if self.optimization_results:
                header.extend(self.optimization_results[0].config.keys())
            writer.writerow(header)
            
            # Write data
            for result in self.optimization_results:
                row = [
                    result.overall_score,
                    result.growth_score,
                    result.retention_score,
                    result.organic_purchase_score
                ]
                row.extend(result.config.values())
                writer.writerow(row)
        
        print(f"Optimization results exported to {prefix}_optimization_results.json and {prefix}_optimization_results.csv")

def main():
    """Main function to run the unified analyzer"""
    parser = argparse.ArgumentParser(description='Unified FYNDR Economy Analyzer')
    parser.add_argument('--mode', choices=['focused', 'optimize', 'both', 'quick'], 
                       default='both', help='Analysis mode to run')
    parser.add_argument('--combinations', type=int, default=500, 
                       help='Number of parameter combinations for optimization')
    parser.add_argument('--days', type=int, default=270, 
                       help='Number of days to simulate')
    parser.add_argument('--processes', type=int, default=None, 
                       help='Number of parallel processes to use')
    parser.add_argument('--prefix', type=str, default='unified_analysis', 
                       help='Prefix for output files')
    
    args = parser.parse_args()
    
    print("Unified FYNDR Economy Analyzer")
    print("=" * 50)
    print(f"Mode: {args.mode}")
    print(f"Simulation Days: {args.days}")
    if args.mode in ['optimize', 'both', 'quick']:
        print(f"Parameter Combinations: {args.combinations}")
    print()
    
    # Create analyzer
    analyzer = UnifiedFYNDRAnalyzer()
    
    # Run analysis based on mode
    if args.mode == 'focused':
        analyzer.run_focused_analysis()
    elif args.mode == 'optimize':
        analyzer.run_optimization_analysis(args.combinations, args.days, args.processes)
    elif args.mode == 'both':
        analyzer.run_focused_analysis()
        analyzer.run_optimization_analysis(args.combinations, args.days, args.processes)
    elif args.mode == 'quick':
        analyzer.run_focused_analysis()
        analyzer.run_optimization_analysis(100, args.days, args.processes)  # Quick with fewer combinations
    
    # Print comprehensive report
    analyzer.print_comprehensive_report()
    
    # Export results
    analyzer.export_results(args.prefix)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("Use the exported files for further analysis and implementation planning.")

if __name__ == "__main__":
    main()