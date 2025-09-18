#!/usr/bin/env python3
"""
FYNDR Life Simulator

A comprehensive, indefinite-running simulator that models the day-to-day
life of the FYNDR game using optimized parameters from the OKR analysis.

Key Features:
- Runs indefinitely with real-time monitoring
- Uses JSON configuration files for easy parameter modification
- Comprehensive logging and visualization
- Real-time statistics and growth tracking
- All game mechanics incorporated with full complexity
- Clear parameter documentation and modification interface

Usage:
    python fyndr_life_simulator.py --config config.json --days 365
    python fyndr_life_simulator.py --config optimized_config.json --days 0  # Run indefinitely
"""

import random
import math
import json
import csv
import time
import argparse
import threading
import signal
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

@dataclass
class LifeSimConfig:
    """Configuration for the FYNDR Life Simulator"""
    
    # === SIMULATION CONTROL ===
    simulation_name: str = "FYNDR Life Sim - Population Mechanics"
    max_days: int = 90  # 0 = run indefinitely
    real_time_speed: float = 10  # 1.0 = real time, 0.1 = 10x faster, 10.0 = 10x slower
    auto_save_interval: int = 270  # Save every N days
    enable_visualization: bool = True
    enable_console_output: bool = True
    
    # === CORE SCORING PARAMETERS ===
    owner_base_points: float = 2.0
    scanner_base_points: float = 1.0
    unique_scanner_bonus: float = 1.0
    
    # === DIMINISHING RETURNS ===
    diminishing_threshold: int = 300000
    diminishing_rates: List[float] = None  # Will be set in __post_init__
    
    # === DIVERSITY BONUSES ===
    geo_diversity_radius: float = 500.0  # meters
    geo_diversity_bonus: float = 2.5
    venue_variety_bonus: float = 2.5
    
    # === SOCIAL MECHANICS ===
    social_sneeze_threshold: int = 3
    social_sneeze_bonus: float = 3.0
    social_sneeze_cap: int = 1
    
    # === LEVELING SYSTEM ===
    points_per_level: int = 200
    max_level: int = 200
    
    # === LINEAR PROGRESSION SYSTEM ===
    use_linear_progression: bool = True  # Enable/disable linear progression curve
    level_base_xp: int = 200  # XP required for level 1
    level_first_increment: int = 25  # XP increase from level 1 → 2
    level_increment_step: int = 34  # How much the increment grows each level (optimized for 9-month completion)
    level_xp_thresholds: List[int] = None  # Will be calculated in __post_init__
    
    # === LEVEL MULTIPLIER SYSTEM ===
    level_multiplier_base: float = 1.0  # Base multiplier for level 1
    level_multiplier_increment: float = 0.05  # Multiplier increase per level
    
    # === LOCALE AND SCANNING BEHAVIOR ===
    locale_size_meters: float = 500.0  # Locale size in meters (500m square)
    sticker_density_per_quarter_sq_mile: int = 500  # Average stickers per 0.25 sq mi
    
    # Player type scanning behavior (percentage of available stickers per day)
    whale_scan_percentage: float = 0.02  # 2% of available stickers per day
    grinder_scan_percentage: float = 0.40  # 40% of available stickers per day
    casual_scan_percentage: float = 0.07  # 7% of available stickers per day
    
    # === MONETIZATION ===
    pack_price_points: int = 300
    pack_price_dollars: float = 3.0
    points_per_dollar: float = 100.0
    wallet_topup_min: float = 5.0
    wallet_topup_max: float = 50.0
    
    
    # === SCANNING MECHANICS ===
    sticker_scan_cooldown_hours: int = 11
    
    # === CHURN AND RETENTION ===
    churn_probability_base: float = 0.001
    churn_probability_whale: float = 0.0005
    churn_probability_grinder: float = 0.0008
    churn_probability_casual: float = 0.002
    
    # === BONUS SYSTEMS ===
    streak_bonus_days: int = 7
    streak_bonus_multiplier: float = 1.5
    comeback_bonus_days: int = 3
    comeback_bonus_multiplier: float = 2.0
    
    # === NEW PLAYER ONBOARDING ===
    new_player_bonus_days: int = 7
    new_player_bonus_multiplier: float = 2.0
    new_player_free_packs: int = 0
    
    # === EVENTS ===
    event_frequency_days: int = 30
    event_duration_days: int = 7
    event_bonus_multiplier: float = 1.5
    
    # === GROWTH PARAMETERS ===
    new_player_daily_probability: float = 0.1  # 10% chance per day
    new_player_whale_probability: float = 0.05  # 5% of new players are whales
    new_player_grinder_probability: float = 0.25  # 25% of new players are grinders
    new_player_casual_probability: float = 0.70  # 70% of new players are casual
    
    # === POPULATION & SPREAD MECHANICS ===
    # Population variables for modeling game spread in a locale
    total_population: int = 2500  # Total population of the area
    population_density_per_quarter_sq_mile: float = 4000.0  # Population density per quarter square mile
    
    # Viral spread mechanics
    viral_spread_percentage: float = 0.40  # 40% of active players recruit new players
    viral_spread_frequency_days: int = 14  # Every 2 weeks
    viral_spread_cap_percentage: float = 0.40  # Maximum 40% of total population can be players
    
    # Organic growth mechanics
    organic_growth_rate_min: float = 0.002  # 0.2% minimum organic growth per 50 tags per week
    organic_growth_rate_max: float = 0.005  # 0.5% maximum organic growth per 50 tags per week
    organic_growth_tags_threshold: int = 50  # Number of tags required for organic growth calculation
    
    # Player type distribution for new players (overrides individual probabilities when enabled)
    use_population_mechanics: bool = True  # Enable/disable population-based growth
    new_player_type_ratios: Dict[str, float] = None  # Will be set in __post_init__
    
    # === STARTING POPULATION ===
    starting_player_count: int = 1  # Number of players to start the simulation with
    starting_player_type_ratios: Dict[str, float] = None  # Will be set in __post_init__
    
    # === VENUE DIVERSITY ===
    venue_types: List[str] = None  # ["restaurant", "cafe", "shop", "park", "school"]
    venue_type_weights: List[float] = None  # [0.3, 0.2, 0.2, 0.2, 0.1]
    
    def __post_init__(self):
        """Initialize default values for complex fields"""
        if self.diminishing_rates is None:
            self.diminishing_rates = [1.0, 0.6, 0.3]
        if self.venue_types is None:
            self.venue_types = ["restaurant", "cafe", "shop", "park", "school"]
        if self.venue_type_weights is None:
            self.venue_type_weights = [0.3, 0.2, 0.2, 0.2, 0.1]
        if self.new_player_type_ratios is None:
            self.new_player_type_ratios = {
                'whale': 0.05,    # 5% whales
                'grinder': 0.25,  # 25% grinders  
                'casual': 0.70    # 70% casual
            }
        if self.starting_player_type_ratios is None:
            self.starting_player_type_ratios = {
                'whale': 0.05,    # 5% whales
                'grinder': 0.25,  # 25% grinders  
                'casual': 0.70    # 70% casual
            }
        if self.level_xp_thresholds is None:
            self.level_xp_thresholds = self._calculate_xp_thresholds()
    
    def _calculate_xp_thresholds(self) -> List[int]:
        """Calculate XP thresholds for linear progression curve"""
        if not self.use_linear_progression:
            # Use simple fixed XP per level
            return [self.points_per_level * (i + 1) for i in range(self.max_level)]
        
        thresholds = [self.level_base_xp]  # Level 1 threshold
        increment = self.level_first_increment
        current = self.level_base_xp

        for lvl in range(2, self.max_level + 1):
            current += increment
            thresholds.append(current)
            increment += self.level_increment_step  # grow increment linearly

        return thresholds

