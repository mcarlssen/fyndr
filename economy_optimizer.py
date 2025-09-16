#!/usr/bin/env python3
"""
FYNDR Economy Optimizer

This module provides comprehensive parameter optimization for the FYNDR game economy
to maximize player growth, retention, and organic purchases over 270-day simulations.
"""

import random
import json
import csv
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from advanced_economy_simulator import AdvancedFYNDRSimulator, AdvancedGameConfig
import itertools
import statistics
from collections import defaultdict

@dataclass
class ParameterRange:
    """Defines a range for a parameter to test"""
    name: str
    min_value: float
    max_value: float
    step: float
    param_type: str  # 'float', 'int', 'list'

@dataclass
class OptimizationResult:
    """Results from a single simulation run"""
    config: Dict[str, Any]
    summary: Dict[str, Any]
    growth_score: float
    retention_score: float
    organic_purchase_score: float
    overall_score: float

class EconomyOptimizer:
    """Main optimizer class for finding optimal economy parameters"""
    
    def __init__(self):
        self.parameter_ranges = self._define_parameter_ranges()
        self.results = []
        
    def _define_parameter_ranges(self) -> List[ParameterRange]:
        """Define the parameter ranges to test based on spec guidelines"""
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
    
    def generate_parameter_combinations(self, max_combinations: int = 1000) -> List[Dict[str, Any]]:
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
    
    def run_single_simulation(self, config_dict: Dict[str, Any], days: int = 270) -> OptimizationResult:
        """Run a single simulation with given parameters"""
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
            print(f"Error in simulation: {e}")
            return None
    
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
    
    def run_optimization(self, max_combinations: int = 1000, days: int = 270, 
                        num_processes: int = None) -> List[OptimizationResult]:
        """Run comprehensive optimization across parameter space"""
        if num_processes is None:
            num_processes = min(mp.cpu_count(), 8)
        
        print(f"Running optimization with {max_combinations} combinations over {days} days")
        print(f"Using {num_processes} processes")
        
        # Generate parameter combinations
        combinations = self.generate_parameter_combinations(max_combinations)
        print(f"Generated {len(combinations)} parameter combinations")
        
        # Run simulations in parallel
        results = []
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            # Submit all jobs
            future_to_config = {
                executor.submit(self.run_single_simulation, config, days): config 
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
        self.results = results
        
        print(f"Optimization complete. {len(results)} successful simulations.")
        return results
    
    def get_top_results(self, n: int = 10) -> List[OptimizationResult]:
        """Get top N results by overall score"""
        return self.results[:n]
    
    def get_parameter_analysis(self) -> Dict[str, Dict[str, float]]:
        """Analyze which parameters have the most impact on scores"""
        if not self.results:
            return {}
        
        # Group results by parameter values
        param_analysis = defaultdict(list)
        
        for result in self.results:
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
    
    def export_results(self, filename: str = "optimization_results.json"):
        """Export optimization results to JSON file"""
        export_data = {
            'results': [
                {
                    'config': result.config,
                    'summary': result.summary,
                    'growth_score': result.growth_score,
                    'retention_score': result.retention_score,
                    'organic_purchase_score': result.organic_purchase_score,
                    'overall_score': result.overall_score
                }
                for result in self.results
            ],
            'parameter_analysis': self.get_parameter_analysis()
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Results exported to {filename}")
    
    def export_csv(self, filename: str = "optimization_results.csv"):
        """Export results to CSV for analysis"""
        if not self.results:
            print("No results to export")
            return
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            header = ['overall_score', 'growth_score', 'retention_score', 'organic_purchase_score']
            header.extend(self.results[0].config.keys())
            writer.writerow(header)
            
            # Write data
            for result in self.results:
                row = [
                    result.overall_score,
                    result.growth_score,
                    result.retention_score,
                    result.organic_purchase_score
                ]
                row.extend(result.config.values())
                writer.writerow(row)
        
        print(f"Results exported to {filename}")

def main():
    """Main function to run optimization"""
    print("FYNDR Economy Optimizer")
    print("=" * 50)
    
    # Create optimizer
    optimizer = EconomyOptimizer()
    
    # Run optimization
    results = optimizer.run_optimization(
        max_combinations=500,  # Start with 500 combinations
        days=270,
        num_processes=4
    )
    
    # Display top results
    print("\nTop 10 Results:")
    print("-" * 50)
    for i, result in enumerate(optimizer.get_top_results(10), 1):
        print(f"\n{i}. Overall Score: {result.overall_score:.2f}")
        print(f"   Growth: {result.growth_score:.2f}, Retention: {result.retention_score:.2f}, Organic: {result.organic_purchase_score:.2f}")
        print(f"   Total Players: {result.summary['total_players']}")
        print(f"   Retention Rate: {result.summary['retention_rate']:.3f}")
        print(f"   Organic Purchases: {result.summary['organic_purchases']}")
    
    # Export results
    optimizer.export_results()
    optimizer.export_csv()
    
    # Display parameter analysis
    print("\nParameter Impact Analysis:")
    print("-" * 50)
    analysis = optimizer.get_parameter_analysis()
    
    # Sort by absolute correlation
    sorted_params = sorted(analysis.items(), key=lambda x: abs(x[1]['correlation']), reverse=True)
    
    for param_name, stats in sorted_params[:15]:  # Top 15 most impactful parameters
        print(f"{param_name}:")
        print(f"  Correlation: {stats['correlation']:.3f}")
        print(f"  Range: {stats['min_value']:.3f} - {stats['max_value']:.3f}")
        print(f"  Mean Score: {stats['mean_score']:.2f}")
        print()

if __name__ == "__main__":
    main()