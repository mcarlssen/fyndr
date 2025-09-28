#!/usr/bin/env python3
"""
OKR-Optimized FYNDR Economy Analyzer

This analyzer specifically targets the three key OKRs:
1. Whales invest more real dollars into the game
2. Grinders level up as fast as possible, leveraging multipliers and bonuses
3. Casual players are motivated to socially "sneeze" the game to other casual players

The analyzer iteratively refines economy parameters to maximize:
- Whale investment and compounding returns
- Grinder leveling speed and sticker density rewards
- Casual player social engagement and userbase growth
- Overall revenue and active userbase after 270 days
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
# Removed parallel processing imports for sequential execution
import statistics
from collections import defaultdict, Counter
import argparse
import math

# Import the advanced simulator
from advanced_economy_simulator import AdvancedFYNDRSimulator, AdvancedGameConfig

@dataclass
class OKROptimizationResult:
    """Results from OKR-focused optimization"""
    config: Dict[str, Any]
    summary: Dict[str, Any]
    
    # OKR-specific scores
    whale_investment_score: float
    grinder_leveling_score: float
    casual_social_score: float
    
    # Traditional scores
    growth_score: float
    retention_score: float
    organic_purchase_score: float
    
    # Overall performance
    overall_score: float
    revenue_score: float
    userbase_score: float

class OKROptimizedAnalyzer:
    """Analyzer optimized for the three key OKRs"""
    
    def __init__(self):
        self.results = []
        self.best_result = None
        self.iteration = 0
        self.convergence_threshold = 0.01
        self.max_iterations = 50
        
    def create_base_config(self) -> AdvancedGameConfig:
        """Create a base configuration optimized for OKRs"""
        return AdvancedGameConfig(
            # === WHALE OPTIMIZATION ===
            # Higher base points to reward whale investment
            owner_base_points=2.5,
            scanner_base_points=1.2,
            unique_scanner_bonus=1.2,
            
            # Better progression for whales
            level_multipliers=[1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0],
            points_per_level=120,
            max_level=25,
            
            # === GRINDER OPTIMIZATION ===
            # Higher diversity bonuses for exploration
            geo_diversity_radius=400.0,
            geo_diversity_bonus=1.5,
            venue_variety_bonus=1.5,
            
            # Better engagement caps for grinders
            weekly_earn_cap=600,
            daily_passive_cap=120,
            sticker_scan_cooldown_hours=11,
            
            # === CASUAL SOCIAL OPTIMIZATION ===
            # Enhanced social mechanics
            social_sneeze_threshold=2,
            social_sneeze_bonus=4.0,
            social_sneeze_cap=2,
            
            # Better new player experience
            new_player_bonus_days=10,
            new_player_bonus_multiplier=2.5,
            new_player_free_packs=2,
            
            # === ECONOMY BALANCE ===
            pack_price_points=300,
            pack_price_dollars=3.0,
            points_per_dollar=100.0,
            
            # === RETENTION OPTIMIZATION ===
            churn_probability_base=0.0008,
            churn_probability_whale=0.0003,
            churn_probability_grinder=0.0006,
            churn_probability_casual=0.0015,
            
            # === ENGAGEMENT BONUSES ===
            streak_bonus_days=5,
            streak_bonus_multiplier=1.8,
            comeback_bonus_days=2,
            comeback_bonus_multiplier=2.5,
            
            # === STICKER DECAY ===
            # Removed sticker decay - no longer needed
            
            # === SEASONAL EVENTS ===
            event_frequency_days=25,
            event_duration_days=8,
            event_bonus_multiplier=1.8,
            
            # === DIMINISHING RETURNS ===
            diminishing_threshold=3,
            diminishing_rates=[1.0, 0.6, 0.3],
        )
    
    def calculate_whale_investment_score(self, summary: Dict[str, Any]) -> float:
        """Calculate score for whale investment and compounding returns"""
        whale_revenue = summary.get('whale_purchases', 0) * 3.0  # Approximate revenue
        whale_count = summary.get('whale_count', 1)
        total_revenue = summary.get('total_revenue', 1)
        
        # Whale revenue per whale
        whale_arpu = whale_revenue / whale_count if whale_count > 0 else 0
        
        # Whale revenue as percentage of total
        whale_revenue_share = whale_revenue / total_revenue if total_revenue > 0 else 0
        
        # Compounding effect (higher levels = better returns)
        avg_level = summary.get('avg_level', 1)
        level_multiplier = 1 + (avg_level - 1) * 0.1
        
        # Score combines ARPU, revenue share, and level progression
        investment_score = (whale_arpu * 0.4) + (whale_revenue_share * 100 * 0.4) + (level_multiplier * 20 * 0.2)
        
        return investment_score
    
    def calculate_grinder_leveling_score(self, summary: Dict[str, Any]) -> float:
        """Calculate score for grinder leveling speed and sticker density rewards"""
        grinder_count = summary.get('grinder_count', 1)
        total_stickers = summary.get('total_stickers', 1)
        total_scans = summary.get('total_scans', 1)
        
        # Sticker density (stickers per grinder)
        sticker_density = total_stickers / grinder_count if grinder_count > 0 else 0
        
        # Scan activity (scans per grinder)
        scan_activity = total_scans / grinder_count if grinder_count > 0 else 0
        
        # Points per scan (efficiency)
        total_points = summary.get('total_points', 1)
        points_per_scan = total_points / total_scans if total_scans > 0 else 0
        
        # Level progression rate
        avg_points_per_player = summary.get('avg_points_per_player', 0)
        leveling_speed = avg_points_per_player / 120  # Points per level
        
        # Score combines density, activity, efficiency, and leveling
        leveling_score = (sticker_density * 0.3) + (scan_activity * 0.3) + (points_per_scan * 0.2) + (leveling_speed * 50 * 0.2)
        
        return leveling_score
    
    def calculate_casual_social_score(self, summary: Dict[str, Any]) -> float:
        """Calculate score for casual player social engagement and userbase growth"""
        casual_count = summary.get('casual_count', 1)
        total_players = summary.get('total_players', 1)
        total_players_ever = summary.get('total_players_ever', 1)
        
        # Userbase growth
        growth_rate = (total_players_ever - total_players) / max(total_players, 1)
        
        # Casual player retention
        retention_rate = summary.get('retention_rate', 0)
        
        # Social engagement (approximated by diversity metrics)
        avg_scans_per_player = summary.get('avg_scans_per_player', 0)
        social_engagement = min(avg_scans_per_player / 10, 1.0)  # Normalize to 0-1
        
        # New player acquisition
        new_players = summary.get('new_players_today', 0)
        acquisition_rate = new_players / max(total_players, 1)
        
        # Score combines growth, retention, engagement, and acquisition
        social_score = (growth_rate * 100 * 0.3) + (retention_rate * 100 * 0.3) + (social_engagement * 50 * 0.2) + (acquisition_rate * 100 * 0.2)
        
        return social_score
    
    def calculate_traditional_scores(self, summary: Dict[str, Any]) -> Tuple[float, float, float]:
        """Calculate traditional growth, retention, and organic purchase scores"""
        total_players = summary.get('total_players', 0)
        retention_rate = summary.get('retention_rate', 0)
        organic_purchases = summary.get('organic_purchases', 0)
        
        # Growth score
        growth_score = total_players * 0.7 + (retention_rate * 1000 * 0.3)
        
        # Retention score
        avg_consecutive_days = summary.get('avg_consecutive_days', 0)
        retention_score = (retention_rate * 1000) + (avg_consecutive_days * 10)
        
        # Organic purchase score
        grinder_purchases = summary.get('grinder_purchases', 0)
        casual_purchases = summary.get('casual_purchases', 0)
        organic_score = (organic_purchases * 0.5) + (grinder_purchases * 0.3) + (casual_purchases * 0.2)
        
        return growth_score, retention_score, organic_score
    
    def calculate_overall_score(self, whale_score: float, grinder_score: float, casual_score: float,
                              growth_score: float, retention_score: float, organic_score: float,
                              summary: Dict[str, Any]) -> Tuple[float, float, float]:
        """Calculate overall performance scores"""
        
        # OKR-weighted score (prioritizes the three key objectives)
        okr_score = (whale_score * 0.4) + (grinder_score * 0.35) + (casual_score * 0.25)
        
        # Revenue score (total revenue at end of 270 days)
        total_revenue = summary.get('total_revenue', 0)
        revenue_score = total_revenue
        
        # Userbase score (total active players at end of 270 days)
        total_players = summary.get('total_players', 0)
        userbase_score = total_players
        
        # Overall score combines OKR performance with revenue and userbase
        overall_score = (okr_score * 0.5) + (revenue_score * 0.3) + (userbase_score * 0.2)
        
        return overall_score, revenue_score, userbase_score
    
    def generate_parameter_variations(self, base_config: AdvancedGameConfig, iteration: int) -> List[AdvancedGameConfig]:
        """Generate parameter variations for iterative optimization"""
        variations = []
        
        # Base configuration
        variations.append(base_config)
        
        # BROAD whale optimization variations
        whale_variations = [
            # Much higher base points for better whale returns
            AdvancedGameConfig(**{**base_config.__dict__, 'owner_base_points': 2.0}),
            AdvancedGameConfig(**{**base_config.__dict__, 'owner_base_points': 2.5}),
            AdvancedGameConfig(**{**base_config.__dict__, 'owner_base_points': 3.0}),
            AdvancedGameConfig(**{**base_config.__dict__, 'owner_base_points': 3.5}),
            AdvancedGameConfig(**{**base_config.__dict__, 'owner_base_points': 4.0}),
            AdvancedGameConfig(**{**base_config.__dict__, 'owner_base_points': 5.0}),
            AdvancedGameConfig(**{**base_config.__dict__, 'owner_base_points': 6.0}),
            # Much better progression multipliers
            AdvancedGameConfig(**{**base_config.__dict__, 'level_multipliers': [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]}),
            AdvancedGameConfig(**{**base_config.__dict__, 'level_multipliers': [1.0, 1.15, 1.3, 1.45, 1.6, 1.75, 1.9, 2.05, 2.2, 2.35, 2.5]}),
            AdvancedGameConfig(**{**base_config.__dict__, 'level_multipliers': [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0]}),
            # Much lower whale churn
            AdvancedGameConfig(**{**base_config.__dict__, 'churn_probability_whale': 0.0001}),
            AdvancedGameConfig(**{**base_config.__dict__, 'churn_probability_whale': 0.0002}),
            AdvancedGameConfig(**{**base_config.__dict__, 'churn_probability_whale': 0.0003}),
            AdvancedGameConfig(**{**base_config.__dict__, 'churn_probability_whale': 0.0005}),
        ]
        
        # Grinder optimization variations
        grinder_variations = [
            # Higher diversity bonuses
            AdvancedGameConfig(**{**base_config.__dict__, 'geo_diversity_bonus': base_config.geo_diversity_bonus * 1.2}),
            # Better scan cooldown
            AdvancedGameConfig(**{**base_config.__dict__, 'sticker_scan_cooldown_hours': base_config.sticker_scan_cooldown_hours - 2}),
            # Lower grinder churn
            AdvancedGameConfig(**{**base_config.__dict__, 'churn_probability_grinder': base_config.churn_probability_grinder * 0.9}),
        ]
        
        # Casual social optimization variations
        casual_variations = [
            # Enhanced social mechanics
            AdvancedGameConfig(**{**base_config.__dict__, 'social_sneeze_bonus': base_config.social_sneeze_bonus * 1.3}),
            # Better new player experience
            AdvancedGameConfig(**{**base_config.__dict__, 'new_player_bonus_multiplier': base_config.new_player_bonus_multiplier * 1.2}),
            # Lower casual churn
            AdvancedGameConfig(**{**base_config.__dict__, 'churn_probability_casual': base_config.churn_probability_casual * 0.9}),
        ]
        
        # Economy balance variations
        economy_variations = [
            # Slightly lower pack price for accessibility
            AdvancedGameConfig(**{**base_config.__dict__, 'pack_price_dollars': base_config.pack_price_dollars * 0.95}),
            # Better point conversion
            AdvancedGameConfig(**{**base_config.__dict__, 'points_per_dollar': base_config.points_per_dollar * 1.1}),
        ]
        
        # Combine variations
        all_variations = whale_variations + grinder_variations + casual_variations + economy_variations
        
        # Add some random variations for exploration
        for _ in range(5):
            random_config = AdvancedGameConfig(**base_config.__dict__)
            
            # Randomly adjust key parameters
            random_config.owner_base_points *= random.uniform(0.9, 1.1)
            random_config.geo_diversity_bonus *= random.uniform(0.9, 1.1)
            random_config.social_sneeze_bonus *= random.uniform(0.9, 1.1)
            random_config.churn_probability_whale *= random.uniform(0.8, 1.2)
            random_config.churn_probability_grinder *= random.uniform(0.8, 1.2)
            random_config.churn_probability_casual *= random.uniform(0.8, 1.2)
            
            all_variations.append(random_config)
        
        return all_variations
    
    def run_single_simulation(self, config: AdvancedGameConfig, days: int = 270) -> Optional[OKROptimizationResult]:
        """Run a single simulation and calculate OKR scores"""
        try:
            simulator = AdvancedFYNDRSimulator(config)
            simulator.run_simulation(days)
            summary = simulator.get_economy_summary()
            
            # Calculate OKR-specific scores
            whale_score = self.calculate_whale_investment_score(summary)
            grinder_score = self.calculate_grinder_leveling_score(summary)
            casual_score = self.calculate_casual_social_score(summary)
            
            # Calculate traditional scores
            growth_score, retention_score, organic_score = self.calculate_traditional_scores(summary)
            
            # Calculate overall scores
            overall_score, revenue_score, userbase_score = self.calculate_overall_score(
                whale_score, grinder_score, casual_score,
                growth_score, retention_score, organic_score,
                summary
            )
            
            return OKROptimizationResult(
                config=config.__dict__,
                summary=summary,
                whale_investment_score=whale_score,
                grinder_leveling_score=grinder_score,
                casual_social_score=casual_score,
                growth_score=growth_score,
                retention_score=retention_score,
                organic_purchase_score=organic_score,
                overall_score=overall_score,
                revenue_score=revenue_score,
                userbase_score=userbase_score
            )
            
        except Exception as e:
            print(f"Error in simulation: {e}")
            return None
    
    def run_iterative_optimization(self, max_iterations: int = 50, days: int = 270) -> OKROptimizationResult:
        """Run iterative optimization to find the best economy parameters"""
        print("=" * 80)
        print("OKR-OPTIMIZED FYNDR ECONOMY ANALYSIS")
        print("=" * 80)
        print("Optimizing for:")
        print("1. Whale investment and compounding returns")
        print("2. Grinder leveling speed and sticker density rewards")
        print("3. Casual player social engagement and userbase growth")
        print(f"Target: Maximum revenue + active userbase after {days} days")
        print()
        
        # Start with base configuration
        current_config = self.create_base_config()
        best_score = 0
        convergence_count = 0
        
        for iteration in range(max_iterations):
            self.iteration = iteration
            print(f"Iteration {iteration + 1}/{max_iterations}")
            
            # Generate parameter variations
            variations = self.generate_parameter_variations(current_config, iteration)
            print(f"Testing {len(variations)} parameter variations...")
            
            # Run simulations sequentially with progress tracking
            results = []
            for i, config in enumerate(variations):
                progress = (i + 1) / len(variations) * 100
                print(f"  Running simulation {i+1}/{len(variations)} ({progress:.1f}%)...", end=" ")
                result = self.run_single_simulation(config, days)
                if result is not None:
                    results.append(result)
                    print(f"Score: {result.overall_score:.2f}")
                else:
                    print("Failed")
            
            if not results:
                print("No successful simulations in this iteration")
                continue
            
            # Sort by overall score
            results.sort(key=lambda x: x.overall_score, reverse=True)
            best_result = results[0]
            
            print(f"Best score this iteration: {best_result.overall_score:.2f}")
            print(f"  Whale Investment: {best_result.whale_investment_score:.2f}")
            print(f"  Grinder Leveling: {best_result.grinder_leveling_score:.2f}")
            print(f"  Casual Social: {best_result.casual_social_score:.2f}")
            print(f"  Revenue: ${best_result.revenue_score:.2f}")
            print(f"  Userbase: {best_result.userbase_score}")
            
            # Check for improvement
            if best_result.overall_score > best_score:
                improvement = best_result.overall_score - best_score
                print(f"Improvement: +{improvement:.2f}")
                best_score = best_result.overall_score
                self.best_result = best_result
                current_config = AdvancedGameConfig(**best_result.config)
                convergence_count = 0
            else:
                convergence_count += 1
                print("No improvement - convergence count:", convergence_count)
            
            # Check for convergence
            if convergence_count >= 3:
                print("Converged - no improvement for 3 iterations")
                break
            
            print()
        
        print("=" * 80)
        print("OPTIMIZATION COMPLETE")
        print("=" * 80)
        
        if self.best_result:
            print(f"Best Overall Score: {self.best_result.overall_score:.2f}")
            print(f"Final Revenue: ${self.best_result.revenue_score:.2f}")
            print(f"Final Userbase: {self.best_result.userbase_score}")
            print()
            print("OKR Performance:")
            print(f"  Whale Investment Score: {self.best_result.whale_investment_score:.2f}")
            print(f"  Grinder Leveling Score: {self.best_result.grinder_leveling_score:.2f}")
            print(f"  Casual Social Score: {self.best_result.casual_social_score:.2f}")
        
        return self.best_result
    
    def print_detailed_analysis(self):
        """Print detailed analysis of the best result"""
        if not self.best_result:
            print("No results to analyze")
            return
        
        result = self.best_result
        summary = result.summary
        
        print("\n" + "=" * 80)
        print("DETAILED OKR ANALYSIS")
        print("=" * 80)
        
        # Whale Analysis
        print("\n🐋 WHALE INVESTMENT ANALYSIS:")
        print(f"  Total Whale Revenue: ${summary.get('whale_purchases', 0) * 3.0:.2f}")
        print(f"  Whale Count: {summary.get('whale_count', 0)}")
        print(f"  Whale ARPU: ${(summary.get('whale_purchases', 0) * 3.0) / max(summary.get('whale_count', 1), 1):.2f}")
        print(f"  Whale Revenue Share: {(summary.get('whale_purchases', 0) * 3.0) / max(summary.get('total_revenue', 1), 1) * 100:.1f}%")
        print(f"  Average Player Level: {summary.get('avg_level', 1):.1f}")
        
        # Grinder Analysis
        print("\n⚡ GRINDER LEVELING ANALYSIS:")
        print(f"  Grinder Count: {summary.get('grinder_count', 0)}")
        print(f"  Total Stickers: {summary.get('total_stickers', 0)}")
        print(f"  Sticker Density: {summary.get('total_stickers', 0) / max(summary.get('grinder_count', 1), 1):.1f} stickers/grinder")
        print(f"  Total Scans: {summary.get('total_scans', 0)}")
        print(f"  Scan Activity: {summary.get('total_scans', 0) / max(summary.get('grinder_count', 1), 1):.1f} scans/grinder")
        print(f"  Points per Scan: {summary.get('total_points', 0) / max(summary.get('total_scans', 1), 1):.2f}")
        
        # Casual Social Analysis
        print("\n👥 CASUAL SOCIAL ANALYSIS:")
        print(f"  Casual Count: {summary.get('casual_count', 0)}")
        print(f"  Total Players: {summary.get('total_players', 0)}")
        print(f"  Total Players Ever: {summary.get('total_players_ever', 0)}")
        print(f"  Growth Rate: {(summary.get('total_players_ever', 0) - summary.get('total_players', 0)) / max(summary.get('total_players', 1), 1) * 100:.1f}%")
        print(f"  Retention Rate: {summary.get('retention_rate', 0) * 100:.1f}%")
        print(f"  Average Scans per Player: {summary.get('avg_scans_per_player', 0):.1f}")
        
        # Economy Summary
        print("\n💰 ECONOMY SUMMARY:")
        print(f"  Total Revenue: ${summary.get('total_revenue', 0):.2f}")
        print(f"  Organic Purchases: {summary.get('organic_purchases', 0)}")
        print(f"  Average Points per Player: {summary.get('avg_points_per_player', 0):.1f}")
        print(f"  Points per Scan: {summary.get('total_points', 0) / max(summary.get('total_scans', 1), 1):.2f}")
        
        # Optimal Parameters
        print("\n🎯 OPTIMAL PARAMETERS:")
        config = result.config
        print(f"  Owner Base Points: {config.get('owner_base_points', 0):.2f}")
        print(f"  Scanner Base Points: {config.get('scanner_base_points', 0):.2f}")
        print(f"  Geo Diversity Bonus: {config.get('geo_diversity_bonus', 0):.2f}")
        print(f"  Social Sneeze Bonus: {config.get('social_sneeze_bonus', 0):.2f}")
        print(f"  Daily Scan Cap: {config.get('daily_scan_cap', 0)}")
        print(f"  Pack Price: ${config.get('pack_price_dollars', 0):.2f}")
        print(f"  Whale Churn Rate: {config.get('churn_probability_whale', 0):.4f}")
        print(f"  Grinder Churn Rate: {config.get('churn_probability_grinder', 0):.4f}")
        print(f"  Casual Churn Rate: {config.get('churn_probability_casual', 0):.4f}")
    
    def export_results(self, prefix: str = "okr_optimized"):
        """Export optimization results"""
        if not self.best_result:
            print("No results to export")
            return
        
        # Export detailed results
        export_data = {
            'optimization_result': {
                'config': self.best_result.config,
                'summary': self.best_result.summary,
                'whale_investment_score': self.best_result.whale_investment_score,
                'grinder_leveling_score': self.best_result.grinder_leveling_score,
                'casual_social_score': self.best_result.casual_social_score,
                'growth_score': self.best_result.growth_score,
                'retention_score': self.best_result.retention_score,
                'organic_purchase_score': self.best_result.organic_purchase_score,
                'overall_score': self.best_result.overall_score,
                'revenue_score': self.best_result.revenue_score,
                'userbase_score': self.best_result.userbase_score,
            },
            'optimization_metadata': {
                'iterations': self.iteration + 1,
                'convergence_threshold': self.convergence_threshold,
                'max_iterations': self.max_iterations,
            }
        }
        
        with open(f'{prefix}_results.json', 'w') as f:
            json.dump(export_data, f, indent=2)
        
        # Export CSV summary
        with open(f'{prefix}_summary.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'metric', 'value'
            ])
            
            result = self.best_result
            writer.writerow(['overall_score', result.overall_score])
            writer.writerow(['whale_investment_score', result.whale_investment_score])
            writer.writerow(['grinder_leveling_score', result.grinder_leveling_score])
            writer.writerow(['casual_social_score', result.casual_social_score])
            writer.writerow(['revenue_score', result.revenue_score])
            writer.writerow(['userbase_score', result.userbase_score])
            writer.writerow(['total_revenue', result.summary.get('total_revenue', 0)])
            writer.writerow(['total_players', result.summary.get('total_players', 0)])
            writer.writerow(['whale_count', result.summary.get('whale_count', 0)])
            writer.writerow(['grinder_count', result.summary.get('grinder_count', 0)])
            writer.writerow(['casual_count', result.summary.get('casual_count', 0)])
        
        print(f"Results exported to {prefix}_results.json and {prefix}_summary.csv")

def main():
    """Main function to run OKR-optimized analysis"""
    parser = argparse.ArgumentParser(description='OKR-Optimized FYNDR Economy Analyzer')
    parser.add_argument('--iterations', type=int, default=50, 
                       help='Maximum number of optimization iterations')
    parser.add_argument('--days', type=int, default=270, 
                       help='Number of days to simulate')
    # Removed processes argument - now runs sequentially
    parser.add_argument('--prefix', type=str, default='okr_optimized', 
                       help='Prefix for output files')
    
    args = parser.parse_args()
    
    print("OKR-Optimized FYNDR Economy Analyzer")
    print("=" * 50)
    print(f"Max Iterations: {args.iterations}")
    print(f"Simulation Days: {args.days}")
    print()
    
    # Create analyzer
    analyzer = OKROptimizedAnalyzer()
    
    # Run optimization
    start_time = time.time()
    best_result = analyzer.run_iterative_optimization(
        max_iterations=args.iterations,
        days=args.days
    )
    end_time = time.time()
    
    print(f"Optimization completed in {end_time - start_time:.2f} seconds")
    
    # Print detailed analysis
    analyzer.print_detailed_analysis()
    
    # Export results
    analyzer.export_results(args.prefix)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("Use the exported files for implementation planning.")

if __name__ == "__main__":
    main()