@dataclass
class Player:
    """Represents a player in the FYNDR game"""
    id: int
    player_type: str  # "whale", "grinder", "casual"
    level: int = 1
    total_points: float = 0.0
    total_xp: int = 0  # Experience points for leveling
    wallet_balance: float = 0.0
    total_spent: float = 0.0
    stickers_placed: int = 0
    stickers_scanned: int = 0
    days_active: int = 0
    days_since_last_scan: int = 0
    streak_days: int = 0
    last_scan_times: Dict[int, int] = None  # sticker_id -> day
    favorite_venues: List[str] = None
    location: Tuple[float, float] = None  # (lat, lng)
    join_day: int = 0
    is_active: bool = True
    churn_day: Optional[int] = None
    
    def __post_init__(self):
        if self.last_scan_times is None:
            self.last_scan_times = {}
        if self.favorite_venues is None:
            self.favorite_venues = []
        if self.location is None:
            # Random location in a 10km x 10km area
            self.location = (random.uniform(0, 0.1), random.uniform(0, 0.1))

@dataclass
class Sticker:
    """Represents a sticker in the game"""
    id: int
    owner_id: int
    venue_type: str
    location: Tuple[float, float]
    points_value: float
    is_active: bool = True
    creation_day: int = 0
    total_scans: int = 0
    unique_scanners: set = None
    
    def __post_init__(self):
        if self.unique_scanners is None:
            self.unique_scanners = set()

