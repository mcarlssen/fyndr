#!/usr/bin/env python3
"""
OKR-Optimized FYNDR Economy Analyzer V2

This analyzer implements a sophisticated multi-phase optimization approach:
1. Phase 1: Optimize parameters for WHALES only
2. Phase 2: Optimize parameters for GRINDERS only  
3. Phase 3: Optimize parameters for CASUAL players only
4. Phase 4: Multi-player optimization combining best individual results

This approach finds player-specific optimal parameters and then tests
how they work together, rather than using a one-size-fits-all approach.
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
import statistics
from collections import defaultdict, Counter
import argparse
import math

# Import the advanced simulator
from advanced_economy_simulator import AdvancedFYNDRSimulator, AdvancedGameConfig

# Import visualization engine
from visualization_engine import FYNDRVisualizationEngine

@dataclass
class PlayerTypeResult:
    """Results from optimizing for a specific player type"""
    player_type: str
    config: Dict[str, Any]
    summary: Dict[str, Any]
    target_score: float
    overall_score: float
    revenue: float
    userbase: int

@dataclass
class MultiPlayerResult:
    """Results from multi-player optimization"""
    config: Dict[str, Any]
    summary: Dict[str, Any]
    whale_score: float
    grinder_score: float
    casual_score: float
    overall_score: float
    revenue: float
    userbase: int

class OKROptimizedAnalyzerV2:
    """V2 analyzer with player-specific optimization phases"""
    
    def __init__(self):
        self.whale_result: Optional[PlayerTypeResult] = None
        self.grinder_result: Optional[PlayerTypeResult] = None
        self.casual_result: Optional[PlayerTypeResult] = None
        self.multiplayer_result: Optional[MultiPlayerResult] = None
        self.phase_results = {}
        self.all_simulation_results = []  # Store all simulation results for visualization
        self.visualization_engine = FYNDRVisualizationEngine()
        
    def create_base_config(self) -> AdvancedGameConfig:
        """Create a balanced base configuration"""
        return AdvancedGameConfig(
            # === CORE SCORING PARAMETERS ===
            owner_base_points=2.0,
            scanner_base_points=1.0,
            unique_scanner_bonus=1.0,
            
            # === DIVERSITY BONUSES ===
            geo_diversity_radius=500.0,
            geo_diversity_bonus=1.0,
            venue_variety_bonus=1.0,
            
            # === SOCIAL MECHANICS ===
            social_sneeze_threshold=3,
            social_sneeze_bonus=3.0,
            social_sneeze_cap=1,
            
            # === PROGRESSION SYSTEM ===
            level_multipliers=[1.0, 1.05, 1.10, 1.15, 1.20],
            points_per_level=100,
            max_level=20,
            
            # === ECONOMY PARAMETERS ===
            pack_price_points=300,
            pack_price_dollars=3.0,
            points_per_dollar=100.0,
            wallet_topup_min=5.0,
            wallet_topup_max=50.0,
            
            # === PLAYER BEHAVIOR CAPS ===
            weekly_earn_cap=500,
            daily_passive_cap=100,
            sticker_scan_cooldown_hours=11,
            
            # === RETENTION MECHANICS ===
            churn_probability_base=0.001,
            churn_probability_whale=0.0005,
            churn_probability_grinder=0.0008,
            churn_probability_casual=0.002,
            
            # === ENGAGEMENT BONUSES ===
            streak_bonus_days=7,
            streak_bonus_multiplier=1.5,
            comeback_bonus_days=3,
            comeback_bonus_multiplier=2.0,
            
            # === NEW PLAYER ONBOARDING ===
            new_player_bonus_days=7,
            new_player_bonus_multiplier=2.0,
            new_player_free_packs=1,
            
            # === SEASONAL EVENTS ===
            event_frequency_days=30,
            event_duration_days=7,
            event_bonus_multiplier=1.5,
            
            # === DIMINISHING RETURNS ===
            diminishing_threshold=3,
            diminishing_rates=[1.0, 0.6, 0.3],
        )
    
    def calculate_whale_score(self, summary: Dict[str, Any]) -> float:
        """Calculate whale-specific optimization score"""
        whale_revenue = summary.get('whale_purchases', 0) * summary.get('pack_price_dollars', 3.0)
        whale_count = summary.get('whale_count', 1)
        total_revenue = summary.get('total_revenue', 1)
        avg_level = summary.get('avg_level', 1)
        
        # Whale ARPU
        whale_arpu = whale_revenue / whale_count if whale_count > 0 else 0
        
        # Whale revenue share
        whale_revenue_share = whale_revenue / total_revenue if total_revenue > 0 else 0
        
        # Level progression (compounding returns)
        level_progression = avg_level / 10
        
        # Whale retention
        whale_retention = 1 - summary.get('churn_rate', 0.1)
        
        # Weighted score focusing on whale investment and retention
        whale_score = (whale_arpu * 0.4) + (whale_revenue_share * 200 * 0.3) + (level_progression * 100 * 0.2) + (whale_retention * 100 * 0.1)
        
        return whale_score
    
    def calculate_grinder_score(self, summary: Dict[str, Any]) -> float:
        """Calculate grinder-specific optimization score"""
        grinder_count = summary.get('grinder_count', 1)
        total_stickers = summary.get('total_stickers', 1)
        total_scans = summary.get('total_scans', 1)
        total_points = summary.get('total_points', 1)
        grinder_purchases = summary.get('grinder_purchases', 0)  # Stickers placed by grinders
        
        # Sticker density (exploration reward)
        sticker_density = total_stickers / grinder_count if grinder_count > 0 else 0
        
        # Scan activity
        scan_activity = total_scans / grinder_count if grinder_count > 0 else 0
        
        # Points per scan (efficiency)
        points_per_scan = total_points / total_scans if total_scans > 0 else 0
        
        # Level progression
        avg_points_per_player = summary.get('avg_points_per_player', 0)
        leveling_speed = avg_points_per_player / 100  # Points per level
        
        # Grinder sticker placement (their "revenue" - they pay with points)
        sticker_placement = grinder_purchases / grinder_count if grinder_count > 0 else 0
        
        # Grinder retention
        grinder_retention = 1 - summary.get('churn_rate', 0.1)
        
        # Weighted score focusing on leveling, engagement, and sticker placement
        grinder_score = (sticker_density * 0.25) + (scan_activity * 0.25) + (points_per_scan * 0.2) + (leveling_speed * 50 * 0.1) + (sticker_placement * 10 * 0.1) + (grinder_retention * 100 * 0.1)
        
        return grinder_score
    
    def calculate_casual_score(self, summary: Dict[str, Any]) -> float:
        """Calculate casual-specific optimization score"""
        casual_count = summary.get('casual_count', 1)
        total_players = summary.get('total_players', 1)
        total_players_ever = summary.get('total_players_ever', 1)
        retention_rate = summary.get('retention_rate', 0)
        
        # Growth rate
        growth_rate = (total_players_ever - total_players) / max(total_players, 1)
        
        # Social engagement (scan activity as proxy)
        avg_scans_per_player = summary.get('avg_scans_per_player', 0)
        social_engagement = min(avg_scans_per_player / 10, 1.0)
        
        # New player acquisition
        new_players = summary.get('new_players_today', 0)
        acquisition_rate = new_players / max(total_players, 1)
        
        # Casual retention
        casual_retention = retention_rate
        
        # Weighted score focusing on growth and social engagement
        casual_score = (growth_rate * 200 * 0.4) + (social_engagement * 50 * 0.3) + (acquisition_rate * 100 * 0.2) + (casual_retention * 100 * 0.1)
        
        return casual_score
    
    def generate_whale_optimizations(self, base_config: AdvancedGameConfig) -> List[AdvancedGameConfig]:
        """Generate parameter variations optimized for whale investment with BROAD ranges"""
        variations = []
        
        # Base configuration
        variations.append(base_config)
        
        # BROAD whale-specific optimizations
        whale_optimizations = [
            # Much higher base points for better whale returns
            {'owner_base_points': 2.5, 'scanner_base_points': 1.1},
            {'owner_base_points': 3.0, 'scanner_base_points': 1.2},
            {'owner_base_points': 3.5, 'scanner_base_points': 1.3},
            {'owner_base_points': 4.0, 'scanner_base_points': 1.4},
            {'owner_base_points': 5.0, 'scanner_base_points': 1.5},
            {'owner_base_points': 6.0, 'scanner_base_points': 1.6},
            
            # Much better progression for whales
            {'level_multipliers': [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]},
            {'level_multipliers': [1.0, 1.15, 1.3, 1.45, 1.6, 1.75, 1.9, 2.05, 2.2, 2.35, 2.5]},
            {'level_multipliers': [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0]},
            {'level_multipliers': [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5]},
            
            # Much lower whale churn (DOUBLED RANGE)
            {'churn_probability_whale': 0.0001},
            {'churn_probability_whale': 0.0005},
            {'churn_probability_whale': 0.001},
            {'churn_probability_whale': 0.005},
            {'churn_probability_whale': 0.01},
            {'churn_probability_whale': 0.05},
            {'churn_probability_whale': 0.1},
            
            # Much broader pack pricing for whales (DOUBLED RANGE)
            {'pack_price_dollars': 0.5, 'points_per_dollar': 200.0},
            {'pack_price_dollars': 1.0, 'points_per_dollar': 180.0},
            {'pack_price_dollars': 1.5, 'points_per_dollar': 160.0},
            {'pack_price_dollars': 2.0, 'points_per_dollar': 140.0},
            {'pack_price_dollars': 2.5, 'points_per_dollar': 120.0},
            {'pack_price_dollars': 3.0, 'points_per_dollar': 100.0},
            {'pack_price_dollars': 4.0, 'points_per_dollar': 80.0},
            {'pack_price_dollars': 5.0, 'points_per_dollar': 60.0},
            {'pack_price_dollars': 8.0, 'points_per_dollar': 40.0},
            {'pack_price_dollars': 12.0, 'points_per_dollar': 30.0},
            {'pack_price_dollars': 16.0, 'points_per_dollar': 20.0},
            {'pack_price_dollars': 20.0, 'points_per_dollar': 10.0},
            
            # Much higher weekly caps for whales
            {'weekly_earn_cap': 600, 'daily_passive_cap': 120},
            {'weekly_earn_cap': 800, 'daily_passive_cap': 150},
            {'weekly_earn_cap': 1000, 'daily_passive_cap': 200},
            {'weekly_earn_cap': 1500, 'daily_passive_cap': 300},
            {'weekly_earn_cap': 2000, 'daily_passive_cap': 400},
        ]
        
        for opt in whale_optimizations:
            config_dict = base_config.__dict__.copy()
            config_dict.update(opt)
            variations.append(AdvancedGameConfig(**config_dict))
        
        # Random variations for exploration
        for _ in range(5):
            config_dict = base_config.__dict__.copy()
            config_dict['owner_base_points'] *= random.uniform(1.2, 2.0)
            config_dict['scanner_base_points'] *= random.uniform(1.1, 1.5)
            config_dict['churn_probability_whale'] *= random.uniform(0.3, 1.0)
            config_dict['pack_price_dollars'] *= random.uniform(0.7, 1.5)
            variations.append(AdvancedGameConfig(**config_dict))
        
        return variations
    
    def generate_grinder_optimizations(self, base_config: AdvancedGameConfig) -> List[AdvancedGameConfig]:
        """Generate parameter variations optimized for grinder leveling"""
        variations = []
        
        # Base configuration
        variations.append(base_config)
        
        # Grinder-specific optimizations
        grinder_optimizations = [
            # Higher diversity bonuses for exploration
            {'geo_diversity_bonus': 1.5, 'venue_variety_bonus': 1.5},
            {'geo_diversity_bonus': 2.0, 'venue_variety_bonus': 2.0},
            {'geo_diversity_bonus': 2.5, 'venue_variety_bonus': 2.5},
            
            # Better scan cooldowns for grinders
            {'sticker_scan_cooldown_hours': 8},
            {'sticker_scan_cooldown_hours': 6},
            {'sticker_scan_cooldown_hours': 4},
            
            # Lower grinder churn
            {'churn_probability_grinder': 0.0003},
            {'churn_probability_grinder': 0.0004},
            {'churn_probability_grinder': 0.0005},
            
            # Better point conversion for organic purchases
            {'pack_price_points': 250, 'points_per_dollar': 120.0},
            {'pack_price_points': 200, 'points_per_dollar': 130.0},
            {'pack_price_points': 350, 'points_per_dollar': 100.0},
            
            # Higher weekly caps for grinders
            {'weekly_earn_cap': 800, 'daily_passive_cap': 150},
            {'weekly_earn_cap': 1000, 'daily_passive_cap': 200},
        ]
        
        for opt in grinder_optimizations:
            config_dict = base_config.__dict__.copy()
            config_dict.update(opt)
            variations.append(AdvancedGameConfig(**config_dict))
        
        # Random variations for exploration
        for _ in range(5):
            config_dict = base_config.__dict__.copy()
            config_dict['geo_diversity_bonus'] *= random.uniform(1.2, 2.0)
            config_dict['venue_variety_bonus'] *= random.uniform(1.2, 2.0)
            config_dict['churn_probability_grinder'] *= random.uniform(0.3, 1.0)
            config_dict['pack_price_points'] *= random.uniform(0.7, 1.5)
            variations.append(AdvancedGameConfig(**config_dict))
        
        return variations
    
    def generate_casual_optimizations(self, base_config: AdvancedGameConfig) -> List[AdvancedGameConfig]:
        """Generate parameter variations optimized for casual social engagement"""
        variations = []
        
        # Base configuration
        variations.append(base_config)
        
        # Casual-specific optimizations
        casual_optimizations = [
            # Enhanced social mechanics
            {'social_sneeze_bonus': 4.0, 'social_sneeze_cap': 2},
            {'social_sneeze_bonus': 5.0, 'social_sneeze_cap': 3},
            {'social_sneeze_bonus': 6.0, 'social_sneeze_cap': 4},
            
            # Better new player experience
            {'new_player_bonus_multiplier': 2.5, 'new_player_free_packs': 2},
            {'new_player_bonus_multiplier': 3.0, 'new_player_free_packs': 3},
            {'new_player_bonus_multiplier': 3.5, 'new_player_free_packs': 4},
            
            # Lower casual churn
            {'churn_probability_casual': 0.001},
            {'churn_probability_casual': 0.0015},
            {'churn_probability_casual': 0.0008},
            
            # More frequent events
            {'event_frequency_days': 20, 'event_duration_days': 10},
            {'event_frequency_days': 15, 'event_duration_days': 12},
            {'event_frequency_days': 25, 'event_duration_days': 8},
            
            # Better engagement bonuses
            {'streak_bonus_multiplier': 2.0, 'comeback_bonus_multiplier': 2.5},
            {'streak_bonus_multiplier': 2.5, 'comeback_bonus_multiplier': 3.0},
        ]
        
        for opt in casual_optimizations:
            config_dict = base_config.__dict__.copy()
            config_dict.update(opt)
            variations.append(AdvancedGameConfig(**config_dict))
        
        # Random variations for exploration
        for _ in range(5):
            config_dict = base_config.__dict__.copy()
            config_dict['social_sneeze_bonus'] *= random.uniform(1.2, 2.0)
            config_dict['new_player_bonus_multiplier'] *= random.uniform(1.2, 2.0)
            config_dict['churn_probability_casual'] *= random.uniform(0.3, 1.0)
            config_dict['event_frequency_days'] = int(config_dict['event_frequency_days'] * random.uniform(0.7, 1.5))
            variations.append(AdvancedGameConfig(**config_dict))
        
        return variations
    
    def run_single_simulation(self, config: AdvancedGameConfig, days: int, 
                            player_type_focus: str = None) -> Optional[Dict[str, Any]]:
        """Run a single simulation and return results"""
        try:
            simulator = AdvancedFYNDRSimulator(config)
            simulator.run_simulation(days)
            summary = simulator.get_economy_summary()
            
            # Calculate player-type specific scores
            whale_score = self.calculate_whale_score(summary)
            grinder_score = self.calculate_grinder_score(summary)
            casual_score = self.calculate_casual_score(summary)
            
            # Calculate overall score (same as V1 for consistency)
            overall_score = (whale_score * 0.4) + (grinder_score * 0.35) + (casual_score * 0.25)
            
            # Scale scores to match V1 ranges (V1 scores were ~300-400 range)
            whale_score *= 10
            grinder_score *= 10  
            casual_score *= 10
            overall_score *= 10
            
            result = {
                'config': config.__dict__,
                'summary': summary,
                'whale_score': whale_score,
                'grinder_score': grinder_score,
                'casual_score': casual_score,
                'overall_score': overall_score,
                'revenue': summary.get('total_revenue', 0),
                'userbase': summary.get('total_players', 0),
                'player_type_focus': player_type_focus
            }
            
            # Store result for visualization
            self.all_simulation_results.append(result)
            
            return result
            
        except Exception as e:
            print(f"Error in simulation: {e}")
            return None
    
    def run_phase_1_whale_optimization(self, days: int = 90, base_config: AdvancedGameConfig = None) -> PlayerTypeResult:
        """Phase 1: Optimize parameters for whales only"""
        print("=" * 80)
        print("PHASE 1: WHALE INVESTMENT OPTIMIZATION")
        print("=" * 80)
        print("Finding optimal parameters for whale investment and retention...")
        print()
        
        if base_config is None:
            base_config = self.create_base_config()
        variations = self.generate_whale_optimizations(base_config)
        
        best_score = 0
        best_result = None
        
        print(f"Testing {len(variations)} whale-optimized configurations...")
        
        for i, config in enumerate(variations):
            progress = (i + 1) / len(variations) * 100
            print(f"  Running whale simulation {i+1}/{len(variations)} ({progress:.1f}%)...", end=" ")
            
            result = self.run_single_simulation(config, days)
            if result:
                whale_score = result['whale_score']
                print(f"Whale Score: {whale_score:.2f}")
                
                if whale_score > best_score:
                    best_score = whale_score
                    best_result = result
            else:
                print("Failed")
        
        if best_result:
            whale_result = PlayerTypeResult(
                player_type="whale",
                config=best_result['config'],
                summary=best_result['summary'],
                target_score=best_result['whale_score'],
                overall_score=best_result['overall_score'],
                revenue=best_result['revenue'],
                userbase=best_result['userbase']
            )
            self.whale_result = whale_result
            
            print(f"\nBest Whale Configuration Found:")
            print(f"  Whale Score: {whale_result.target_score:.2f}")
            print(f"  Overall Score: {whale_result.overall_score:.2f}")
            print(f"  Revenue: ${whale_result.revenue:.2f}")
            print(f"  Stickers Placed: {whale_result.summary.get('whale_purchases', 0)}")
            print(f"  Userbase: {whale_result.userbase}")
            print(f"  Key Parameters:")
            print(f"    Owner Base Points: {whale_result.config.get('owner_base_points', 0):.2f}")
            print(f"    Pack Price: ${whale_result.config.get('pack_price_dollars', 0):.2f}")
            print(f"    Whale Churn: {whale_result.config.get('churn_probability_whale', 0):.4f}")
            
            return whale_result
        else:
            print("No successful whale simulations!")
            return None
    
    def run_phase_2_grinder_optimization(self, days: int = 90, base_config: AdvancedGameConfig = None) -> PlayerTypeResult:
        """Phase 2: Optimize parameters for grinders only"""
        print("\n" + "=" * 80)
        print("PHASE 2: GRINDER LEVELING OPTIMIZATION")
        print("=" * 80)
        print("Finding optimal parameters for grinder leveling and engagement...")
        print()
        
        if base_config is None:
            base_config = self.create_base_config()
        variations = self.generate_grinder_optimizations(base_config)
        
        best_score = 0
        best_result = None
        
        print(f"Testing {len(variations)} grinder-optimized configurations...")
        
        for i, config in enumerate(variations):
            progress = (i + 1) / len(variations) * 100
            print(f"  Running grinder simulation {i+1}/{len(variations)} ({progress:.1f}%)...", end=" ")
            
            result = self.run_single_simulation(config, days)
            if result:
                grinder_score = result['grinder_score']
                print(f"Grinder Score: {grinder_score:.2f}")
                
                if grinder_score > best_score:
                    best_score = grinder_score
                    best_result = result
            else:
                print("Failed")
        
        if best_result:
            grinder_result = PlayerTypeResult(
                player_type="grinder",
                config=best_result['config'],
                summary=best_result['summary'],
                target_score=best_result['grinder_score'],
                overall_score=best_result['overall_score'],
                revenue=best_result['revenue'],
                userbase=best_result['userbase']
            )
            self.grinder_result = grinder_result
            
            print(f"\nBest Grinder Configuration Found:")
            print(f"  Grinder Score: {grinder_result.target_score:.2f}")
            print(f"  Overall Score: {grinder_result.overall_score:.2f}")
            print(f"  Stickers Placed: {grinder_result.summary.get('grinder_purchases', 0)}")
            print(f"  Userbase: {grinder_result.userbase}")
            print(f"  Key Parameters:")
            print(f"    Geo Diversity Bonus: {grinder_result.config.get('geo_diversity_bonus', 0):.2f}")
            print(f"    Pack Price Points: {grinder_result.config.get('pack_price_points', 0)}")
            print(f"    Grinder Churn: {grinder_result.config.get('churn_probability_grinder', 0):.4f}")
            
            return grinder_result
        else:
            print("No successful grinder simulations!")
            return None
    
    def run_phase_3_casual_optimization(self, days: int = 90, base_config: AdvancedGameConfig = None) -> PlayerTypeResult:
        """Phase 3: Optimize parameters for casual players only"""
        print("\n" + "=" * 80)
        print("PHASE 3: CASUAL SOCIAL OPTIMIZATION")
        print("=" * 80)
        print("Finding optimal parameters for casual social engagement and growth...")
        print()
        
        if base_config is None:
            base_config = self.create_base_config()
        variations = self.generate_casual_optimizations(base_config)
        
        best_score = 0
        best_result = None
        
        print(f"Testing {len(variations)} casual-optimized configurations...")
        
        for i, config in enumerate(variations):
            progress = (i + 1) / len(variations) * 100
            print(f"  Running casual simulation {i+1}/{len(variations)} ({progress:.1f}%)...", end=" ")
            
            result = self.run_single_simulation(config, days)
            if result:
                casual_score = result['casual_score']
                print(f"Casual Score: {casual_score:.2f}")
                
                if casual_score > best_score:
                    best_score = casual_score
                    best_result = result
            else:
                print("Failed")
        
        if best_result:
            casual_result = PlayerTypeResult(
                player_type="casual",
                config=best_result['config'],
                summary=best_result['summary'],
                target_score=best_result['casual_score'],
                overall_score=best_result['overall_score'],
                revenue=best_result['revenue'],
                userbase=best_result['userbase']
            )
            self.casual_result = casual_result
            
            print(f"\nBest Casual Configuration Found:")
            print(f"  Casual Score: {casual_result.target_score:.2f}")
            print(f"  Overall Score: {casual_result.overall_score:.2f}")
            print(f"  Revenue: ${casual_result.revenue:.2f}")
            print(f"  Stickers Placed: {casual_result.summary.get('casual_purchases', 0)}")
            print(f"  Userbase: {casual_result.userbase}")
            print(f"  Key Parameters:")
            print(f"    Social Sneeze Bonus: {casual_result.config.get('social_sneeze_bonus', 0):.2f}")
            print(f"    New Player Bonus: {casual_result.config.get('new_player_bonus_multiplier', 0):.2f}")
            print(f"    Casual Churn: {casual_result.config.get('churn_probability_casual', 0):.4f}")
            
            return casual_result
        else:
            print("No successful casual simulations!")
            return None
    
    def run_phase_4_multiplayer_optimization(self, days: int = 90, base_config: AdvancedGameConfig = None) -> MultiPlayerResult:
        """Phase 4: Multi-player optimization combining best individual results"""
        print("\n" + "=" * 80)
        print("PHASE 4: MULTI-PLAYER OPTIMIZATION")
        print("=" * 80)
        print("Testing combinations of best individual player type parameters...")
        print()
        
        if not all([self.whale_result, self.grinder_result, self.casual_result]):
            print("Error: Need results from all previous phases!")
            return None
        
        # Create hybrid configurations combining best individual parameters
        hybrid_configs = []
        
        # Configuration 1: Whale-focused hybrid
        whale_hybrid = self.create_base_config()
        whale_hybrid.__dict__.update(self.whale_result.config)
        whale_hybrid.__dict__.update({
            'geo_diversity_bonus': self.grinder_result.config.get('geo_diversity_bonus', 1.0),
            'social_sneeze_bonus': self.casual_result.config.get('social_sneeze_bonus', 3.0),
        })
        hybrid_configs.append(whale_hybrid)
        
        # Configuration 2: Grinder-focused hybrid
        grinder_hybrid = self.create_base_config()
        grinder_hybrid.__dict__.update(self.grinder_result.config)
        grinder_hybrid.__dict__.update({
            'owner_base_points': self.whale_result.config.get('owner_base_points', 2.0),
            'social_sneeze_bonus': self.casual_result.config.get('social_sneeze_bonus', 3.0),
        })
        hybrid_configs.append(grinder_hybrid)
        
        # Configuration 3: Casual-focused hybrid
        casual_hybrid = self.create_base_config()
        casual_hybrid.__dict__.update(self.casual_result.config)
        casual_hybrid.__dict__.update({
            'owner_base_points': self.whale_result.config.get('owner_base_points', 2.0),
            'geo_diversity_bonus': self.grinder_result.config.get('geo_diversity_bonus', 1.0),
        })
        hybrid_configs.append(casual_hybrid)
        
        # Configuration 4: Balanced hybrid (average of best parameters)
        balanced_hybrid = self.create_base_config()
        balanced_hybrid.__dict__.update({
            'owner_base_points': (self.whale_result.config.get('owner_base_points', 2.0) + 2.0) / 2,
            'geo_diversity_bonus': (self.grinder_result.config.get('geo_diversity_bonus', 1.0) + 1.0) / 2,
            'social_sneeze_bonus': (self.casual_result.config.get('social_sneeze_bonus', 3.0) + 3.0) / 2,
            'pack_price_dollars': (self.whale_result.config.get('pack_price_dollars', 3.0) + 3.0) / 2,
            'pack_price_points': (self.grinder_result.config.get('pack_price_points', 300) + 300) / 2,
            'churn_probability_whale': self.whale_result.config.get('churn_probability_whale', 0.0005),
            'churn_probability_grinder': self.grinder_result.config.get('churn_probability_grinder', 0.0008),
            'churn_probability_casual': self.casual_result.config.get('churn_probability_casual', 0.002),
        })
        hybrid_configs.append(balanced_hybrid)
        
        # Test additional random combinations
        for _ in range(8):
            random_hybrid = self.create_base_config()
            random_hybrid.__dict__.update({
                'owner_base_points': random.uniform(
                    self.whale_result.config.get('owner_base_points', 2.0) * 0.8,
                    self.whale_result.config.get('owner_base_points', 2.0) * 1.2
                ),
                'geo_diversity_bonus': random.uniform(
                    self.grinder_result.config.get('geo_diversity_bonus', 1.0) * 0.8,
                    self.grinder_result.config.get('geo_diversity_bonus', 1.0) * 1.2
                ),
                'social_sneeze_bonus': random.uniform(
                    self.casual_result.config.get('social_sneeze_bonus', 3.0) * 0.8,
                    self.casual_result.config.get('social_sneeze_bonus', 3.0) * 1.2
                ),
            })
            hybrid_configs.append(random_hybrid)
        
        best_score = 0
        best_result = None
        
        print(f"Testing {len(hybrid_configs)} multi-player hybrid configurations...")
        
        for i, config in enumerate(hybrid_configs):
            progress = (i + 1) / len(hybrid_configs) * 100
            print(f"  Running hybrid simulation {i+1}/{len(hybrid_configs)} ({progress:.1f}%)...", end=" ")
            
            result = self.run_single_simulation(config, days)
            if result:
                overall_score = result['overall_score']
                print(f"Overall Score: {overall_score:.2f}")
                
                if overall_score > best_score:
                    best_score = overall_score
                    best_result = result
            else:
                print("Failed")
        
        if best_result:
            multiplayer_result = MultiPlayerResult(
                config=best_result['config'],
                summary=best_result['summary'],
                whale_score=best_result['whale_score'],
                grinder_score=best_result['grinder_score'],
                casual_score=best_result['casual_score'],
                overall_score=best_result['overall_score'],
                revenue=best_result['revenue'],
                userbase=best_result['userbase']
            )
            self.multiplayer_result = multiplayer_result
            
            print(f"\nBest Multi-Player Configuration Found:")
            print(f"  Overall Score: {multiplayer_result.overall_score:.2f}")
            print(f"  Whale Score: {multiplayer_result.whale_score:.2f}")
            print(f"  Grinder Score: {multiplayer_result.grinder_score:.2f}")
            print(f"  Casual Score: {multiplayer_result.casual_score:.2f}")
            print(f"  Revenue: ${multiplayer_result.revenue:.2f}")
            print(f"  Userbase: {multiplayer_result.userbase}")
            
            return multiplayer_result
        else:
            print("No successful multi-player simulations!")
            return None
    
    def run_complete_optimization(self, days: int = 90, iterations: int = 1):
        """Run all four phases of optimization with optional multiple iterations"""
        print("=" * 80)
        print("OKR-OPTIMIZED FYNDR ECONOMY ANALYZER V2")
        print("=" * 80)
        print("Multi-Phase Player-Specific Optimization")
        print("Phase 1: Whale Investment Optimization")
        print("Phase 2: Grinder Leveling Optimization") 
        print("Phase 3: Casual Social Optimization")
        print("Phase 4: Multi-Player Integration")
        print(f"Simulation Days: {days}")
        print(f"Iterations per Phase: {iterations}")
        print()
        
        start_time = time.time()
        
        # Run multiple iterations if requested
        for iteration in range(iterations):
            if iterations > 1:
                print(f"\n{'='*20} ITERATION {iteration + 1}/{iterations} {'='*20}")
            
            # Phase 1: Whale optimization
            # On subsequent iterations, use the best whale config as base
            if iteration > 0 and self.whale_result:
                base_config = AdvancedGameConfig(**self.whale_result.config)
                whale_result = self.run_phase_1_whale_optimization(days, base_config)
            else:
                whale_result = self.run_phase_1_whale_optimization(days)
            
            # Phase 2: Grinder optimization
            # On subsequent iterations, use the best grinder config as base
            if iteration > 0 and self.grinder_result:
                base_config = AdvancedGameConfig(**self.grinder_result.config)
                grinder_result = self.run_phase_2_grinder_optimization(days, base_config)
            else:
                grinder_result = self.run_phase_2_grinder_optimization(days)
            
            # Phase 3: Casual optimization
            # On subsequent iterations, use the best casual config as base
            if iteration > 0 and self.casual_result:
                base_config = AdvancedGameConfig(**self.casual_result.config)
                casual_result = self.run_phase_3_casual_optimization(days, base_config)
            else:
                casual_result = self.run_phase_3_casual_optimization(days)
            
            # Phase 4: Multi-player optimization
            # On subsequent iterations, use the best multiplayer config as base
            if iteration > 0 and self.multiplayer_result:
                base_config = AdvancedGameConfig(**self.multiplayer_result.config)
                multiplayer_result = self.run_phase_4_multiplayer_optimization(days, base_config)
            else:
                multiplayer_result = self.run_phase_4_multiplayer_optimization(days)
        
        end_time = time.time()
        
        # Print final summary
        self.print_final_summary()
        
        print(f"\nOptimization completed in {end_time - start_time:.2f} seconds")
        
        return {
            'whale_result': whale_result,
            'grinder_result': grinder_result,
            'casual_result': casual_result,
            'multiplayer_result': multiplayer_result
        }
    
    def print_final_summary(self):
        """Print comprehensive final analysis"""
        print("\n" + "=" * 80)
        print("FINAL OPTIMIZATION SUMMARY")
        print("=" * 80)
        
        if self.whale_result:
            print(f"\n🐋 WHALE OPTIMIZATION RESULTS:")
            print(f"  Best Whale Score: {self.whale_result.target_score:.2f}")
            print(f"  Revenue: ${self.whale_result.revenue:.2f}")
            print(f"  Stickers Placed: {self.whale_result.summary.get('whale_purchases', 0)}")
            print(f"  Userbase: {self.whale_result.userbase}")
        
        if self.grinder_result:
            print(f"\n⚡ GRINDER OPTIMIZATION RESULTS:")
            print(f"  Best Grinder Score: {self.grinder_result.target_score:.2f}")
            print(f"  Stickers Placed: {self.grinder_result.summary.get('grinder_purchases', 0)}")
            print(f"  Userbase: {self.grinder_result.userbase}")
        
        if self.casual_result:
            print(f"\n👥 CASUAL OPTIMIZATION RESULTS:")
            print(f"  Best Casual Score: {self.casual_result.target_score:.2f}")
            print(f"  Revenue: ${self.casual_result.revenue:.2f}")
            print(f"  Stickers Placed: {self.casual_result.summary.get('casual_purchases', 0)}")
            print(f"  Userbase: {self.casual_result.userbase}")
        
        if self.multiplayer_result:
            print(f"\n🎯 MULTI-PLAYER OPTIMIZATION RESULTS:")
            print(f"  Overall Score: {self.multiplayer_result.overall_score:.2f}")
            print(f"  Whale Score: {self.multiplayer_result.whale_score:.2f}")
            print(f"  Grinder Score: {self.multiplayer_result.grinder_score:.2f}")
            print(f"  Casual Score: {self.multiplayer_result.casual_score:.2f}")
            print(f"  Revenue: ${self.multiplayer_result.revenue:.2f}")
            print(f"  Userbase: {self.multiplayer_result.userbase}")
            
            print(f"\n🎯 OPTIMAL MULTI-PLAYER PARAMETERS:")
            config = self.multiplayer_result.config
            print(f"  Owner Base Points: {config.get('owner_base_points', 0):.2f}")
            print(f"  Scanner Base Points: {config.get('scanner_base_points', 0):.2f}")
            print(f"  Geo Diversity Bonus: {config.get('geo_diversity_bonus', 0):.2f}")
            print(f"  Social Sneeze Bonus: {config.get('social_sneeze_bonus', 0):.2f}")
            print(f"  Pack Price: ${config.get('pack_price_dollars', 0):.2f}")
            print(f"  Pack Price Points: {config.get('pack_price_points', 0)}")
            print(f"  Whale Churn: {config.get('churn_probability_whale', 0):.4f}")
            print(f"  Grinder Churn: {config.get('churn_probability_grinder', 0):.4f}")
            print(f"  Casual Churn: {config.get('churn_probability_casual', 0):.4f}")
    
    def export_results(self, prefix: str = "okr_v2_optimized"):
        """Export all optimization results and generate visualizations"""
        export_data = {
            'optimization_metadata': {
                'method': 'multi_phase_player_specific_optimization',
                'phases': 4,
                'description': 'Phase 1: Whale optimization, Phase 2: Grinder optimization, Phase 3: Casual optimization, Phase 4: Multi-player integration'
            },
            'whale_result': asdict(self.whale_result) if self.whale_result else None,
            'grinder_result': asdict(self.grinder_result) if self.grinder_result else None,
            'casual_result': asdict(self.casual_result) if self.casual_result else None,
            'multiplayer_result': asdict(self.multiplayer_result) if self.multiplayer_result else None,
            'all_simulation_results': self.all_simulation_results
        }
        
        with open(f'{prefix}_results.json', 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Results exported to {prefix}_results.json")
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        try:
            visualization_files = self.visualization_engine.generate_all_visualizations(export_data)
            print(f"Visualizations generated in 'visualizations/' directory:")
            for viz_type, filepath in visualization_files.items():
                print(f"  {viz_type}: {filepath}")
        except Exception as e:
            print(f"Error generating visualizations: {e}")
            print("Continuing without visualizations...")

def main():
    """Main function to run V2 OKR-optimized analysis"""
    parser = argparse.ArgumentParser(description='OKR-Optimized FYNDR Economy Analyzer V2')
    parser.add_argument('--days', type=int, default=90, 
                       help='Number of days to simulate')
    parser.add_argument('--iterations', type=int, default=1, 
                       help='Number of iterations to run (each iteration runs all 4 phases)')
    parser.add_argument('--prefix', type=str, default='okr_v2_optimized', 
                       help='Prefix for output files')
    
    args = parser.parse_args()
    
    print("OKR-Optimized FYNDR Economy Analyzer V2")
    print("=" * 50)
    print("Multi-Phase Player-Specific Optimization")
    print(f"Simulation Days: {args.days}")
    print()
    
    # Create analyzer
    analyzer = OKROptimizedAnalyzerV2()
    
    # Run complete optimization
    results = analyzer.run_complete_optimization(args.days, args.iterations)
    
    # Export results
    analyzer.export_results(args.prefix)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("Use the exported files for implementation planning.")

if __name__ == "__main__":
    main()
