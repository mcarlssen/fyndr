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
import os
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
    real_time_speed: float = 0  # 1.0 = real time, 0.1 = 10x faster, 10.0 = 10x slower
    auto_save_interval: int = 2000  # Save every N days
    enable_visualization: bool = True
    enable_console_output: bool = True
    auto_analyze_on_completion: bool = True  # Automatically run analysis when simulation completes

    # === STARTING POPULATION ===
    starting_player_count: int = 20  # Number of players to start the simulation with
    starting_player_type_ratios: Dict[str, float] = None  # Will be set in __post_init__
    
    # === STARTING PLAYER REWARDS ===
    starting_player_points: float = 100.0  # Starting points for initial players
    starting_player_stickers: int = 0  # Free stickers for initial players
    starting_whale_wallet_balance: float = 0.0  # Starting wallet balance for whale players
    starting_whale_total_spent: float = 0.0  # Starting total spent for whale players
    
    # === CURRENT POINT CALCULATION ORDER ===
    # Base points
    # Level multiplier
    # Diversity bonus
    # Social sneeze bonus
    # Social hub bonus
    # Event bonus
    # New player bonus
    # Streak bonus
    # Comeback bonus
    # Referral bonus (2x for 14 days)
    # Referral bonus (2x for 14 days)

    # === CORE SCORING PARAMETERS ===
    owner_base_points: float = 3.0
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
        
    # === LINEAR PROGRESSION LEVELING SYSTEM ===
    use_linear_progression: bool = True  # Enable/disable linear progression curve
    level_base_xp: int = 200  # XP required for level 1
    level_first_increment: int = 25  # XP increase from level 1 → 2
    level_increment_step: int = 34  # How much the increment grows each level (optimized for 9-month completion)
    level_xp_thresholds: List[int] = None  # Will be calculated in __post_init__
    max_level: int = 200
    
    # === LEVEL MULTIPLIER SYSTEM ===
    level_multiplier_base: float = 1.0  # Base multiplier for level 1
    level_multiplier_increment: float = 0.05  # Multiplier increase per level
    
    # === LOCALE AND SCANNING BEHAVIOR ===
    locale_size_meters: float = 804.5  # Locale size in meters (804.5m square = 1 quarter sq mi)
    sticker_density_per_locale_size: int = 500  # Average stickers per local 'unit'
    
    # === PLAYER MOVEMENT PATTERNS ===
    enable_movement_patterns: bool = True  # Enable realistic player movement
    max_scan_distance_meters: float = 300.0  # Maximum distance to scan stickers
    travel_time_per_100m_minutes: float = 2.0  # Travel time per 100 meters (walking speed)
    daily_routine_variance: float = 0.3  # Random variance in daily routines (30%)
    
    # === SOCIAL HUB MECHANICS ===
    enable_social_hubs: bool = True  # Enable social hub mechanics
    social_hub_radius_meters: float = 50.0  # Radius of social hub influence
    social_hub_scan_bonus: float = 2.5  # Bonus multiplier for scanning in social hubs
    social_hub_placement_bonus: float = 2.0  # Bonus multiplier for placing in social hubs
    social_hub_attraction_radius: float = 200.0  # How far players are drawn to social hubs
    
    # Player type scanning behavior (percentage of available stickers per day)
    whale_scan_percentage: float = 0.3  # 30% chance to scan per day
    grinder_scan_percentage: float = 0.95  # 90% chance to scan per day
    casual_scan_percentage: float = 0.6  # 60% chance to scan per day
    
    # === STICKER DENSITY LIMITS ===
    sticker_placement_cooldown_days: int = 0  # No cooldown - allow multiple stickers per day
    
    # === REALISTIC DENSITY SIMULATION ===
    enable_realistic_density: bool = False  # Enable area-specific density limits
    campus_building_density: int = 1000  # High density in campus buildings
    campus_quad_density: int = 200  # Medium density in open areas
    campus_perimeter_density: int = 50  # Low density on campus edges
    social_hub_density: int = 1500  # Very high density in social hubs
    
    # === MONETIZATION ===
    pack_price_points: int = 550
    pack_price_dollars: float = 3.0
    points_per_dollar: float = 250.0
    wallet_topup_min: float = 6.0
    wallet_topup_max: float = 60.0
    
    # === PRICE SENSITIVITY MECHANICS ===
    enable_price_sensitivity: bool = True  # Enable price-based purchase probability adjustments
    price_sensitivity_factor: float = .25  # How much price affects purchase probability (0.1 = 10% change per $1)
    
    # === PURCHASING BEHAVIOR ===
    # Whale purchasing behavior (monthly rates converted to daily)
    whale_purchase_probability: float = 0.1  # 10% daily = 3 purchases/month (2-4 purchases/month)
    # Note: whale_purchase_min/max removed - now using wallet_topup_min/max ($6-60)
    
    # Grinder purchasing behavior (1/4 whale rate + point reinvestment)
    grinder_purchase_probability: float = 0.025  # 2.5% daily = 0.75 purchases/month (0.5-1% monthly)
    grinder_purchase_min: float = 3.0  # Minimum purchase amount
    grinder_purchase_max: float = 9.0  # Maximum purchase amount
    grinder_reinvest_on_levelup: bool = True  # Grinders reinvest all points when leveling up
    grinder_reinvest_percentage: float = 1.0  # 100% of points reinvested on level up
    
    # Casual purchasing behavior  
    casual_purchase_probability: float = 0.033  # 3.3% daily = 1 purchase/month to spend money
    casual_purchase_min: float = 3.0  # Minimum purchase amount
    casual_purchase_max: float = 3.0  # Maximum purchase amount
    
    # === SCANNING MECHANICS ===
    sticker_scan_cooldown_hours: int = 11  # 1 hour cooldown for more frequent scanning
    
    # === BONUS SYSTEMS ===
    # Streak bonuses: Rewards consecutive daily activity (no cooldown, resets if inactive)
    streak_bonus_days: int = 21  # Days of consecutive activity needed (legacy)
    streak_bonus_multiplier: float = 3  # Point multiplier during streak (legacy)
    
    # Tiered streak bonuses for scan and placement streaks
    scan_streak_tiers: List[Tuple[int, float]] = None  # Will be set in __post_init__
    placement_streak_tiers: List[Tuple[int, float]] = None  # Will be set in __post_init__
    activity_streak_tiers: List[Tuple[int, float]] = None  # Will be set in __post_init__
    
    # Combined activity streak (scanning OR placing)
    activity_streak_bonus_days: int = 21  # Days of any activity needed
    activity_streak_bonus_multiplier: float = 2.0  # Point multiplier for activity streak
    
    # Comeback bonus: Rewards players returning after absence (no cooldown, triggers once per return)
    comeback_bonus_days: int = 3  # Days away needed to trigger comeback bonus
    comeback_bonus_multiplier: float = 2.0  # Point multiplier for comeback

     # === EVENTS ===
    # Seasonal/special events: Randomly triggered events that boost all point earnings
    event_frequency_days: int = 7  # Average days between events (randomly triggered)
    event_duration_days: int = 2  # How long events last once triggered
    event_bonus_multiplier: float = 5  # Point multiplier during events (applies to all scans)
    
    # === REFERRAL REWARD SYSTEM ===
    # Referral rewards: Players who refer others get bonuses
    referral_reward_multiplier: float = 4.0  # Point multiplier for referrers
    referral_reward_days: int = 7  # Days of bonus for successful referrers

    # === CHURN AND RETENTION ===
    # Time-based churn curves (replaces flat rates with realistic industry benchmarks)
    # Format: {player_type: {time_period: daily_churn_rate}}
    churn_curves: Dict[str, Dict[str, float]] = None  # Will be set in __post_init__
    
    # === COMEBACK MECHANICS ===
    comeback_cooldown_days: int = 30  # 30 days cooldown before comeback is possible
    comeback_probability: float = 0.01  # 1% chance per day for churned players to return
    comeback_bonus_points: float = 500.0  # Bonus points for returning players
    
    # === POPULATION & SPREAD MECHANICS ===
    # Population variables for modeling game spread in a locale
    total_population: int = 2500  # Total population of the area
    population_density_per_quarter_sq_mile: float = 4000.0  # Population density per quarter square mile

    # Player type distribution for new players (overrides individual probabilities when enabled)
    use_population_mechanics: bool = True  # Enable/disable population-based growth
    new_player_type_ratios: Dict[str, float] = None  # Will be set in __post_init__

    # === NEW PLAYER ONBOARDING ===
    # New player bonus: Boosts new players for their first week (no cooldown, one-time per player)
    new_player_bonus_days: int = 14  # Days of bonus for new players
    new_player_bonus_multiplier: float = 3.0  # Point multiplier for new players
    new_player_free_packs: int = 0  # Free sticker packs for new players
    
    # === NEW PLAYER STARTING ASSETS ===
    new_player_points: float = 100.0  # Starting points for new players (who join later)
    new_player_stickers: int = 0  # Starting stickers for new players (0 = must earn/purchase)
    new_player_whale_wallet_balance: float = 0.0  # Starting wallet balance for new whale players
    new_player_whale_total_spent: float = 0.0  # Starting total spent for new whale players
    
    # Viral spread mechanics
    viral_spread_percentage: float = 0.012  # 1.2% of active players recruit new players
    viral_spread_frequency_min_days: int = 7  # Minimum days between viral spread events
    viral_spread_frequency_max_days: int = 14  # Maximum days between viral spread events
    viral_spread_cap_percentage: float = 0.40  # Maximum 40% of total population can be players
    
    # Organic growth mechanics
    organic_growth_rate_min: float = 0.002  # 0.2% minimum organic growth per 50 tags per week
    organic_growth_rate_max: float = 0.005  # 0.5% maximum organic growth per 50 tags per week
    organic_growth_tags_threshold: int = 50  # Number of tags required for organic growth calculation
    organic_growth_area_radius_meters: float = 50.0  # Radius in meters for area-bounded organic growth
    
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
        
        # Initialize tiered streak bonuses
        if self.scan_streak_tiers is None:
            self.scan_streak_tiers = [
                (8, 2.0),   # 8 days: 2x multiplier
                (12, 3.0),  # 12 days: 3x multiplier
                (17, 4.0),  # 17 days: 4x multiplier
                (23, 5.0),  # 23 days: 5x multiplier
                (30, 6.0)   # 30 days: 6x multiplier
            ]
        
        if self.placement_streak_tiers is None:
            self.placement_streak_tiers = [
                (8, 2.0),   # 8 days: 2x multiplier
                (12, 3.0),  # 12 days: 3x multiplier
                (17, 4.0),  # 17 days: 4x multiplier
                (23, 5.0),  # 23 days: 5x multiplier
                (30, 6.0)   # 30 days: 6x multiplier
            ]
        
        if self.activity_streak_tiers is None:
            self.activity_streak_tiers = [
                (8, 2.0),   # 8 days: 2x multiplier
                (12, 3.0),  # 12 days: 3x multiplier
                (17, 4.0),  # 17 days: 4x multiplier
                (23, 5.0),  # 23 days: 5x multiplier
                (30, 6.0)   # 30 days: 6x multiplier
            ]
        
        # Initialize realistic time-based churn curves based on industry benchmarks
        if self.churn_curves is None:
            self.churn_curves = {
                "casual": {
                    "day_1_3": 0.15,    # 15% daily churn (high initial drop-off)
                    "day_4_7": 0.08,    # 8% daily churn (stabilizing)
                    "day_8_30": 0.05,   # 5% daily churn (more realistic long-term)
                    "day_31_plus": 0.04 # 4% daily churn (mature players)
                },
                "grinder": {
                    "day_1_3": 0.10,    # 10% daily churn (better initial retention)
                    "day_4_7": 0.05,    # 5% daily churn
                    "day_8_30": 0.03,   # 3% daily churn (more realistic long-term)
                    "day_31_plus": 0.025 # 2.5% daily churn (very engaged)
                },
                "whale": {
                    "day_1_3": 0.06,    # 6% daily churn (best initial retention)
                    "day_4_7": 0.03,    # 3% daily churn
                    "day_8_30": 0.015,  # 1.5% daily churn (excellent long-term)
                    "day_31_plus": 0.01 # 1% daily churn (highly engaged)
                }
            }
    
    def _calculate_xp_thresholds(self) -> List[int]:
        """Calculate XP thresholds for linear progression curve"""
        
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
    days_since_last_placement: int = 0
    
    # === STICKER INVENTORY TRACKING ===
    stickers_owned: int = 0  # Total stickers in inventory
    sticker_packs_purchased: int = 0  # Packs bought with money
    sticker_packs_earned: int = 0  # Packs bought with points
    total_stickers_purchased: int = 0  # Total stickers bought (money + points)
    
    # === STREAK TRACKING ===
    streak_days: int = 0  # Legacy - total activity streak
    scan_streak_days: int = 0  # Consecutive days of scanning
    placement_streak_days: int = 0  # Consecutive days of placing stickers
    last_activity_day: int = 0  # Last day player was active (scanned OR placed)
    scanned_today: bool = False  # Did player scan today?
    placed_today: bool = False  # Did player place a sticker today?
    last_scan_times: Dict[int, int] = None  # sticker_id -> day
    last_scan_locations: Dict[int, Tuple[float, float]] = None  # sticker_id -> location
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
    
    # === REFERRAL TRACKING ===
    referred_by: Optional[int] = None  # ID of player who referred this player
    referrals_made: int = 0  # Number of successful referrals made
    referral_bonus_remaining: int = 0  # Days of referral bonus remaining
    
    # === COMEBACK TRACKING ===
    churn_day: Optional[int] = None  # Day when player churned
    comeback_eligible_day: Optional[int] = None  # Day when player becomes eligible for comeback
    has_received_comeback_bonus: bool = False
    
    # === LEVEL-UP TRACKING ===
    last_level_up_day: Optional[int] = None  # Day when player last leveled up  # Whether player has received comeback bonus
    
    def __post_init__(self):
        if self.last_scan_times is None:
            self.last_scan_times = {}
        if self.last_scan_locations is None:
            self.last_scan_locations = {}
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
    total_earnings: float = 0.0
    daily_earnings: float = 0.0
    scans_today: int = 0
    unique_scans_today: int = 0
    days_since_last_scan: int = 0
    
    # Social sneeze mode tracking
    is_in_sneeze_mode: bool = False
    sneeze_mode_start_time: float = 0.0  # Time when sneeze mode started (in hours from day start)
    sneeze_mode_triggered_at_scans: int = 0  # Scan count when sneeze mode was triggered
    
    def __post_init__(self):
        if self.unique_scanners is None:
            self.unique_scanners = set()

