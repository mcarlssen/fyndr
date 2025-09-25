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
    max_days: int = 270  # 0 = run indefinitely
    real_time_speed: float = 100  # 1.0 = real time, 0.1 = 10x faster, 10.0 = 10x slower
    auto_save_interval: int = 271  # Save every N days
    enable_visualization: bool = True
    enable_console_output: bool = True
    auto_analyze_on_completion: bool = True  # Automatically run analysis when simulation completes
    
    # === CORE SCORING PARAMETERS ===
    owner_base_points: float = 2.0
    scanner_base_points: float = 1.0
    unique_scanner_bonus: float = 1.0
    
    # === DIVERSITY BONUSES ===
    geo_diversity_radius: float = 500.0  # meters
    geo_diversity_bonus: float = 2.5
    venue_variety_bonus: float = 2.5
    
    # === SOCIAL MECHANICS ===
    social_sneeze_threshold: int = 5  # Scans needed to trigger sneeze mode
    social_sneeze_bonus: float = 2.5  # Point multiplier during sneeze mode
    social_sneeze_duration_hours: float = 3.0  # How long sneeze mode lasts (hours)
    social_sneeze_cap: int = 1  # Maximum social sneeze bonuses per day (deprecated with sneeze mode)
    
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
    locale_size_meters: float = 804.5  # Locale size in meters (804.5m square = 1 quarter sq mi)
    sticker_density_per_quarter_sq_mile: int = 500  # Average stickers per 0.25 sq mi
    
    # === PLAYER MOVEMENT PATTERNS ===
    enable_movement_patterns: bool = True  # Enable realistic player movement
    max_scan_distance_meters: float = 100.0  # Maximum distance to scan stickers
    travel_time_per_100m_minutes: float = 2.0  # Travel time per 100 meters (walking speed)
    daily_routine_variance: float = 0.3  # Random variance in daily routines (30%)
    
    # === SOCIAL HUB MECHANICS ===
    enable_social_hubs: bool = True  # Enable social hub mechanics
    social_hub_radius_meters: float = 50.0  # Radius of social hub influence
    social_hub_scan_bonus: float = 1.5  # Bonus multiplier for scanning in social hubs
    social_hub_placement_bonus: float = 2.0  # Bonus multiplier for placing in social hubs
    social_hub_attraction_radius: float = 200.0  # How far players are drawn to social hubs
    
    # Player type scanning behavior (percentage of available stickers per day)
    whale_scan_percentage: float = 0.02  # 2% of available stickers per day
    grinder_scan_percentage: float = 0.40  # 40% of available stickers per day
    casual_scan_percentage: float = 0.07  # 7% of available stickers per day
    
    # === STICKER DENSITY LIMITS ===
    sticker_placement_cooldown_days: int = 1  # Minimum days between sticker placements per player
    
    # === REALISTIC DENSITY SIMULATION ===
    enable_realistic_density: bool = True  # Enable area-specific density limits
    campus_building_density: int = 1000  # High density in campus buildings
    campus_quad_density: int = 200  # Medium density in open areas
    campus_perimeter_density: int = 50  # Low density on campus edges
    social_hub_density: int = 1500  # Very high density in social hubs
    
    # === MONETIZATION ===
    pack_price_points: int = 750
    pack_price_dollars: float = 3.0
    points_per_dollar: float = 250.0
    wallet_topup_min: float = 6.0
    wallet_topup_max: float = 60.0
    
    # === PURCHASING BEHAVIOR ===
    # Whale purchasing behavior
    whale_purchase_probability: float = 0.083  # 8% chance to spend money daily
    whale_purchase_min: float = 3.0  # Minimum purchase amount
    whale_purchase_max: float = 9.0  # Maximum purchase amount
    
    # Casual purchasing behavior  
    casual_purchase_probability: float = 0.00033  # 1% chance per month to spend money
    casual_purchase_min: float = 3.0  # Minimum purchase amount
    casual_purchase_max: float = 3.0  # Maximum purchase amount
    
    # Grinder purchasing behavior (points-based, level-up triggered)
    grinder_reinvest_on_levelup: bool = True  # Grinders reinvest all points when leveling up
    grinder_reinvest_percentage: float = 1.0  # 100% of points reinvested on level up
    
    # === SCANNING MECHANICS ===
    sticker_scan_cooldown_hours: int = 11
    
    # === CHURN AND RETENTION ===
    churn_probability_base: float = 0.001
    churn_probability_whale: float = 0.0005
    churn_probability_grinder: float = 0.0008
    churn_probability_casual: float = 0.002
    
    # === BONUS SYSTEMS ===
    # Streak bonus: Rewards consecutive daily activity (no cooldown, resets if inactive)
    streak_bonus_days: int = 7  # Days of consecutive activity needed
    streak_bonus_multiplier: float = 1.5  # Point multiplier during streak
    
    # Comeback bonus: Rewards players returning after absence (no cooldown, triggers once per return)
    comeback_bonus_days: int = 3  # Days away needed to trigger comeback bonus
    comeback_bonus_multiplier: float = 2.0  # Point multiplier for comeback
    
    # === NEW PLAYER ONBOARDING ===
    # New player bonus: Boosts new players for their first week (no cooldown, one-time per player)
    new_player_bonus_days: int = 7  # Days of bonus for new players
    new_player_bonus_multiplier: float = 2.0  # Point multiplier for new players
    new_player_free_packs: int = 0  # Free sticker packs for new players
    
    # === EVENTS ===
    # Seasonal/special events: Randomly triggered events that boost all point earnings
    event_frequency_days: int = 30  # Average days between events (randomly triggered)
    event_duration_days: int = 7  # How long events last once triggered
    event_bonus_multiplier: float = 1.5  # Point multiplier during events (applies to all scans)
    
    # === GROWTH PARAMETERS ===
    new_player_daily_probability: float = 0.2  # 10% chance per day
    new_player_whale_probability: float = 0.02  # 3% of new players are whales
    new_player_grinder_probability: float = 0.18  # 17% of new players are grinders
    new_player_casual_probability: float = 0.80  # 80% of new players are casual
    
    # === POPULATION & SPREAD MECHANICS ===
    # Population variables for modeling game spread in a locale
    total_population: int = 2500  # Total population of the area
    population_density_per_quarter_sq_mile: float = 4000.0  # Population density per quarter square mile
    
    # Viral spread mechanics
    viral_spread_percentage: float = 0.40  # 20% of active players recruit new players
    viral_spread_frequency_min_days: int = 10  # Minimum days between viral spread events
    viral_spread_frequency_max_days: int = 18  # Maximum days between viral spread events
    viral_spread_cap_percentage: float = 0.40  # Maximum 40% of total population can be players
    
    # Organic growth mechanics
    organic_growth_rate_min: float = 0.002  # 0.2% minimum organic growth per 50 tags per week
    organic_growth_rate_max: float = 0.005  # 0.5% maximum organic growth per 50 tags per week
    organic_growth_tags_threshold: int = 50  # Number of tags required for organic growth calculation
    organic_growth_area_radius_meters: float = 20.0  # Radius in meters for area-bounded organic growth
    
    # Player type distribution for new players (overrides individual probabilities when enabled)
    use_population_mechanics: bool = True  # Enable/disable population-based growth
    new_player_type_ratios: Dict[str, float] = None  # Will be set in __post_init__
    
    # === STARTING POPULATION ===
    starting_player_count: int = 5  # Number of players to start the simulation with
    starting_player_type_ratios: Dict[str, float] = None  # Will be set in __post_init__
    
    # === VENUE DIVERSITY ===
    venue_types: List[str] = None  # ["restaurant", "cafe", "shop", "park", "school"]
    venue_type_weights: List[float] = None  # [0.3, 0.2, 0.2, 0.2, 0.1]
    
    def __post_init__(self):
        """Initialize default values for complex fields"""
        if self.venue_types is None:
            self.venue_types = ["restaurant", "cafe", "shop", "park", "school"]
        if self.venue_type_weights is None:
            self.venue_type_weights = [0.3, 0.2, 0.2, 0.2, 0.1]
        if self.new_player_type_ratios is None:
            self.new_player_type_ratios = {
                'whale': 0.02,    # 3% whales
                'grinder': 0.18,  # 17% grinders  
                'casual': 0.80    # 80% casual
            }
        if self.starting_player_type_ratios is None:
            self.starting_player_type_ratios = {
                'whale': 0.02,    # 3% whales
                'grinder': 0.18,  # 17% grinders  
                'casual': 0.80    # 80% casual
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
    
    # === MOVEMENT PATTERN TRACKING ===
    home_location: Tuple[float, float] = None  # Player's home/dorm location
    work_location: Tuple[float, float] = None  # Class/office location
    social_hubs: List[Tuple[float, float]] = None  # Favorite social locations
    daily_routine: List[Tuple[float, float]] = None  # Daily commute path
    current_location: Tuple[float, float] = None  # Current position
    last_movement_time: float = 0.0  # Time of last movement (hours)
    movement_speed: float = 1.0  # Player's movement speed multiplier
    
    def __post_init__(self):
        if self.last_scan_times is None:
            self.last_scan_times = {}
        if self.favorite_venues is None:
            self.favorite_venues = []
        if self.social_hubs is None:
            self.social_hubs = []
        if self.daily_routine is None:
            self.daily_routine = []
        if self.location is None:
            # Random location in a 10km x 10km area
            self.location = (random.uniform(0, 0.1), random.uniform(0, 0.1))
        if self.current_location is None:
            self.current_location = self.location
        if self.home_location is None:
            self.home_location = self.location

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
    
    # Social sneeze mode tracking
    is_in_sneeze_mode: bool = False
    sneeze_mode_start_time: float = 0.0  # Time when sneeze mode started (in hours from day start)
    sneeze_mode_triggered_at_scans: int = 0  # Scan count when sneeze mode was triggered
    
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
    
    # Sticker density tracking
    current_sticker_density: float = 0.0
    max_stickers_allowed: int = 0
    sticker_density_cap_reached: bool = False
    
    # Social sneeze mode tracking
    stickers_in_sneeze_mode: int = 0
    sneeze_mode_hotspots: List[Tuple[float, float]] = None  # Locations of sneeze mode stickers
    
    # Social hub tracking
    active_social_hubs: int = 0
    social_hub_locations: List[Tuple[float, float]] = None  # Locations of active social hubs
    players_in_social_hubs: int = 0  # Number of players currently in social hubs

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
        self.last_viral_spread_day = None  # Track when viral spread last occurred
        
        # === STICKER DENSITY TRACKING ===
        self.max_stickers_allowed = self._calculate_max_stickers_allowed()
        self.player_last_sticker_day = {}  # Track when each player last placed a sticker
        
        # Initialize social hubs first (needed for sticker creation)
        if self.config.enable_social_hubs:
            self._initialize_social_hubs()
        else:
            self.social_hubs = []  # Initialize as empty list if disabled
        
        # Initialize with some starting players
        self._initialize_starting_population()
    
    def _calculate_max_stickers_allowed(self) -> int:
        """Calculate the maximum number of stickers allowed based on locale area and density limits"""
        # Convert locale size to quarter square miles
        # 804.5m = 0.8045km = 0.8045/1.609 miles = 0.5 miles
        # 0.5 miles square = 0.5^2 = 0.25 sq mi = 1 quarter sq mi
        locale_area_quarter_sq_mi = (self.config.locale_size_meters / 1000 / 1.609) ** 2 / 0.25
        
        # Calculate target sticker count (hard cap, no multiplier)
        max_stickers = int(locale_area_quarter_sq_mi * self.config.sticker_density_per_quarter_sq_mile)
        
        return max_stickers
        
    def _initialize_starting_population(self):
        """Initialize the game with a starting population"""
        # Create initial players using configurable parameters
        for i in range(self.config.starting_player_count):
            player_type = random.choices(
                list(self.config.starting_player_type_ratios.keys()),
                weights=list(self.config.starting_player_type_ratios.values())
            )[0]
            
            # Create player with movement patterns
            home_location = (random.uniform(0, 0.1), random.uniform(0, 0.1))
            work_location = (random.uniform(0, 0.1), random.uniform(0, 0.1))
            
            player = Player(
                id=self.next_player_id,
                player_type=player_type,
                join_day=0,
                location=home_location,
                home_location=home_location,
                work_location=work_location,
                current_location=home_location
            )
            
            # Set up social hubs for the player
            if self.config.enable_social_hubs and hasattr(self, 'social_hubs'):
                player.social_hubs = random.sample(self.social_hubs, min(3, len(self.social_hubs)))
            
            # Set up daily routine
            if self.config.enable_movement_patterns:
                player.daily_routine = [home_location, work_location] + player.social_hubs
                player.last_movement_time = random.uniform(0, 24)  # Random start time
            
            # Give new players some starting points and free packs
            player.total_points = 100.0
            if player.player_type == "whale":
                player.wallet_balance = 20.0  # $20 starting balance
                player.total_spent = 20.0
                self.total_revenue += 20.0
            
            self.players[self.next_player_id] = player
            self.next_player_id += 1
        
        # Create some initial stickers (respecting density limits)
        initial_stickers = min(100, self.max_stickers_allowed)
        for _ in range(initial_stickers):
            self._create_new_sticker()
    
    def _create_new_sticker(self, player: Player = None):
        """Create a new sticker in the game with density limits"""
        # Check player cooldown if specified
        if player and player.id in self.player_last_sticker_day:
            days_since_last_sticker = self.current_day - self.player_last_sticker_day[player.id]
            if days_since_last_sticker < self.config.sticker_placement_cooldown_days:
                return False
        
        if not self.players:
            return False
            
        # Choose a random active player as owner if not specified
        if player is None:
            active_players = [p for p in self.players.values() if p.is_active]
            if not active_players:
                return False
            owner = random.choice(active_players)
        else:
            owner = player
            
        venue_type = random.choices(
            self.config.venue_types,
            weights=self.config.venue_type_weights
        )[0]
        
        # Place sticker near owner's current location
        location = (
            owner.current_location[0] + random.uniform(-0.01, 0.01),
            owner.current_location[1] + random.uniform(-0.01, 0.01)
        )
        
        # Check area-specific density limits
        area_density_limit = self._get_area_density_limit(location)
        nearby_stickers = self._count_stickers_in_area(location, 100)  # 100m radius
        
        if nearby_stickers >= area_density_limit:
            return False
        
        sticker = Sticker(
            id=self.next_sticker_id,
            owner_id=owner.id,
            venue_type=venue_type,
            location=location,
            points_value=self.config.owner_base_points,
            creation_day=self.current_day
        )
        
        # Atomic check and add - if we're at the limit, don't add the sticker
        if len(self.stickers) < self.max_stickers_allowed:
            self.stickers[self.next_sticker_id] = sticker
            self.next_sticker_id += 1
            self.total_stickers_placed += 1
            
            # Track player's last sticker placement
            self.player_last_sticker_day[owner.id] = self.current_day
            
            # Award points to owner
            owner.total_points += self.config.owner_base_points
            owner.stickers_placed += 1
            self.total_points_earned += self.config.owner_base_points
            
            return True
        else:
            return False
    
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
        if random.random() < self.config.whale_purchase_probability:
            spend_amount = random.uniform(
                self.config.whale_purchase_min,
                self.config.whale_purchase_max
            )
            player.wallet_balance += spend_amount
            player.total_spent += spend_amount
            self.total_revenue += spend_amount
        
        # Whales place more stickers
        if random.random() < 0.8:  # 80% chance to place sticker
            self._create_new_sticker(player)
        
        # Whales scan more frequently
        if random.random() < 0.9:  # 90% chance to scan
            self._simulate_scan_behavior(player)
    
    def _simulate_grinder_behavior(self, player: Player):
        """Simulate grinder player behavior"""
        # Grinders don't make daily purchases - they reinvest points on level up
        # This is handled in the _check_level_up method
        
        if random.random() < 0.7:  # 70% chance to place sticker
            self._create_new_sticker(player)
        
        if random.random() < 0.8:  # 80% chance to scan
            self._simulate_scan_behavior(player)
    
    def _simulate_casual_behavior(self, player: Player):
        """Simulate casual player behavior"""
        # Casual players are less active but more social
        if random.random() < 0.4:  # 40% chance to place sticker
            self._create_new_sticker(player)
        
        if random.random() < 0.5:  # 50% chance to scan
            self._simulate_scan_behavior(player)
        
        # Casual players might spend occasionally
        if random.random() < self.config.casual_purchase_probability:
            spend_amount = random.uniform(
                self.config.casual_purchase_min,
                self.config.casual_purchase_max
            )
            player.wallet_balance += spend_amount
            player.total_spent += spend_amount
            self.total_revenue += spend_amount
    
    def _simulate_scan_behavior(self, player: Player):
        """Simulate a player scanning stickers with geographic constraints"""
        # Update player movement first
        current_time_hours = (self.current_day % 1) * 24
        self._update_player_movement(player, current_time_hours)
        
        # Find available stickers within scanning distance
        if self.config.enable_movement_patterns:
            available_stickers = self._get_nearby_stickers(player)
        else:
            # Fallback to all stickers if movement patterns disabled
            available_stickers = []
            for sticker in self.stickers.values():
                if not sticker.is_active:
                    continue
                available_stickers.append(sticker)
        
        # Filter by cooldown
        filtered_stickers = []
        for sticker in available_stickers:
            if sticker.id in player.last_scan_times:
                days_since_scan = self.current_day - player.last_scan_times[sticker.id]
                if days_since_scan < (self.config.sticker_scan_cooldown_hours / 24):
                    continue
            filtered_stickers.append(sticker)
        
        available_stickers = filtered_stickers
        
        if not available_stickers:
            return
        
        # Choose a sticker to scan
        sticker = random.choice(available_stickers)
        
        # Get current time in hours (simplified - using day progress)
        current_time_hours = (self.current_day % 1) * 24  # Hours within current day
        
        # Calculate points earned by scanner
        scanner_points = self._calculate_scan_points(player, sticker, current_time_hours)
        
        # Calculate points earned by sticker owner
        owner_points = self._calculate_owner_points(sticker, player, current_time_hours)
        
        # Award points and XP to scanner
        player.total_points += scanner_points
        player.total_xp += int(scanner_points)  # Convert points to XP
        player.stickers_scanned += 1
        player.days_since_last_scan = 0
        player.last_scan_times[sticker.id] = self.current_day
        
        # Check for level up
        self._check_level_up(player)
        
        # Award points to sticker owner (if not scanning their own sticker)
        if sticker.owner_id != player.id:
            owner = self.players.get(sticker.owner_id)
            if owner and owner.is_active:
                owner.total_points += owner_points
                owner.total_xp += int(owner_points)  # Convert points to XP
                # Check for owner level up
                self._check_level_up(owner)
        
        # Update sticker stats
        sticker.total_scans += 1
        sticker.unique_scanners.add(player.id)
        
        self.total_scans += 1
        self.total_points_earned += scanner_points + owner_points
    
    def _calculate_scan_points(self, player: Player, sticker: Sticker, current_time_hours: float) -> float:
        """Calculate points earned from scanning a sticker"""
        base_points = self.config.scanner_base_points
        
        # Apply scanner's level multiplier (dynamic calculation for all levels)
        # Configurable base multiplier and increment per level
        scanner_level_mult = self.config.level_multiplier_base + ((player.level - 1) * self.config.level_multiplier_increment)
        
        base_points *= scanner_level_mult
        
        # Apply diversity bonuses
        diversity_bonus = self._calculate_diversity_bonus(player, sticker)
        base_points *= diversity_bonus
        
        # Apply social sneeze bonus
        social_bonus = self._calculate_social_bonus(player, sticker, current_time_hours)
        base_points *= social_bonus
        
        # Apply social hub bonus
        if self.config.enable_social_hubs and self._is_in_social_hub(sticker.location):
            base_points *= self.config.social_hub_scan_bonus
        
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
    
    def _calculate_owner_points(self, sticker: Sticker, scanner: Player, current_time_hours: float) -> float:
        """Calculate points earned by the sticker owner when someone scans their sticker"""
        base_points = self.config.owner_base_points
        
        # Apply sticker owner's level multiplier (this is the key missing piece!)
        # Get the owner's level from the sticker
        owner = self.players.get(sticker.owner_id)
        if owner:
            owner_level_mult = self.config.level_multiplier_base + ((owner.level - 1) * self.config.level_multiplier_increment)
            base_points *= owner_level_mult
        
        # Apply diversity bonuses (owner gets same bonuses as scanner)
        diversity_bonus = self._calculate_diversity_bonus(scanner, sticker)
        base_points *= diversity_bonus
        
        # Apply social sneeze bonus
        social_bonus = self._calculate_social_bonus(scanner, sticker, current_time_hours)
        base_points *= social_bonus
        
        # Apply social hub bonus
        if self.config.enable_social_hubs and self._is_in_social_hub(sticker.location):
            base_points *= self.config.social_hub_scan_bonus
        
        # Apply event bonus
        if self.current_event:
            base_points *= self.config.event_bonus_multiplier
        
        # Apply new player bonus (for the scanner, not owner)
        if self.current_day - scanner.join_day <= self.config.new_player_bonus_days:
            base_points *= self.config.new_player_bonus_multiplier
        
        # Apply streak bonus (for the scanner, not owner)
        if scanner.streak_days >= self.config.streak_bonus_days:
            base_points *= self.config.streak_bonus_multiplier
        
        # Apply comeback bonus (for the scanner, not owner)
        if scanner.days_since_last_scan >= self.config.comeback_bonus_days:
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
            
            # Handle grinder reinvestment on level up
            if (player.player_type == "grinder" and 
                self.config.grinder_reinvest_on_levelup and 
                player.total_points > 0):
                
                # Calculate how many points to reinvest
                points_to_reinvest = player.total_points * self.config.grinder_reinvest_percentage
                
                # Convert points to dollars using the conversion rate
                dollars_reinvested = points_to_reinvest / self.config.points_per_dollar
                
                # Add to wallet balance
                player.wallet_balance += dollars_reinvested
                player.total_spent += dollars_reinvested
                self.total_revenue += dollars_reinvested
                
                # Reset points (they've been "spent")
                player.total_points = 0
                
                # if self.config.enable_console_output:
                    # print(f"💰 Grinder {player.id} reinvested {points_to_reinvest:.1f} points (${dollars_reinvested:.2f}) on level up!")
            
            # if self.config.enable_console_output:
                # print(f"🎉 Player {player.id} ({player.player_type}) leveled up to level {player.level}!")
    
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
    
    def _update_sneeze_mode_status(self, sticker: Sticker, current_time_hours: float):
        """Update sticker's sneeze mode status based on current time"""
        # Check if sticker should enter sneeze mode
        if (not sticker.is_in_sneeze_mode and 
            sticker.total_scans >= self.config.social_sneeze_threshold and
            sticker.sneeze_mode_triggered_at_scans < self.config.social_sneeze_threshold):
            # Trigger sneeze mode
            sticker.is_in_sneeze_mode = True
            sticker.sneeze_mode_start_time = current_time_hours
            sticker.sneeze_mode_triggered_at_scans = sticker.total_scans
            
        # Check if sneeze mode should end
        elif (sticker.is_in_sneeze_mode and 
              current_time_hours - sticker.sneeze_mode_start_time >= self.config.social_sneeze_duration_hours):
            # End sneeze mode
            sticker.is_in_sneeze_mode = False
            sticker.sneeze_mode_start_time = 0.0
    
    def _calculate_social_bonus(self, player: Player, sticker: Sticker, current_time_hours: float) -> float:
        """Calculate social sneeze bonus based on sneeze mode status"""
        # Update sneeze mode status first
        self._update_sneeze_mode_status(sticker, current_time_hours)
        
        # Apply bonus if in sneeze mode
        if sticker.is_in_sneeze_mode:
            return 1.0 + self.config.social_sneeze_bonus
        return 1.0
    
    def _calculate_organic_growth_areas(self) -> Dict[Tuple[float, float], List[Sticker]]:
        """Calculate organic growth areas based on sticker density within radius"""
        areas = {}
        radius_meters = self.config.organic_growth_area_radius_meters
        radius_degrees = radius_meters / 111000  # Convert meters to degrees (rough approximation)
        
        # Group stickers by proximity
        for sticker in self.stickers.values():
            if not sticker.is_active:
                continue
                
            # Find existing area center within radius, or create new one
            area_center = None
            for center in areas.keys():
                distance = math.sqrt(
                    (sticker.location[0] - center[0])**2 + 
                    (sticker.location[1] - center[1])**2
                )
                if distance <= radius_degrees:
                    area_center = center
                    break
            
            if area_center is None:
                # Create new area center at this sticker's location
                area_center = sticker.location
                areas[area_center] = []
            
            areas[area_center].append(sticker)
        
        return areas
    
    def _initialize_social_hubs(self):
        """Initialize social hub locations on the campus"""
        self.social_hubs = [
            (0.05, 0.05),   # Central quad
            (0.03, 0.07),   # Library
            (0.07, 0.03),   # Student center
            (0.02, 0.02),   # Cafeteria
            (0.08, 0.08),   # Gym
        ]
    
    def _calculate_distance_meters(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate distance between two locations in meters"""
        distance_degrees = math.sqrt(
            (loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2
        )
        return distance_degrees * 111000  # Convert degrees to meters (rough approximation)
    
    def _is_in_social_hub(self, location: Tuple[float, float]) -> bool:
        """Check if a location is within a social hub"""
        if not self.config.enable_social_hubs or not hasattr(self, 'social_hubs') or not self.social_hubs:
            return False
        
        for hub_location in self.social_hubs:
            distance = self._calculate_distance_meters(location, hub_location)
            if distance <= self.config.social_hub_radius_meters:
                return True
        return False
    
    def _get_area_density_limit(self, location: Tuple[float, float]) -> int:
        """Get the density limit for a specific area"""
        if not self.config.enable_realistic_density:
            return self.max_stickers_allowed
        
        if self._is_in_social_hub(location):
            return self.config.social_hub_density
        elif self._is_in_campus_building(location):
            return self.config.campus_building_density
        elif self._is_in_campus_quad(location):
            return self.config.campus_quad_density
        else:
            return self.config.campus_perimeter_density
    
    def _is_in_campus_building(self, location: Tuple[float, float]) -> bool:
        """Check if location is in a campus building (simplified)"""
        # Simplified: buildings are in the center area
        center_x, center_y = 0.05, 0.05
        distance = self._calculate_distance_meters(location, (center_x, center_y))
        return distance <= 200  # Within 200m of center
    
    def _is_in_campus_quad(self, location: Tuple[float, float]) -> bool:
        """Check if location is in the campus quad (open area)"""
        # Simplified: quad is the main open area
        center_x, center_y = 0.05, 0.05
        distance = self._calculate_distance_meters(location, (center_x, center_y))
        return 200 < distance <= 400  # Between 200m and 400m from center
    
    def _update_player_movement(self, player: Player, current_time_hours: float):
        """Update player's location based on movement patterns"""
        if not self.config.enable_movement_patterns:
            return
        
        # Calculate time since last movement
        time_since_movement = current_time_hours - player.last_movement_time
        
        # Determine if player should move (based on daily routine)
        should_move = self._should_player_move(player, current_time_hours)
        
        if should_move:
            # Calculate new location based on routine
            new_location = self._calculate_next_location(player, current_time_hours)
            
            # Check if movement is possible (travel time constraints)
            if new_location != player.current_location:
                travel_distance = self._calculate_distance_meters(player.current_location, new_location)
                travel_time_hours = (travel_distance / 100) * (self.config.travel_time_per_100m_minutes / 60)
                
                if time_since_movement >= travel_time_hours:
                    player.current_location = new_location
                    player.last_movement_time = current_time_hours
    
    def _should_player_move(self, player: Player, current_time_hours: float) -> bool:
        """Determine if player should move based on daily routine"""
        # Simplified: players move every 2-4 hours with some randomness
        time_since_movement = current_time_hours - player.last_movement_time
        base_movement_interval = 3.0  # 3 hours
        
        # Add variance based on player type
        if player.player_type == "grinder":
            base_movement_interval *= 0.8  # Grinders move more frequently
        elif player.player_type == "casual":
            base_movement_interval *= 1.5  # Casuals move less frequently
        
        # Add random variance
        variance = random.uniform(0.5, 1.5)
        movement_interval = base_movement_interval * variance
        
        return time_since_movement >= movement_interval
    
    def _calculate_next_location(self, player: Player, current_time_hours: float) -> Tuple[float, float]:
        """Calculate player's next location based on routine and social hub attraction"""
        # Base routine: alternate between home, work, and social hubs
        routine_locations = [player.home_location, player.work_location] + player.social_hubs
        
        if not routine_locations:
            return player.current_location
        
        # Choose next location based on time of day and social hub attraction
        if current_time_hours < 8 or current_time_hours > 22:  # Night time - go home
            return player.home_location
        elif 8 <= current_time_hours < 17:  # Day time - go to work
            return player.work_location
        else:  # Evening - social hubs
            # Check for nearby social hubs with sneeze mode stickers
            sneeze_stickers = self.get_sneeze_mode_stickers(current_time_hours)
            for sticker in sneeze_stickers:
                for hub in player.social_hubs:
                    if self._calculate_distance_meters(sticker.location, hub) <= self.config.social_hub_attraction_radius:
                        return hub  # Attracted to social hub with viral stickers
            
            # Default to random social hub
            return random.choice(player.social_hubs) if player.social_hubs else player.home_location
    
    def _get_nearby_stickers(self, player: Player) -> List[Sticker]:
        """Get stickers within scanning distance of player"""
        nearby_stickers = []
        for sticker in self.stickers.values():
            if not sticker.is_active:
                continue
            
            distance = self._calculate_distance_meters(player.current_location, sticker.location)
            if distance <= self.config.max_scan_distance_meters:
                nearby_stickers.append(sticker)
        
        return nearby_stickers
    
    def _count_stickers_in_area(self, location: Tuple[float, float], radius_meters: float) -> int:
        """Count stickers within a specific area"""
        count = 0
        for sticker in self.stickers.values():
            if not sticker.is_active:
                continue
            
            distance = self._calculate_distance_meters(location, sticker.location)
            if distance <= radius_meters:
                count += 1
        return count
    
    def get_sneeze_mode_stickers(self, current_time_hours: float) -> List[Sticker]:
        """Get all stickers currently in sneeze mode (for hotspot tracking)"""
        sneeze_stickers = []
        for sticker in self.stickers.values():
            if sticker.is_active:
                # Update sneeze mode status
                self._update_sneeze_mode_status(sticker, current_time_hours)
                if sticker.is_in_sneeze_mode:
                    sneeze_stickers.append(sticker)
        return sneeze_stickers
    
    def _calculate_daily_scans_for_player(self, player: Player) -> int:
        """Calculate how many scans a player should do per day based on their type and locale"""
        # Calculate available stickers in the locale
        # Use the same calculation as the density limit for consistency
        # 500m = 0.5km = 0.5/1.609 miles = 0.311 miles
        # 0.5km square = 0.311^2 = 0.097 sq mi
        # 0.097 sq mi / 0.25 = 0.388 quarter sq mi
        locale_area_quarter_sq_mi = (self.config.locale_size_meters / 1000 / 1.609) ** 2 / 0.25
        
        # Calculate available stickers in locale (use actual sticker count, not density assumption)
        available_stickers = len(self.stickers)  # Use actual stickers in the game
        
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
            
            # 1. Viral spread mechanics (20% of active players recruit new players with random frequency)
            
            # Check if we should trigger viral spread
            should_trigger_viral = False
            if self.last_viral_spread_day is None:
                # First time - random chance
                should_trigger_viral = random.random() < 0.1
            else:
                days_since_last_viral = self.current_day - self.last_viral_spread_day
                min_days = self.config.viral_spread_frequency_min_days
                max_days = self.config.viral_spread_frequency_max_days
                if days_since_last_viral >= min_days:
                    if days_since_last_viral >= max_days:
                        should_trigger_viral = True  # Force trigger at max days
                    else:
                        # Random chance between min and max days
                        chance = (days_since_last_viral - min_days) / (max_days - min_days)
                        should_trigger_viral = random.random() < chance
            
            if should_trigger_viral:
                active_players = [p for p in self.players.values() if p.is_active]
                recruiting_players = int(len(active_players) * self.config.viral_spread_percentage)
                viral_recruits = min(recruiting_players, self.max_possible_players - current_players)
                new_players_count += viral_recruits
                self.viral_recruits_today = viral_recruits
                self.last_viral_spread_day = self.current_day  # Track when viral spread occurred
            
            # 2. Organic growth based on sticker activity (daily calculation with area bounds)
            total_active_stickers = len([s for s in self.stickers.values() if s.is_active])
            if total_active_stickers >= self.config.organic_growth_tags_threshold:
                # Calculate area-bounded organic growth
                organic_growth_areas = self._calculate_organic_growth_areas()
                
                for area_center, area_stickers in organic_growth_areas.items():
                    if len(area_stickers) >= self.config.organic_growth_tags_threshold:
                        # Calculate daily organic growth rate for this area (divide weekly rate by 7)
                        sticker_density_factor = min(len(area_stickers) / self.config.organic_growth_tags_threshold, 3.0)
                        daily_organic_rate = random.uniform(
                            self.config.organic_growth_rate_min / 7,  # Convert weekly to daily
                            self.config.organic_growth_rate_max / 7   # Convert weekly to daily
                        ) * sticker_density_factor
                        
                        # Apply to total population, not just current players
                        area_organic_new_players = int(self.config.total_population * daily_organic_rate)
                        area_organic_new_players = min(area_organic_new_players, self.max_possible_players - current_players - new_players_count)
                        new_players_count += area_organic_new_players
                        self.organic_new_players_today += area_organic_new_players
            
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
        
        # Calculate sneeze mode statistics
        current_time_hours = (self.current_day % 1) * 24  # Hours within current day
        sneeze_stickers = self.get_sneeze_mode_stickers(current_time_hours)
        sneeze_hotspots = [sticker.location for sticker in sneeze_stickers]
        
        # Calculate social hub statistics
        active_social_hubs = 0
        social_hub_locations = []
        players_in_social_hubs = 0
        
        if self.config.enable_social_hubs and hasattr(self, 'social_hubs') and self.social_hubs:
            for hub_location in self.social_hubs:
                # Check if hub has any stickers
                hub_stickers = self._count_stickers_in_area(hub_location, self.config.social_hub_radius_meters)
                if hub_stickers > 0:
                    active_social_hubs += 1
                    social_hub_locations.append(hub_location)
                
                # Count players in this hub
                for player in active_players:
                    if self._calculate_distance_meters(player.current_location, hub_location) <= self.config.social_hub_radius_meters:
                        players_in_social_hubs += 1
        
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
            population_cap_reached=len(active_players) >= self.max_possible_players,
            
            # === STICKER DENSITY METRICS ===
            current_sticker_density=len(self.stickers) / ((self.config.locale_size_meters / 1000 / 1.609) ** 2 / 0.25),
            max_stickers_allowed=self.max_stickers_allowed,
            sticker_density_cap_reached=len(self.stickers) >= self.max_stickers_allowed,
            
            # === SOCIAL SNEEZE MODE METRICS ===
            stickers_in_sneeze_mode=len(sneeze_stickers),
            sneeze_mode_hotspots=sneeze_hotspots,
            
            # === SOCIAL HUB METRICS ===
            active_social_hubs=active_social_hubs,
            social_hub_locations=social_hub_locations,
            players_in_social_hubs=players_in_social_hubs
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
        finally:
            # Run analysis if enabled and simulation completed normally
            if self.config.auto_analyze_on_completion and not self.paused:
                self.run_analysis_on_completion()
    
    def _print_daily_summary(self, stats: DailyStats):
        """Print daily summary to console"""
        sneeze_info = f" | Sneeze: {stats.stickers_in_sneeze_mode}" if stats.stickers_in_sneeze_mode > 0 else ""
        hub_info = f" | Hubs: {stats.active_social_hubs}" if stats.active_social_hubs > 0 else ""
        print(f"Day {stats.day:3d} | "
              f"Players: {stats.active_players:4d} | "
              f"Revenue: ${stats.total_revenue:8.2f} | "
              f"Scans: {stats.total_scans:5d} | "
              f"Stickers: {stats.total_stickers_placed:4d} | "
              f"Retention: {stats.retention_rate:.1%} | "
              f"Growth: {stats.growth_rate:+.1%}{sneeze_info}{hub_info}")
    
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
    
    def run_analysis_on_completion(self):
        """Run comprehensive analysis when simulation completes"""
        if not self.config.auto_analyze_on_completion:
            return
            
        print("\n" + "="*60)
        print("RUNNING POST-SIMULATION ANALYSIS")
        print("="*60)
        
        try:
            # Import analysis tools
            from analysis_tools import FYNDRAnalyzer
            
            # Create analyzer instance
            analyzer = FYNDRAnalyzer()
            
            # Export simulation data to CSV files for analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            daily_stats_file = f"analysis_daily_stats_{timestamp}.csv"
            players_file = f"analysis_players_{timestamp}.csv"
            stickers_file = f"analysis_stickers_{timestamp}.csv"
            
            # Export daily stats
            with open(daily_stats_file, 'w', newline='') as f:
                if self.daily_stats:
                    writer = csv.DictWriter(f, fieldnames=asdict(self.daily_stats[0]).keys())
                    writer.writeheader()
                    for stats in self.daily_stats:
                        writer.writerow(asdict(stats))
            
            # Export player data
            with open(players_file, 'w', newline='') as f:
                if self.players:
                    # Get all player attributes
                    sample_player = list(self.players.values())[0]
                    fieldnames = list(asdict(sample_player).keys())
                    # Convert sets to lists for CSV compatibility
                    for field in fieldnames:
                        if hasattr(sample_player, field):
                            attr = getattr(sample_player, field)
                            if isinstance(attr, set):
                                fieldnames[fieldnames.index(field)] = f"{field}_list"
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for player in self.players.values():
                        player_dict = asdict(player)
                        # Convert sets to lists
                        for key, value in player_dict.items():
                            if isinstance(value, set):
                                player_dict[f"{key}_list"] = list(value)
                                del player_dict[key]
                        writer.writerow(player_dict)
            
            # Export sticker data
            with open(stickers_file, 'w', newline='') as f:
                if self.stickers:
                    sample_sticker = list(self.stickers.values())[0]
                    fieldnames = list(asdict(sample_sticker).keys())
                    # Convert sets to lists for CSV compatibility
                    for field in fieldnames:
                        if hasattr(sample_sticker, field):
                            attr = getattr(sample_sticker, field)
                            if isinstance(attr, set):
                                fieldnames[fieldnames.index(field)] = f"{field}_list"
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for sticker in self.stickers.values():
                        sticker_dict = asdict(sticker)
                        # Convert sets to lists
                        for key, value in sticker_dict.items():
                            if isinstance(value, set):
                                sticker_dict[f"{key}_list"] = list(value)
                                del sticker_dict[key]
                        writer.writerow(sticker_dict)
            
            # Load data into analyzer
            analyzer.load_simulation_data(daily_stats_file, players_file, stickers_file)
            
            # Run comprehensive analysis
            print("Analyzing economy health...")
            economy_health = analyzer.analyze_economy_health()
            
            print("Analyzing player behavior...")
            player_behavior = analyzer.analyze_player_behavior()
            
            print("Analyzing growth patterns...")
            growth_analysis = analyzer.analyze_growth_patterns()
            
            # Generate comprehensive report
            print("Generating analysis report...")
            report = analyzer.generate_comprehensive_report()
            
            # Save analysis results
            analysis_file = f"simulation_analysis_{timestamp}.json"
            with open(analysis_file, 'w') as f:
                json.dump({
                    'economy_health': economy_health,
                    'player_behavior': player_behavior,
                    'growth_analysis': growth_analysis,
                    'comprehensive_report': report,
                    'simulation_config': asdict(self.config),
                    'final_stats': asdict(self.daily_stats[-1]) if self.daily_stats else {}
                }, f, indent=2)
            
            print(f"\nAnalysis completed! Results saved to:")
            print(f"  - {analysis_file}")
            print(f"  - {daily_stats_file}")
            print(f"  - {players_file}")
            print(f"  - {stickers_file}")
            
            # Print summary to console
            print("\n" + "="*60)
            print("ANALYSIS SUMMARY")
            print("="*60)
            print(f"Total Players: {len(self.players)}")
            print(f"Total Revenue: ${self.total_revenue:.2f}")
            print(f"Total Scans: {self.total_scans}")
            print(f"Total Stickers: {len(self.stickers)}")
            if self.daily_stats:
                final_day = self.daily_stats[-1]
                print(f"Final Day Active Players: {final_day.active_players}")
                print(f"Retention Rate: {final_day.retention_rate:.1%}")
                print(f"Growth Rate: {final_day.growth_rate:+.1%}")
            
        except ImportError:
            print("Warning: analysis_tools module not found. Skipping analysis.")
        except Exception as e:
            print(f"Error during analysis: {e}")
            print("Continuing without analysis...")
    
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
        
        # Run analysis if enabled
        if simulator.config.auto_analyze_on_completion:
            simulator.run_analysis_on_completion()
        
        print("Simulation completed")

if __name__ == "__main__":
    main()