@dataclass
class DailyStats:
    """Daily statistics for the simulation"""
    day: int
    total_players: int
    active_players: int
    new_players: int
    churned_players: int
    total_revenue: float
    total_points_earned: float
    total_scans: int
    total_stickers_placed: int
    player_type_counts: Dict[str, int]
    revenue_by_type: Dict[str, float]
    avg_level: float
    retention_rate: float
    growth_rate: float
    
    # === POPULATION & SPREAD METRICS ===
    total_population: int = 100000
    population_density: float = 25000.0
    max_possible_players: int = 40000
    population_penetration_rate: float = 0.0
    viral_recruits_today: int = 0
    organic_new_players_today: int = 0
    population_cap_reached: bool = False

# ============================================================================
# CORE SIMULATOR CLASS
# ============================================================================

class FYNDRLifeSimulator:
    """Main life simulator for FYNDR game"""
    
    def __init__(self, config: LifeSimConfig):
        self.config = config
        self.players: Dict[int, Player] = {}
        self.stickers: Dict[int, Sticker] = {}
        self.daily_stats: List[DailyStats] = []
        self.current_day = 0
        self.running = False
        self.paused = False
        self.next_player_id = 1
        self.next_sticker_id = 1
        
        # Statistics tracking
        self.total_revenue = 0.0
        self.total_points_earned = 0.0
        self.total_scans = 0
        self.total_stickers_placed = 0
        
        # Event tracking
        self.current_event = None
        self.event_start_day = None
        
        # === POPULATION & SPREAD TRACKING ===
        self.viral_recruits_today = 0
        self.organic_new_players_today = 0
        self.max_possible_players = int(self.config.total_population * self.config.viral_spread_cap_percentage)
        
        # Initialize with some starting players
        self._initialize_starting_population()
        
    def _initialize_starting_population(self):
        """Initialize the game with a starting population"""
        # Create initial players using configurable parameters
        for i in range(self.config.starting_player_count):
            player_type = random.choices(
                list(self.config.starting_player_type_ratios.keys()),
                weights=list(self.config.starting_player_type_ratios.values())
            )[0]
            
            player = Player(
                id=self.next_player_id,
                player_type=player_type,
                join_day=0,
                location=(random.uniform(0, 0.1), random.uniform(0, 0.1))
            )
            
            # Give new players some starting points and free packs
            player.total_points = 100.0
            if player.player_type == "whale":
                player.wallet_balance = 20.0  # $20 starting balance
                player.total_spent = 20.0
                self.total_revenue += 20.0
            
            self.players[self.next_player_id] = player
            self.next_player_id += 1
        
        # Create some initial stickers
        for _ in range(100):
            self._create_new_sticker()
    
    def _create_new_sticker(self):
        """Create a new sticker in the game"""
        if not self.players:
            return
            
        # Choose a random active player as owner
        active_players = [p for p in self.players.values() if p.is_active]
        if not active_players:
            return
            
        owner = random.choice(active_players)
        venue_type = random.choices(
            self.config.venue_types,
            weights=self.config.venue_type_weights
        )[0]
        
        # Place sticker near owner's location
        location = (
            owner.location[0] + random.uniform(-0.01, 0.01),
            owner.location[1] + random.uniform(-0.01, 0.01)
        )
        
        sticker = Sticker(
            id=self.next_sticker_id,
            owner_id=owner.id,
            venue_type=venue_type,
            location=location,
            points_value=self.config.owner_base_points,
            creation_day=self.current_day
        )
        
        self.stickers[self.next_sticker_id] = sticker
        self.next_sticker_id += 1
        self.total_stickers_placed += 1
        
        # Award points to owner
        owner.total_points += self.config.owner_base_points
        owner.stickers_placed += 1
        self.total_points_earned += self.config.owner_base_points
    
    def _simulate_player_behavior(self, player: Player):
        """Simulate a single player's behavior for one day"""
        if not player.is_active:
            return
            
        # Check for churn
        if self._check_player_churn(player):
            player.is_active = False
            player.churn_day = self.current_day
            return
        
        # Update player stats
        player.days_active += 1
        player.days_since_last_scan += 1
        
        # Check for streak bonus
        if player.days_since_last_scan == 0:  # Player scanned today
            player.streak_days += 1
        else:
            player.streak_days = 0
        
        # Simulate player actions based on type
        if player.player_type == "whale":
            self._simulate_whale_behavior(player)
        elif player.player_type == "grinder":
            self._simulate_grinder_behavior(player)
        else:  # casual
            self._simulate_casual_behavior(player)
    
    def _check_player_churn(self, player: Player) -> bool:
        """Check if a player should churn based on their type and activity"""
        base_churn = self.config.churn_probability_base
        
        if player.player_type == "whale":
            churn_prob = self.config.churn_probability_whale
        elif player.player_type == "grinder":
            churn_prob = self.config.churn_probability_grinder
        else:  # casual
            churn_prob = self.config.churn_probability_casual
        
        # Increase churn probability if player hasn't been active
        if player.days_since_last_scan > 7:
            churn_prob *= 2.0
        if player.days_since_last_scan > 14:
            churn_prob *= 3.0
            
        return random.random() < churn_prob
    
    def _simulate_whale_behavior(self, player: Player):
        """Simulate whale player behavior"""
        # Whales are more likely to spend money
        if random.random() < 0.3:  # 30% chance to spend money
            spend_amount = random.uniform(
                self.config.wallet_topup_min,
                self.config.wallet_topup_max
            )
            player.wallet_balance += spend_amount
            player.total_spent += spend_amount
            self.total_revenue += spend_amount
        
        # Whales place more stickers
        if random.random() < 0.8:  # 80% chance to place sticker
            self._create_new_sticker()
        
        # Whales scan more frequently
        if random.random() < 0.9:  # 90% chance to scan
            self._simulate_scan_behavior(player)
    
    def _simulate_grinder_behavior(self, player: Player):
        """Simulate grinder player behavior"""
        # Grinders are very active but don't spend money
        if random.random() < 0.7:  # 70% chance to place sticker
            self._create_new_sticker()
        
        if random.random() < 0.8:  # 80% chance to scan
            self._simulate_scan_behavior(player)
    
    def _simulate_casual_behavior(self, player: Player):
        """Simulate casual player behavior"""
        # Casual players are less active but more social
        if random.random() < 0.4:  # 40% chance to place sticker
            self._create_new_sticker()
        
        if random.random() < 0.5:  # 50% chance to scan
            self._simulate_scan_behavior(player)
        
        # Casual players might spend occasionally
        if random.random() < 0.1:  # 10% chance to spend
            spend_amount = random.uniform(5.0, 15.0)
            player.wallet_balance += spend_amount
            player.total_spent += spend_amount
            self.total_revenue += spend_amount
    
    def _simulate_scan_behavior(self, player: Player):
        """Simulate a player scanning stickers"""
        # Find available stickers (not on cooldown)
        available_stickers = []
        for sticker in self.stickers.values():
            if not sticker.is_active:
                continue
            if sticker.id in player.last_scan_times:
                days_since_scan = self.current_day - player.last_scan_times[sticker.id]
                if days_since_scan < (self.config.sticker_scan_cooldown_hours / 24):
                    continue
            available_stickers.append(sticker)
        
        if not available_stickers:
            return
        
        # Choose a sticker to scan
        sticker = random.choice(available_stickers)
        
        # Calculate points earned
        points = self._calculate_scan_points(player, sticker)
        
        # Award points and XP
        player.total_points += points
        player.total_xp += int(points)  # Convert points to XP
        player.stickers_scanned += 1
        player.days_since_last_scan = 0
        player.last_scan_times[sticker.id] = self.current_day
        
        # Check for level up
        self._check_level_up(player)
        
        # Update sticker stats
        sticker.total_scans += 1
        sticker.unique_scanners.add(player.id)
        
        self.total_scans += 1
        self.total_points_earned += points
    
    def _calculate_scan_points(self, player: Player, sticker: Sticker) -> float:
        """Calculate points earned from scanning a sticker"""
        base_points = self.config.scanner_base_points
        
        # Apply level multiplier (dynamic calculation for all levels)
        # Configurable base multiplier and increment per level
        level_mult = self.config.level_multiplier_base + ((player.level - 1) * self.config.level_multiplier_increment)
        
        base_points *= level_mult
        
        # Apply diversity bonuses
        diversity_bonus = self._calculate_diversity_bonus(player, sticker)
        base_points *= diversity_bonus
        
        # Apply social sneeze bonus
        social_bonus = self._calculate_social_bonus(player, sticker)
        base_points *= social_bonus
        
        # Apply event bonus
        if self.current_event:
            base_points *= self.config.event_bonus_multiplier
        
        # Apply new player bonus
        if self.current_day - player.join_day <= self.config.new_player_bonus_days:
            base_points *= self.config.new_player_bonus_multiplier
        
        # Apply streak bonus
        if player.streak_days >= self.config.streak_bonus_days:
            base_points *= self.config.streak_bonus_multiplier
        
        # Apply comeback bonus
        if player.days_since_last_scan >= self.config.comeback_bonus_days:
            base_points *= self.config.comeback_bonus_multiplier
        
        return base_points
    
    def _check_level_up(self, player: Player):
        """Check if player should level up and handle the level up process"""
        if player.level >= self.config.max_level:
            return  # Already at max level
        
        # Get XP threshold for next level
        next_level_xp = self.config.level_xp_thresholds[player.level - 1]  # 0-indexed
        
        if player.total_xp >= next_level_xp:
            # Level up!
            player.level += 1
            if self.config.enable_console_output:
                print(f"🎉 Player {player.id} ({player.player_type}) leveled up to level {player.level}!")
    
    def _calculate_diversity_bonus(self, player: Player, sticker: Sticker) -> float:
        """Calculate diversity bonus for scanning a sticker"""
        bonus = 1.0
        
        # Geographic diversity
        if self._is_geographically_diverse(player, sticker):
            bonus += self.config.geo_diversity_bonus
        
        # Venue variety
        if sticker.venue_type not in player.favorite_venues:
            bonus += self.config.venue_variety_bonus
            if len(player.favorite_venues) < 3:
                player.favorite_venues.append(sticker.venue_type)
        
        return bonus
    
    def _is_geographically_diverse(self, player: Player, sticker: Sticker) -> bool:
        """Check if sticker is geographically diverse from player's recent scans"""
        # Simple distance calculation (in degrees)
        distance = math.sqrt(
            (player.location[0] - sticker.location[0])**2 +
            (player.location[1] - sticker.location[1])**2
        )
        
        # Convert to meters (rough approximation)
        distance_meters = distance * 111000  # 1 degree ≈ 111km
        
        return distance_meters > self.config.geo_diversity_radius
    
    def _calculate_social_bonus(self, player: Player, sticker: Sticker) -> float:
        """Calculate social sneeze bonus"""
        if sticker.total_scans >= self.config.social_sneeze_threshold:
            return 1.0 + self.config.social_sneeze_bonus
        return 1.0
    
    def _calculate_daily_scans_for_player(self, player: Player) -> int:
        """Calculate how many scans a player should do per day based on their type and locale"""
        # Calculate available stickers in the locale
        # Locale is 500m square = 0.25 sq km = 0.096 sq mi
        # Convert to quarter square miles: 0.096 / 0.25 = 0.384 quarter sq mi
        locale_area_quarter_sq_mi = (self.config.locale_size_meters / 1000) ** 2 / 0.25  # Convert to quarter sq mi
        
        # Calculate available stickers in locale
        available_stickers = int(locale_area_quarter_sq_mi * self.config.sticker_density_per_quarter_sq_mile)
        
        # Get player type scan percentage
        if player.player_type == "whale":
            scan_percentage = self.config.whale_scan_percentage
        elif player.player_type == "grinder":
            scan_percentage = self.config.grinder_scan_percentage
        else:  # casual
            scan_percentage = self.config.casual_scan_percentage
        
        # Calculate daily scans
        daily_scans = int(available_stickers * scan_percentage)
        
        # Apply some randomness (±20%)
        import random
        variance = random.uniform(0.8, 1.2)
        daily_scans = max(1, int(daily_scans * variance))
        
        return daily_scans
    
    def _add_new_players(self):
        """Add new players to the game using population and spread mechanics"""
        current_players = len([p for p in self.players.values() if p.is_active])
        
        # Check if we've reached the population cap
        if current_players >= self.max_possible_players:
            return
        
        new_players_count = 0
        
        if self.config.use_population_mechanics:
            # Use new population-based growth mechanics
            
            # 1. Viral spread mechanics (40% of active players recruit 1 new player per 2 weeks)
            if self.current_day % self.config.viral_spread_frequency_days == 0:
                active_players = [p for p in self.players.values() if p.is_active]
                recruiting_players = int(len(active_players) * self.config.viral_spread_percentage)
                viral_recruits = min(recruiting_players, self.max_possible_players - current_players)
                new_players_count += viral_recruits
                self.viral_recruits_today = viral_recruits
            
            # 2. Organic growth based on sticker activity (daily calculation)
            total_active_stickers = len([s for s in self.stickers.values() if s.is_active])
            if total_active_stickers >= self.config.organic_growth_tags_threshold:
                # Calculate daily organic growth rate (divide weekly rate by 7)
                sticker_density_factor = min(total_active_stickers / self.config.organic_growth_tags_threshold, 3.0)
                daily_organic_rate = random.uniform(
                    self.config.organic_growth_rate_min / 7,  # Convert weekly to daily
                    self.config.organic_growth_rate_max / 7   # Convert weekly to daily
                ) * sticker_density_factor
                
                # Apply to total population, not just current players
                organic_new_players = int(self.config.total_population * daily_organic_rate)
                organic_new_players = min(organic_new_players, self.max_possible_players - current_players - new_players_count)
                new_players_count += organic_new_players
                self.organic_new_players_today = organic_new_players
            
            # 3. Event boost for both viral and organic growth
            if self._is_event_active():
                new_players_count = int(new_players_count * 2.0)
            
            # Add new players using the configurable player type ratios
            for _ in range(new_players_count):
                player_type = random.choices(
                    list(self.config.new_player_type_ratios.keys()),
                    weights=list(self.config.new_player_type_ratios.values())
                )[0]
                self._create_new_player(player_type)
        else:
            # Use legacy growth mechanics
            if random.random() < self.config.new_player_daily_probability:
                player_type = random.choices(
                    ["whale", "grinder", "casual"],
                    weights=[
                        self.config.new_player_whale_probability,
                        self.config.new_player_grinder_probability,
                        self.config.new_player_casual_probability
                    ]
                )[0]
                self._create_new_player(player_type)
    
    def _create_new_player(self, player_type: str):
        """Create a new player with the specified type"""
        player = Player(
            id=self.next_player_id,
            player_type=player_type,
            join_day=self.current_day,
            location=(random.uniform(0, 0.1), random.uniform(0, 0.1))
        )
        
        # Give new players some starting points and free packs
        player.total_points = 100.0
        if player.player_type == "whale":
            player.wallet_balance = 20.0  # $20 starting balance
            player.total_spent = 20.0
            self.total_revenue += 20.0
        
        self.players[self.next_player_id] = player
        self.next_player_id += 1
    
    def _is_event_active(self) -> bool:
        """Check if a seasonal event is currently active"""
        if self.current_event is not None:
            return True
        return False
    
    def _update_events(self):
        """Update special events"""
        if self.current_event is None:
            if random.random() < (1.0 / self.config.event_frequency_days):
                self.current_event = "special_event"
                self.event_start_day = self.current_day
        else:
            if self.current_day - self.event_start_day >= self.config.event_duration_days:
                self.current_event = None
                self.event_start_day = None
    
    def _calculate_daily_stats(self) -> DailyStats:
        """Calculate daily statistics"""
        active_players = [p for p in self.players.values() if p.is_active]
        new_players_today = len([p for p in self.players.values() if p.join_day == self.current_day])
        churned_today = len([p for p in self.players.values() if p.churn_day == self.current_day])
        
        player_type_counts = Counter(p.player_type for p in active_players)
        revenue_by_type = defaultdict(float)
        
        for player in active_players:
            if player.total_spent > 0:
                revenue_by_type[player.player_type] += player.total_spent
        
        total_players_ever = len(self.players)
        retention_rate = len(active_players) / total_players_ever if total_players_ever > 0 else 0
        
        growth_rate = (new_players_today - churned_today) / len(active_players) if active_players else 0
        
        avg_level = statistics.mean([p.level for p in active_players]) if active_players else 0
        
        return DailyStats(
            day=self.current_day,
            total_players=len(active_players),
            active_players=len(active_players),
            new_players=new_players_today,
            churned_players=churned_today,
            total_revenue=self.total_revenue,
            total_points_earned=self.total_points_earned,
            total_scans=self.total_scans,
            total_stickers_placed=self.total_stickers_placed,
            player_type_counts=dict(player_type_counts),
            revenue_by_type=dict(revenue_by_type),
            avg_level=avg_level,
            retention_rate=retention_rate,
            growth_rate=growth_rate,
            
            # === POPULATION & SPREAD METRICS ===
            total_population=self.config.total_population,
            population_density=self.config.population_density_per_quarter_sq_mile,
            max_possible_players=self.max_possible_players,
            population_penetration_rate=len(active_players) / self.config.total_population,
            viral_recruits_today=self.viral_recruits_today,
            organic_new_players_today=self.organic_new_players_today,
            population_cap_reached=len(active_players) >= self.max_possible_players
        )
    
    def run_day(self):
        """Run one day of simulation"""
        self.current_day += 1
        
        # Reset daily tracking variables
        self.viral_recruits_today = 0
        self.organic_new_players_today = 0
        
        # Update events
        self._update_events()
        
        # Add new players
        self._add_new_players()
        
        # Simulate each active player
        for player in list(self.players.values()):
            self._simulate_player_behavior(player)
        
        # Calculate and store daily stats
        daily_stats = self._calculate_daily_stats()
        self.daily_stats.append(daily_stats)
        
        # Clean up inactive stickers (optional)
        self._cleanup_inactive_stickers()
        
        return daily_stats
    
    def _cleanup_inactive_stickers(self):
        """Remove stickers from inactive players (optional cleanup)"""
        inactive_player_ids = {p.id for p in self.players.values() if not p.is_active}
        stickers_to_remove = [
            s.id for s in self.stickers.values() 
            if s.owner_id in inactive_player_ids
        ]
        
        for sticker_id in stickers_to_remove:
            del self.stickers[sticker_id]
    
    def run_simulation(self, max_days: int = 0):
        """Run the simulation for specified days (0 = indefinitely)"""
        self.running = True
        self.paused = False
        
        print(f"Starting FYNDR Life Simulation: {self.config.simulation_name}")
        print(f"Max days: {'Unlimited' if max_days == 0 else max_days}")
        print(f"Real-time speed: {self.config.real_time_speed}x")
        print("=" * 60)
        
        try:
            while self.running and (max_days == 0 or self.current_day < max_days):
                if not self.paused:
                    daily_stats = self.run_day()
                    
                    if self.config.enable_console_output:
                        self._print_daily_summary(daily_stats)
                    
                    # Auto-save
                    if self.current_day % self.config.auto_save_interval == 0:
                        self.save_simulation_state()
                
                # Real-time delay
                if self.config.real_time_speed > 0:
                    time.sleep(1.0 / self.config.real_time_speed)
                    
        except KeyboardInterrupt:
            print("\nSimulation paused. Press Ctrl+C again to exit.")
            self.paused = True
            self.running = False
    
    def _print_daily_summary(self, stats: DailyStats):
        """Print daily summary to console"""
        print(f"Day {stats.day:3d} | "
              f"Players: {stats.active_players:4d} | "
              f"Revenue: ${stats.total_revenue:8.2f} | "
              f"Scans: {stats.total_scans:5d} | "
              f"Stickers: {stats.total_stickers_placed:4d} | "
              f"Retention: {stats.retention_rate:.1%} | "
              f"Growth: {stats.growth_rate:+.1%}")
    
    def save_simulation_state(self, filename: str = None):
        """Save current simulation state to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fyndr_life_sim_{timestamp}.json"
        
        # Convert players to serializable format
        players_data = {}
        for k, v in self.players.items():
            player_dict = asdict(v)
            # Convert last_scan_times to regular dict
            if "last_scan_times" in player_dict:
                player_dict["last_scan_times"] = {str(k): v for k, v in player_dict["last_scan_times"].items()}
            players_data[str(k)] = player_dict
        
        # Convert stickers to serializable format
        stickers_data = {}
        for k, v in self.stickers.items():
            sticker_dict = asdict(v)
            # Convert unique_scanners set to list
            if "unique_scanners" in sticker_dict:
                sticker_dict["unique_scanners"] = list(sticker_dict["unique_scanners"])
            stickers_data[str(k)] = sticker_dict
        
        state = {
            "config": asdict(self.config),
            "current_day": self.current_day,
            "total_revenue": self.total_revenue,
            "total_points_earned": self.total_points_earned,
            "total_scans": self.total_scans,
            "total_stickers_placed": self.total_stickers_placed,
            "players": players_data,
            "stickers": stickers_data,
            "daily_stats": [asdict(s) for s in self.daily_stats]
        }
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"Simulation state saved to {filename}")
    
    def load_simulation_state(self, filename: str):
        """Load simulation state from file"""
        with open(filename, 'r') as f:
            state = json.load(f)
        
        # Restore config
        self.config = LifeSimConfig(**state["config"])
        
        # Restore simulation state
        self.current_day = state["current_day"]
        self.total_revenue = state["total_revenue"]
        self.total_points_earned = state["total_points_earned"]
        self.total_scans = state["total_scans"]
        self.total_stickers_placed = state["total_stickers_placed"]
        
        # Restore players
        self.players = {}
        for k, v in state["players"].items():
            player_data = v.copy()
            # Convert last_scan_times back to int keys
            if "last_scan_times" in player_data:
                player_data["last_scan_times"] = {int(k): v for k, v in player_data["last_scan_times"].items()}
            self.players[int(k)] = Player(**player_data)
        
        # Restore stickers
        self.stickers = {}
        for k, v in state["stickers"].items():
            sticker_data = v.copy()
            # Convert unique_scanners back to set
            if "unique_scanners" in sticker_data:
                sticker_data["unique_scanners"] = set(sticker_data["unique_scanners"])
            self.stickers[int(k)] = Sticker(**sticker_data)
        
        # Restore daily stats
        self.daily_stats = [DailyStats(**s) for s in state["daily_stats"]]
        
        print(f"Simulation state loaded from {filename}")

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

def load_config_from_okr_results(okr_file: str) -> LifeSimConfig:
    """Load configuration from OKR optimization results"""
    with open(okr_file, 'r') as f:
        okr_data = json.load(f)
    
    # Use the best multiplayer configuration
    multiplayer_config = okr_data["multiplayer_result"]["config"]
    
    # Create LifeSimConfig with OKR-optimized parameters
    config = LifeSimConfig(
        simulation_name="FYNDR Life Sim - OKR Optimized",
        owner_base_points=multiplayer_config["owner_base_points"],
        scanner_base_points=multiplayer_config["scanner_base_points"],
        unique_scanner_bonus=multiplayer_config["unique_scanner_bonus"],
        diminishing_threshold=multiplayer_config["diminishing_threshold"],
        diminishing_rates=multiplayer_config["diminishing_rates"],
        geo_diversity_radius=multiplayer_config["geo_diversity_radius"],
        geo_diversity_bonus=multiplayer_config["geo_diversity_bonus"],
        venue_variety_bonus=multiplayer_config["venue_variety_bonus"],
        social_sneeze_threshold=multiplayer_config["social_sneeze_threshold"],
        social_sneeze_bonus=multiplayer_config["social_sneeze_bonus"],
        social_sneeze_cap=multiplayer_config["social_sneeze_cap"],
        points_per_level=multiplayer_config["points_per_level"],
        max_level=multiplayer_config["max_level"],
        pack_price_points=multiplayer_config["pack_price_points"],
        pack_price_dollars=multiplayer_config["pack_price_dollars"],
        points_per_dollar=multiplayer_config["points_per_dollar"],
        wallet_topup_min=multiplayer_config["wallet_topup_min"],
        wallet_topup_max=multiplayer_config["wallet_topup_max"],
        sticker_scan_cooldown_hours=multiplayer_config["sticker_scan_cooldown_hours"],
        churn_probability_base=multiplayer_config["churn_probability_base"],
        churn_probability_whale=multiplayer_config["churn_probability_whale"],
        churn_probability_grinder=multiplayer_config["churn_probability_grinder"],
        churn_probability_casual=multiplayer_config["churn_probability_casual"],
        streak_bonus_days=multiplayer_config["streak_bonus_days"],
        streak_bonus_multiplier=multiplayer_config["streak_bonus_multiplier"],
        comeback_bonus_days=multiplayer_config["comeback_bonus_days"],
        comeback_bonus_multiplier=multiplayer_config["comeback_bonus_multiplier"],
        new_player_bonus_days=multiplayer_config["new_player_bonus_days"],
        new_player_bonus_multiplier=multiplayer_config["new_player_bonus_multiplier"],
        new_player_free_packs=multiplayer_config["new_player_free_packs"],
        event_frequency_days=multiplayer_config["event_frequency_days"],
        event_duration_days=multiplayer_config["event_duration_days"],
        event_bonus_multiplier=multiplayer_config["event_bonus_multiplier"]
    )
    
    return config

def save_config_template(filename: str = "fyndr_life_config_template.json"):
    """Save a configuration template file"""
    config = LifeSimConfig()
    with open(filename, 'w') as f:
        json.dump(asdict(config), f, indent=2)
    print(f"Configuration template saved to {filename}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to run the life simulator"""
    parser = argparse.ArgumentParser(description='FYNDR Life Simulator')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--okr-results', type=str, help='OKR optimization results file')
    parser.add_argument('--days', type=int, help='Number of days to simulate (0 = unlimited)')
    parser.add_argument('--speed', type=float, help='Simulation speed multiplier')
    parser.add_argument('--template', action='store_true', help='Generate configuration template')
    parser.add_argument('--load-state', type=str, help='Load existing simulation state')
    
    args = parser.parse_args()
    
    if args.template:
        save_config_template()
        return
    
    # Load configuration
    if args.okr_results:
        print(f"Loading configuration from OKR results: {args.okr_results}")
        config = load_config_from_okr_results(args.okr_results)
    elif args.config:
        print(f"Loading configuration from: {args.config}")
        with open(args.config, 'r') as f:
            config_data = json.load(f)
        config = LifeSimConfig(**config_data)
    else:
        print("Using default configuration")
        config = LifeSimConfig()
    
    # Override speed if specified
    if args.speed is not None:
        config.real_time_speed = args.speed
    
    # Create and run simulator
    simulator = FYNDRLifeSimulator(config)
    
    # Load existing state if specified
    if args.load_state:
        simulator.load_simulation_state(args.load_state)
    
    # Run simulation
    try:
        days_to_run = args.days if args.days is not None else config.max_days
        simulator.run_simulation(days_to_run)
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    finally:
        # Save final state
        simulator.save_simulation_state()
        print("Simulation completed")

if __name__ == "__main__":
    main()