@dataclass
class GameEvent:
    """Represents a game event that occurred"""
    day: int
    event_type: str  # 'seasonal_event', 'viral_spread', 'organic_growth', 'sneeze_mode', 'level_up', 'purchase', 'churn'
    description: str
    affected_players: int = 0
    affected_stickers: int = 0
    bonus_multiplier: float = 1.0
    additional_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}


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
    
    # === STICKER ECONOMY ANALYTICS ===
    total_stickers_purchased: int = 0  # Total stickers bought (money + points)
    total_sticker_packs_purchased: int = 0  # Packs bought with money
    total_sticker_packs_earned: int = 0  # Packs bought with points
    purchase_to_placement_ratio: float = 0.0  # Ratio of purchases to placements
    
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
    
    # === EVENT TRACKING ===
    events_today: List[GameEvent] = None  # Events that occurred today
    active_events: List[str] = None  # Currently active event types
    event_impacts: Dict[str, float] = None  # Impact of events on metrics
    
    # === COMEBACK TRACKING ===
    comeback_players_today: int = 0  # Number of players who returned today
    
    def __post_init__(self):
        if self.sneeze_mode_hotspots is None:
            self.sneeze_mode_hotspots = []
        if self.social_hub_locations is None:
            self.social_hub_locations = []
        if self.events_today is None:
            self.events_today = []
        if self.active_events is None:
            self.active_events = []
        if self.event_impacts is None:
            self.event_impacts = {}

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
        self.game_events: List[GameEvent] = []  # All events that have occurred
        self.events_today: List[GameEvent] = []  # Events that occurred today
        
        # Comeback tracking
        self.comeback_players_today = 0
        
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
    
    def _calculate_xp_threshold(self, level: int) -> int:
        """Calculate XP threshold for a specific level"""
        if level <= 0 or level > self.config.max_level:
            return float('inf')
        
        # Level 1 threshold is base_xp
        if level == 1:
            return self.config.level_base_xp
        
        # For levels 2+, use the thresholds list
        if level - 1 < len(self.config.level_xp_thresholds):
            return self.config.level_xp_thresholds[level - 1]
        
        # Fallback calculation if thresholds list is incomplete
        increment = self.config.level_first_increment
        current = self.config.level_base_xp
        
        for lvl in range(2, level + 1):
            current += increment
            increment += self.config.level_increment_step
        
        return current
    
    def _calculate_max_stickers_allowed(self) -> int:
        """Calculate the maximum number of stickers allowed based on locale area and density limits"""
        # Calculate the actual playing field area in square meters
        locale_area_meters = self.config.locale_size_meters ** 2
        
        # Fixed reference area: 804.5m × 804.5m = 647,220 square meters, or approx. 0.25 square miles
        reference_area_sq_meters = 647220
        
        # Calculate density ratio: actual area / reference area
        density_ratio = locale_area_meters / reference_area_sq_meters
        
        # Calculate target sticker count based on density ratio
        max_stickers = int(self.config.sticker_density_per_locale_size * density_ratio)
        #print(f"Max stickers allowed: {max_stickers} (area: {locale_area_meters:.0f} sq m, ratio: {density_ratio:.3f})")
        
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
            
            # Give starting players some starting points and free packs
            player.total_points = self.config.starting_player_points
            player.stickers_owned = self.config.starting_player_stickers
            if player.player_type == "whale":
                player.wallet_balance = self.config.starting_whale_wallet_balance
                player.total_spent = self.config.starting_whale_total_spent
                self.total_revenue += self.config.starting_whale_total_spent
            
            self.players[self.next_player_id] = player
            self.next_player_id += 1
        
        # Create some initial stickers (respecting density limits)
        initial_stickers = min(100, self.max_stickers_allowed)
        for _ in range(initial_stickers):
            self._create_new_sticker()
    
    def _purchase_sticker_pack_with_money(self, player: Player) -> bool:
        """Purchase a sticker pack with real money"""
        if player.wallet_balance < self.config.pack_price_dollars:
            return False
        
        # Deduct money
        player.wallet_balance -= self.config.pack_price_dollars
        player.total_spent += self.config.pack_price_dollars
        self.total_revenue += self.config.pack_price_dollars
        
        # Add stickers to inventory
        stickers_per_pack = 6  # 6 stickers per pack
        player.stickers_owned += stickers_per_pack
        player.sticker_packs_purchased += 1
        player.total_stickers_purchased += stickers_per_pack
        
        return True
    
    def _purchase_sticker_pack_with_points(self, player: Player) -> bool:
        """Purchase a sticker pack with points"""
        if player.total_points < self.config.pack_price_points:
            return False
        
        # Deduct points
        player.total_points -= self.config.pack_price_points
        
        # Add stickers to inventory
        stickers_per_pack = 6  # 6 stickers per pack
        player.stickers_owned += stickers_per_pack
        player.sticker_packs_earned += 1
        player.total_stickers_purchased += stickers_per_pack
        
        return True
    
    def _calculate_price_adjusted_probability(self, base_probability: float, player_type: str) -> float:
        """Calculate purchase probability adjusted for price sensitivity"""
        if not self.config.enable_price_sensitivity:
            return base_probability
        
        # Use pack_price_dollars as the reference price (no separate base_pack_price needed)
        # Price sensitivity is relative to the current pack price
        # For now, we'll use a simple linear adjustment based on price level
        # Lower prices = higher probability, higher prices = lower probability
        
        # Calculate price adjustment (10% change per $1 with 0.1 factor)
        # If price is $2: +10% probability, if price is $4: -10% probability
        price_adjustment = (self.config.pack_price_dollars - 3.0) * self.config.price_sensitivity_factor
        
        # Adjust probability (negative adjustment = lower price = higher probability)
        adjusted_probability = base_probability * (1 - price_adjustment)
        
        # Ensure probability stays within reasonable bounds (0.1% to 50%)
        adjusted_probability = max(0.001, min(0.5, adjusted_probability))
        
        return adjusted_probability
    
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
            
        # Check if player has stickers to place
        if owner.stickers_owned <= 0:
            return False
            
        venue_type = random.choices(
            self.config.venue_types,
            weights=self.config.venue_type_weights
        )[0]
        
        # Place sticker near owner's current location
        location = (
            owner.current_location[0] + random.uniform(-0.01, 0.01),
            owner.current_location[1] + random.uniform(-0.01, 0.01)
        )
        
        # Check global density limit (500 stickers total)
        if len(self.stickers) >= self.max_stickers_allowed:
            return False
        
        # Calculate placement streak bonus for the owner
        placement_bonus = self._calculate_placement_streak_bonus(owner)
        
        sticker = Sticker(
            id=self.next_sticker_id,
            owner_id=owner.id,
            venue_type=venue_type,
            location=location,
            points_value=self.config.owner_base_points * placement_bonus,
            creation_day=self.current_day
        )
        
        # Add the sticker (we already checked the limit above)
        self.stickers[self.next_sticker_id] = sticker
        self.next_sticker_id += 1
        self.total_stickers_placed += 1
        
        # Deduct sticker from inventory
        owner.stickers_owned -= 1
        
        # Track player's last sticker placement
        self.player_last_sticker_day[owner.id] = self.current_day
        
        # Award points to owner
        owner.total_points += self.config.owner_base_points
        owner.stickers_placed += 1
        self.total_points_earned += self.config.owner_base_points
        
        return True
    
    def _simulate_player_behavior(self, player: Player):
        """Simulate a single player's behavior for one day"""
        if not player.is_active:
            return
            
        # Check for churn
        if self._check_player_churn(player):
            player.is_active = False
            player.churn_day = self.current_day
            player.comeback_eligible_day = self.current_day + self.config.comeback_cooldown_days
            return
        
        # Update player stats
        player.days_active += 1
        player.days_since_last_scan += 1
        player.days_since_last_placement += 1
        
        # Decay referral bonus
        if player.referral_bonus_remaining > 0:
            player.referral_bonus_remaining -= 1
        
        # Track daily activity for streak calculation
        player.scanned_today = False
        player.placed_today = False
        
        # Simulate player actions based on type
        if player.player_type == "whale":
            self._simulate_whale_behavior(player)
        elif player.player_type == "grinder":
            self._simulate_grinder_behavior(player)
        else:  # casual
            self._simulate_casual_behavior(player)
        
        # Update streaks based on today's activity
        self._update_player_streaks(player)
    
    def _check_player_churn(self, player: Player) -> bool:
        """Check if a player should churn based on time-based churn curves and activity"""
        # Calculate days since player joined
        days_since_install = self.current_day - player.join_day
        
        # Get base churn rate from time-based curves
        churn_curves = self.config.churn_curves[player.player_type]
        
        if days_since_install <= 3:
            base_churn = churn_curves["day_1_3"]
        elif days_since_install <= 7:
            base_churn = churn_curves["day_4_7"]
        elif days_since_install <= 30:
            base_churn = churn_curves["day_8_30"]
        else:
            base_churn = churn_curves["day_31_plus"]
        
        # Apply activity-based modifiers
        churn_prob = self._apply_activity_churn_modifiers(base_churn, player)
        
        return random.random() < churn_prob
    
    def _apply_activity_churn_modifiers(self, base_churn: float, player: Player) -> float:
        """Apply activity-based modifiers to churn probability"""
        churn_prob = base_churn
        
        # Increase churn if player hasn't been active recently
        if player.days_since_last_scan > 14:
            churn_prob *= 4.0  # 4x churn if inactive > 14 days
        elif player.days_since_last_scan > 7:
            churn_prob *= 2.5  # 2.5x churn if inactive > 7 days
        elif player.days_since_last_scan > 3:
            churn_prob *= 1.5  # 1.5x churn if inactive > 3 days
        
        # Reduce churn for highly engaged players
        if player.streak_days >= 14:
            churn_prob *= 0.3  # 70% reduction for 14+ day streaks
        elif player.streak_days >= 7:
            churn_prob *= 0.5  # 50% reduction for 7+ day streaks
        elif player.streak_days >= 3:
            churn_prob *= 0.8  # 20% reduction for 3+ day streaks
        
        # Reduce churn for players who have made purchases (investment)
        if player.total_spent > 0:
            churn_prob *= 0.7  # 30% reduction for paying players
        
        # Reduce churn for high-level players (investment in progression)
        if player.level >= 10:
            churn_prob *= 0.6  # 40% reduction for level 10+ players
        elif player.level >= 5:
            churn_prob *= 0.8  # 20% reduction for level 5+ players
        
        return churn_prob
    
    def _calculate_tiered_scan_streak_bonus(self, player: Player) -> float:
        """Calculate tiered scan streak bonus based on consecutive scanning days"""
        bonus = 1.0
        
        # Find the highest tier the player qualifies for
        for days_required, multiplier in self.config.scan_streak_tiers:
            if player.scan_streak_days >= days_required:
                bonus = multiplier
            else:
                break  # Tiers are ordered by days, so we can stop at first failure
        
        return bonus
    
    def _calculate_tiered_placement_streak_bonus(self, player: Player) -> float:
        """Calculate tiered placement streak bonus based on consecutive placement days"""
        bonus = 1.0
        
        # Find the highest tier the player qualifies for
        for days_required, multiplier in self.config.placement_streak_tiers:
            if player.placement_streak_days >= days_required:
                bonus = multiplier
            else:
                break  # Tiers are ordered by days, so we can stop at first failure
        
        return bonus
    
    def _calculate_tiered_activity_streak_bonus(self, player: Player) -> float:
        """Calculate tiered activity streak bonus based on consecutive activity days"""
        bonus = 1.0
        
        # Find the highest tier the player qualifies for
        for days_required, multiplier in self.config.activity_streak_tiers:
            if player.streak_days >= days_required:
                bonus = multiplier
            else:
                break  # Tiers are ordered by days, so we can stop at first failure
        
        return bonus
    
    def _calculate_placement_streak_bonus(self, player: Player) -> float:
        """Calculate placement streak bonus for sticker creation"""
        bonus = 1.0
        
        # Apply tiered placement streak bonus
        placement_streak_bonus = self._calculate_tiered_placement_streak_bonus(player)
        bonus *= placement_streak_bonus
        
        # Apply tiered activity streak bonus
        activity_streak_bonus = self._calculate_tiered_activity_streak_bonus(player)
        bonus *= activity_streak_bonus
        
        return bonus
    
    def _update_player_streaks(self, player: Player):
        """Update player streaks based on today's activity"""
        # Update scan streak
        if player.scanned_today:
            player.scan_streak_days += 1
            player.days_since_last_scan = 0
        else:
            player.scan_streak_days = 0
        
        # Update placement streak  
        if player.placed_today:
            player.placement_streak_days += 1
            player.days_since_last_placement = 0
        else:
            player.placement_streak_days = 0
        
        # Update overall activity streak (scanning OR placing)
        if player.scanned_today or player.placed_today:
            player.streak_days += 1
            player.last_activity_day = self.current_day
        else:
            player.streak_days = 0
        
        # Add realistic streak variability (occasional breaks)
        self._apply_streak_variability(player)
    
    def _apply_streak_variability(self, player: Player):
        """Apply realistic streak variability with occasional breaks"""
        # 5% chance to break a streak even if active (realistic life events)
        if random.random() < 0.05 and (player.scan_streak_days > 0 or player.placement_streak_days > 0):
            if random.random() < 0.5:
                player.scan_streak_days = 0
            else:
                player.placement_streak_days = 0
        
        # 2% chance to break overall activity streak
        if random.random() < 0.02 and player.streak_days > 0:
            player.streak_days = 0
    
    def get_churn_statistics(self) -> Dict[str, Any]:
        """Calculate churn statistics for analysis"""
        if not self.players:
            return {}
        
        # Calculate retention rates by day
        retention_by_day = {}
        for day in range(1, min(31, self.current_day + 1)):
            players_at_start = sum(1 for p in self.players.values() if p.join_day <= self.current_day - day)
            players_remaining = sum(1 for p in self.players.values() 
                                 if p.join_day <= self.current_day - day and p.is_active)
            
            if players_at_start > 0:
                retention_rate = players_remaining / players_at_start
                retention_by_day[day] = retention_rate
        
        # Calculate churn rates by player type
        churn_by_type = {}
        for player_type in ["casual", "grinder", "whale"]:
            type_players = [p for p in self.players.values() if p.player_type == player_type]
            if type_players:
                churned = sum(1 for p in type_players if not p.is_active)
                total = len(type_players)
                churn_by_type[player_type] = {
                    "total": total,
                    "churned": churned,
                    "churn_rate": churned / total if total > 0 else 0
                }
        
        return {
            "retention_by_day": retention_by_day,
            "churn_by_type": churn_by_type,
            "current_day": self.current_day
        }
    
    def print_churn_analysis(self):
        """Print detailed churn analysis to console"""
        stats = self.get_churn_statistics()
        
        print("\n" + "="*60)
        print("CHURN ANALYSIS - Time-Based Curves")
        print("="*60)
        
        # Show retention rates for key days
        key_days = [1, 3, 7, 14, 30]
        print("\nRetention Rates by Day:")
        for day in key_days:
            if day in stats["retention_by_day"]:
                retention = stats["retention_by_day"][day]
                churn = (1 - retention) * 100
                print(f"  Day {day:2d}: {retention:.1%} retained ({churn:.1f}% churned)")
        
        # Show churn by player type
        print("\nChurn by Player Type:")
        for player_type, data in stats["churn_by_type"].items():
            print(f"  {player_type.capitalize():8s}: {data['churn_rate']:.1%} churn rate ({data['churned']}/{data['total']} players)")
        
        print("="*60)
    
    def _simulate_whale_behavior(self, player: Player):
        """Simulate whale player behavior - focused on sticker ownership and strategic spending"""
        from player_behaviors import simulate_whale_behavior
        simulate_whale_behavior(self, player)
    
    def _simulate_grinder_behavior(self, player: Player):
        """Simulate grinder player behavior - focused on economy wins via streaks and bonuses"""
        from player_behaviors import simulate_grinder_behavior
        simulate_grinder_behavior(self, player)
    
    def _simulate_casual_behavior(self, player: Player):
        """Simulate casual player behavior - balanced activity across all mechanics"""
        from player_behaviors import simulate_casual_behavior
        simulate_casual_behavior(self, player)
    
    def _simulate_scan_behavior(self, player: Player):
        """Simulate a player scanning stickers with geographic constraints (legacy - once per day)"""
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
        
        # Award points to sticker owner
        if sticker.owner_id in self.players:
            owner = self.players[sticker.owner_id]
            owner.total_points += owner_points
            owner.total_xp += int(owner_points)
            sticker.total_earnings += owner_points
            sticker.daily_earnings += owner_points
        
        # Update sticker stats
        sticker.scans_today += 1
        sticker.total_scans += 1
        sticker.days_since_last_scan = 0
        if sticker.unique_scans_today == 0:
            sticker.unique_scans_today = 1
        
        # Update global stats
        self.total_scans += 1
        self.total_points_earned += scanner_points + owner_points
        
        # Update player's last scan location
        player.last_scan_locations[sticker.id] = player.current_location
        
        # Update player's favorite venues
        if player.favorite_venues is None:
            player.favorite_venues = []
        if sticker.venue_type not in player.favorite_venues:
            player.favorite_venues.append(sticker.venue_type)
        
        # Update player's last activity day
        player.last_activity_day = self.current_day
        
        # Check for social sneeze mode
        if sticker.scans_today >= self.config.social_sneeze_threshold:
            sticker.is_in_sneeze_mode = True
            sticker.sneeze_mode_start_day = self.current_day
        
        # Check for comeback bonus
        if player.days_since_last_scan >= self.config.comeback_bonus_days:
            player.comeback_bonus_active = True
            player.comeback_bonus_remaining = self.config.comeback_bonus_days
        
        # Check for streak bonuses
        if player.days_since_last_scan == 0:
            player.scan_streak_days += 1
        else:
            player.scan_streak_days = 1
        
        # Check for level up
        if player.total_xp >= self._calculate_xp_threshold(player.level + 1):
            player.level += 1
            player.last_level_up_day = self.current_day
            
            # Log level up
            self._log_event(
                "player_level_up",
                f"Player {player.id} leveled up to level {player.level}",
                affected_players=1,
                additional_data={
                    "player_id": player.id,
                    "new_level": player.level,
                    "total_xp": player.total_xp
                }
            )
    
    def _simulate_scan_behavior_per_sticker(self, player: Player, scan_probability: float):
        """Simulate a player attempting to scan each available sticker with given probability"""
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
        
        # Attempt to scan each available sticker with the given probability
        for sticker in available_stickers:
            if random.random() < scan_probability:
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
                
                # Award points to sticker owner
                if sticker.owner_id in self.players:
                    owner = self.players[sticker.owner_id]
                    owner.total_points += owner_points
                    owner.total_xp += int(owner_points)
                    sticker.total_earnings += owner_points
                    sticker.daily_earnings += owner_points
                
                # Update sticker stats
                sticker.scans_today += 1
                sticker.total_scans += 1
                sticker.days_since_last_scan = 0
                if sticker.unique_scans_today == 0:
                    sticker.unique_scans_today = 1
                
                # Update global stats
                self.total_scans += 1
                self.total_points_earned += scanner_points + owner_points
                
                # Update player's last scan location
                player.last_scan_locations[sticker.id] = player.current_location
                
                # Update player's favorite venues
                if player.favorite_venues is None:
                    player.favorite_venues = []
                if sticker.venue_type not in player.favorite_venues:
                    player.favorite_venues.append(sticker.venue_type)
                
                # Update player's last activity day
                player.last_activity_day = self.current_day
                
                # Check for social sneeze mode
                if sticker.scans_today >= self.config.social_sneeze_threshold:
                    sticker.is_in_sneeze_mode = True
                    sticker.sneeze_mode_start_day = self.current_day
                
                # Check for comeback bonus
                if player.days_since_last_scan >= self.config.comeback_bonus_days:
                    player.comeback_bonus_active = True
                    player.comeback_bonus_remaining = self.config.comeback_bonus_days
                
                # Check for streak bonuses
                if player.days_since_last_scan == 0:
                    player.scan_streak_days += 1
                else:
                    player.scan_streak_days = 1
        
        # Check for level up
        if player.total_xp >= self._calculate_xp_threshold(player.level + 1):
            player.level += 1
            player.last_level_up_day = self.current_day
            
            # Log level up
            self._log_event(
                "player_level_up",
                f"Player {player.id} leveled up to level {player.level}",
                affected_players=1,
                additional_data={
                    "player_id": player.id,
                    "new_level": player.level,
                    "total_xp": player.total_xp
                }
            )
    
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
        
        # Apply tiered scan streak bonus (for scanning activity)
        scan_streak_bonus = self._calculate_tiered_scan_streak_bonus(player)
        base_points *= scan_streak_bonus
        
        # Apply tiered activity streak bonus (for any activity)
        activity_streak_bonus = self._calculate_tiered_activity_streak_bonus(player)
        base_points *= activity_streak_bonus
        
        # Apply comeback bonus
        if player.days_since_last_scan >= self.config.comeback_bonus_days:
            base_points *= self.config.comeback_bonus_multiplier
        
        # Apply referral bonus (for players who successfully referred others)
        if player.referral_bonus_remaining > 0:
            base_points *= self.config.referral_reward_multiplier
        
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
        
        # Apply tiered scan streak bonus (for the scanner's scanning activity)
        scan_streak_bonus = self._calculate_tiered_scan_streak_bonus(scanner)
        base_points *= scan_streak_bonus
        
        # Apply tiered activity streak bonus (for the scanner's any activity)
        activity_streak_bonus = self._calculate_tiered_activity_streak_bonus(scanner)
        base_points *= activity_streak_bonus
        
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
            old_level = player.level
            player.level += 1
            player.last_level_up_day = self.current_day  # Track when player leveled up
            
            # Log level up event
            self._log_event(
                "level_up",
                f"Player {player.id} ({player.player_type}) leveled up from {old_level} to {player.level}!",
                affected_players=1,
                additional_data={
                    "player_id": player.id,
                    "player_type": player.player_type,
                    "old_level": old_level,
                    "new_level": player.level,
                    "total_xp": player.total_xp,
                    "xp_threshold": next_level_xp
                }
            )
            
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
                # Note: Reinvestment doesn't generate revenue - it's internal point conversion
                
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
            
            # Log sneeze mode event
            self._log_event(
                "sneeze_mode",
                f"Sticker {sticker.id} entered sneeze mode! {sticker.total_scans} scans triggered {self.config.social_sneeze_bonus}x bonus",
                affected_stickers=1,
                bonus_multiplier=1.0 + self.config.social_sneeze_bonus,
                additional_data={
                    "sticker_id": sticker.id,
                    "owner_id": sticker.owner_id,
                    "venue_type": sticker.venue_type,
                    "scan_threshold": self.config.social_sneeze_threshold,
                    "bonus_multiplier": self.config.social_sneeze_bonus,
                    "duration_hours": self.config.social_sneeze_duration_hours
                }
            )
            
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
    
    def _check_comebacks(self):
        """Check for churned players who might come back"""
        comeback_count = 0
        
        for player in self.players.values():
            # Skip if player is already active
            if player.is_active:
                continue
                
            # Skip if player hasn't been churned long enough
            if player.comeback_eligible_day is None or self.current_day < player.comeback_eligible_day:
                continue
                
            # Check if player comes back (1% chance per day)
            if random.random() < self.config.comeback_probability:
                # Player comes back!
                player.is_active = True
                player.churn_day = None
                player.comeback_eligible_day = None
                
                # Give comeback bonus if not already received
                if not player.has_received_comeback_bonus:
                    player.total_points += self.config.comeback_bonus_points
                    player.has_received_comeback_bonus = True
                    self.total_points_earned += self.config.comeback_bonus_points
                    
                    # Log comeback event
                    self._log_event(
                        "comeback",
                        f"Player {player.id} ({player.player_type}) returned with {self.config.comeback_bonus_points} bonus points!",
                        affected_players=1,
                        additional_data={
                            "player_id": player.id,
                            "player_type": player.player_type,
                            "days_churned": self.current_day - (player.churn_day or 0),
                            "bonus_points": self.config.comeback_bonus_points
                        }
                    )
                
                comeback_count += 1
        
        # Track comebacks for daily stats
        self.comeback_players_today = comeback_count
        
        if comeback_count > 0:
            self._log_event(
                "comeback_batch",
                f"{comeback_count} players returned today!",
                affected_players=comeback_count,
                additional_data={"comeback_count": comeback_count}
            )

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
                
                # Track which players are recruiting (for referral rewards)
                recruiting_player_ids = random.sample([p.id for p in active_players], min(recruiting_players, len(active_players)))
                
                # Log viral spread event
                self._log_event(
                    "viral_spread",
                    f"Viral spread event! {recruiting_players} players recruited {viral_recruits} new players",
                    affected_players=viral_recruits,
                    additional_data={
                        "recruiting_players": recruiting_players,
                        "recruiting_player_ids": recruiting_player_ids,
                        "viral_spread_percentage": self.config.viral_spread_percentage,
                        "days_since_last_viral": self.current_day - self.last_viral_spread_day if self.last_viral_spread_day else 0
                    }
                )
            
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
                        
                        # Log organic growth event
                        if area_organic_new_players > 0:
                            self._log_event(
                                "organic_growth",
                                f"Organic growth in area! {area_organic_new_players} new players from {len(area_stickers)} stickers",
                                affected_players=area_organic_new_players,
                                affected_stickers=len(area_stickers),
                                additional_data={
                                    "area_center": area_center,
                                    "sticker_density_factor": sticker_density_factor,
                                    "organic_rate": daily_organic_rate,
                                    "threshold": self.config.organic_growth_tags_threshold
                                }
                            )
            
            # 3. Event boost for both viral and organic growth
            if self._is_event_active():
                new_players_count = int(new_players_count * 2.0)
            
            # Add new players using the configurable player type ratios
            for i in range(new_players_count):
                player_type = random.choices(
                    list(self.config.new_player_type_ratios.keys()),
                    weights=list(self.config.new_player_type_ratios.values())
                )[0]
                
                # Assign referral if this is from viral spread
                referred_by = None
                if should_trigger_viral and i < len(recruiting_player_ids):
                    referred_by = recruiting_player_ids[i]
                
                self._create_new_player(player_type, referred_by=referred_by)
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
    
    def _create_new_player(self, player_type: str, referred_by: Optional[int] = None):
        """Create a new player with the specified type"""
        player = Player(
            id=self.next_player_id,
            player_type=player_type,
            join_day=self.current_day,
            location=(random.uniform(0, 0.1), random.uniform(0, 0.1)),
            referred_by=referred_by
        )
        
        # Give new players starting assets based on configuration
        player.total_points = self.config.new_player_points
        player.stickers_owned = self.config.new_player_stickers
        if player.player_type == "whale":
            player.wallet_balance = self.config.new_player_whale_wallet_balance
            player.total_spent = self.config.new_player_whale_total_spent
            self.total_revenue += self.config.new_player_whale_total_spent
        
        # Award referral bonus to the referrer
        if referred_by and referred_by in self.players:
            referrer = self.players[referred_by]
            referrer.referrals_made += 1
            referrer.referral_bonus_remaining = self.config.referral_reward_days
            
            # Log referral event
            self._log_event(
                "referral_reward",
                f"Player {referrer.id} earned referral bonus for recruiting player {player.id}",
                affected_players=1,
                additional_data={
                    "referrer_id": referrer.id,
                    "referred_player_id": player.id,
                    "referral_bonus_days": self.config.referral_reward_days,
                    "referral_multiplier": self.config.referral_reward_multiplier
                }
            )
        
        self.players[self.next_player_id] = player
        self.next_player_id += 1
    
    def _is_event_active(self) -> bool:
        """Check if a seasonal event is currently active"""
        if self.current_event is not None:
            return True
        return False
    
    def _log_event(self, event_type: str, description: str, affected_players: int = 0, 
                   affected_stickers: int = 0, bonus_multiplier: float = 1.0, 
                   additional_data: Dict[str, Any] = None):
        """Log a game event"""
        event = GameEvent(
            day=self.current_day,
            event_type=event_type,
            description=description,
            affected_players=affected_players,
            affected_stickers=affected_stickers,
            bonus_multiplier=bonus_multiplier,
            additional_data=additional_data or {}
        )
        self.game_events.append(event)
        self.events_today.append(event)
    
    def _update_events(self):
        """Update special events"""
        if self.current_event is None:
            if random.random() < (1.0 / self.config.event_frequency_days):
                self.current_event = "special_event"
                self.event_start_day = self.current_day
                self._log_event(
                    "seasonal_event",
                    f"Seasonal event started! {self.config.event_bonus_multiplier}x point multiplier for {self.config.event_duration_days} days",
                    bonus_multiplier=self.config.event_bonus_multiplier,
                    additional_data={
                        "duration_days": self.config.event_duration_days,
                        "event_name": "special_event"
                    }
                )
        else:
            if self.current_day - self.event_start_day >= self.config.event_duration_days:
                self._log_event(
                    "seasonal_event_end",
                    f"Seasonal event ended after {self.config.event_duration_days} days",
                    additional_data={"event_name": "special_event"}
                )
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
        
        # Calculate event impacts
        event_impacts = {}
        active_events = []
        
        # Check for active events
        if self.current_event:
            active_events.append("seasonal_event")
            event_impacts["seasonal_event"] = self.config.event_bonus_multiplier
        
        # Count sneeze mode stickers
        sneeze_stickers = [s for s in self.stickers.values() if s.is_in_sneeze_mode]
        if sneeze_stickers:
            active_events.append("sneeze_mode")
            event_impacts["sneeze_mode"] = 1.0 + self.config.social_sneeze_bonus
        
        # Calculate sticker economy analytics
        total_stickers_purchased = sum(p.total_stickers_purchased for p in active_players)
        total_sticker_packs_purchased = sum(p.sticker_packs_purchased for p in active_players)
        total_sticker_packs_earned = sum(p.sticker_packs_earned for p in active_players)
        purchase_to_placement_ratio = total_stickers_purchased / max(self.total_stickers_placed, 1)
        
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
            
            # === STICKER ECONOMY ANALYTICS ===
            total_stickers_purchased=total_stickers_purchased,
            total_sticker_packs_purchased=total_sticker_packs_purchased,
            total_sticker_packs_earned=total_sticker_packs_earned,
            purchase_to_placement_ratio=purchase_to_placement_ratio,
            
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
            players_in_social_hubs=players_in_social_hubs,
            
            # === EVENT TRACKING ===
            events_today=self.events_today.copy(),
            active_events=active_events,
            event_impacts=event_impacts,
            comeback_players_today=self.comeback_players_today
        )
    
    def run_day(self):
        """Run one day of simulation"""
        self.current_day += 1
        
        # Reset daily tracking variables
        self.viral_recruits_today = 0
        self.organic_new_players_today = 0
        self.comeback_players_today = 0
        self.events_today = []  # Reset daily events
        
        # Update events
        self._update_events()
        
        # Add new players
        self._add_new_players()
        
        # Check for player comebacks
        self._check_comebacks()
        
        # Simulate each active player
        for player in list(self.players.values()):
            self._simulate_player_behavior(player)
        
        # Calculate and store daily stats
        daily_stats = self._calculate_daily_stats()
        self.daily_stats.append(daily_stats)
        
        # Stickers remain active even when players churn (no cleanup)
        
        return daily_stats
    
    
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
                        
                        # Print churn analysis every 7 days
                        # if self.current_day % 7 == 0 and self.current_day > 0:
                        #     self.print_churn_analysis()
                    
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
        sneeze_info = f" | Sneeze: {stats.stickers_in_sneeze_mode:,}" if stats.stickers_in_sneeze_mode > 0 else ""
        hub_info = f" | Hubs: {stats.active_social_hubs}" if stats.active_social_hubs > 0 else ""
        print(f"Day {stats.day:4d} | "
              f"Players: {stats.active_players:4,} | "
              f"Revenue: ${stats.total_revenue:8,.2f} | "
              f"Scans: {stats.total_scans:6,} | "
              f"Stickers: {stats.total_stickers_placed:4,} | "
              f"Retention: {stats.retention_rate:.1%} | "
              f"Growth: {stats.growth_rate:+.1%}{sneeze_info}{hub_info}")
    
    def save_simulation_state(self, filename: str = None, timestamp: str = None):
        """Save current simulation state to file"""
        if filename is None:
            if timestamp is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create organized directory structure
            sim_dir = f"simulations/{timestamp}"
            os.makedirs(sim_dir, exist_ok=True)
            # Save in subdirectory for organization
            filename = f"{sim_dir}/fyndr_life_sim_{timestamp}.json"
            # Also save in current directory for analyzer compatibility
            analyzer_filename = f"fyndr_life_sim_{timestamp}.json"
        
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
            "daily_stats": [asdict(s) for s in self.daily_stats],
            "game_events": [asdict(e) for e in self.game_events]
        }
        
        # Save to organized directory
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        # Also save to current directory for analyzer compatibility
        if 'analyzer_filename' in locals():
            with open(analyzer_filename, 'w') as f:
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
            # Import complete simulation analyzer
            from analyze_complete_simulation import CompleteSimulationAnalyzer
            
            # Get timestamp first, then save state with that timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            simulation_prefix = f"fyndr_life_sim_{timestamp}"
            
            # Save the current simulation state with the specific timestamp
            self.save_simulation_state(timestamp=timestamp)
            
            # Create analyzer instance with the same simulation prefix
            analyzer = CompleteSimulationAnalyzer(simulation_prefix)
            
            if not analyzer.all_files:
                print(f"No simulation files found with prefix: {simulation_prefix}")
                return
            
                # Generate complete analysis
                print("Generating complete simulation analysis...")
                analyzer.generate_complete_summary_report()
                analyzer.generate_level_focused_report()
                analyzer.generate_complete_visualizations()
            
            print(f"Complete simulation analysis saved to: {simulation_prefix}_analysis/")
            
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
            print("Warning: analyze_complete_simulation module not found. Skipping analysis.")
        except Exception as e:
            print(f"Error during analysis: {e}")
            print("Continuing without analysis...")
    
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
    parser.add_argument('--deep-simulation', action='store_true', help='Run deep simulation (15 runs averaged)')
    parser.add_argument('--deep-simulations', type=int, default=15, help='Number of simulations for deep mode')
    parser.add_argument('--deep-console-output', action='store_true', help='Enable console output during deep simulation')
    
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
    
    # Check if deep simulation is requested
    if args.deep_simulation:
        # Import and run deep simulation
        from deep_simulation_runner import run_deep_simulation
        
        days_to_run = args.days if args.days is not None else config.max_days
        
        print("Running deep simulation mode...")
        result = run_deep_simulation(
            config_file=args.config,
            okr_results_file=args.okr_results,
            days=days_to_run,
            num_simulations=args.deep_simulations,
            enable_console_output=args.deep_console_output,
            auto_analyze=True
        )
        
        print("\nDeep simulation completed successfully!")
        return
    
    # Regular simulation mode
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
        #if simulator.config.auto_analyze_on_completion:
        #    simulator.run_analysis_on_completion()
        
        print("Simulation completed")

if __name__ == "__main__":
    main()
