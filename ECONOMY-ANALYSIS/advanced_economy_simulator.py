#!/usr/bin/env python3
"""
Advanced FYNDR Economy Simulator for Long-term Analysis

This simulator is designed to run 270-day simulations to explore optimal sticker rewards
economies for player growth, retention, and organic purchases.

Key Features:
- Comprehensive parameter variation system
- Long-term simulation capabilities (270+ days)
- Advanced player behavior modeling with retention mechanics
- Detailed analytics for growth, retention, and monetization
- Multi-objective optimization support
"""

import random
import math
import json
import csv
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, Counter
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp

@dataclass
class AdvancedGameConfig:
    """Advanced configuration parameters for comprehensive economy testing"""
    
    # === CORE SCORING PARAMETERS ===
    owner_base_points: float = 2.0
    scanner_base_points: float = 1.0
    unique_scanner_bonus: float = 1.0
    
    # === DIMINISHING RETURNS ===
    diminishing_threshold: int = 3
    diminishing_rates: List[float] = None  # [1.0, 0.5, 0.25]
    
    # === DIVERSITY BONUSES ===
    geo_diversity_radius: float = 500.0  # meters
    geo_diversity_bonus: float = 1.0
    venue_variety_bonus: float = 1.0
    
    # === SOCIAL MECHANICS ===
    social_sneeze_threshold: int = 3
    social_sneeze_bonus: float = 3.0
    social_sneeze_cap: int = 1
    
    # === PROGRESSION SYSTEM ===
    level_multipliers: List[float] = None  # [1.0, 1.05, 1.10, 1.15, 1.20]
    points_per_level: int = 100
    max_level: int = 20
    
    # === ECONOMY PARAMETERS ===
    pack_price_points: int = 300
    pack_price_dollars: float = 3.0
    points_per_dollar: float = 100.0
    wallet_topup_min: float = 5.0
    wallet_topup_max: float = 50.0
    
    # === PLAYER BEHAVIOR CAPS ===
    # Removed daily_scan_cap - replaced with per-sticker cooldown
    # daily_scan_cap: int = 20
    weekly_earn_cap: int = 500
    daily_passive_cap: int = 100  # Max points from passive sticker earnings
    sticker_scan_cooldown_hours: int = 11  # Hours between scans of same sticker by same player
    
    # === RETENTION MECHANICS ===
    churn_probability_base: float = 0.001  # Daily base churn rate
    churn_probability_whale: float = 0.0005  # Lower for whales
    churn_probability_grinder: float = 0.0008  # Higher for grinders
    churn_probability_casual: float = 0.002  # Highest for casual
    
    # === ENGAGEMENT BONUSES ===
    streak_bonus_days: int = 7
    streak_bonus_multiplier: float = 1.5
    comeback_bonus_days: int = 3  # Days away to trigger comeback bonus
    comeback_bonus_multiplier: float = 2.0
    
    # === STICKER DECAY ===
    # Removed sticker decay - no longer needed
    # sticker_decay_rate: float = 0.1  # 10% decay per day without scans
    # sticker_min_value: float = 0.1  # Minimum value before becoming inactive
    
    # === NEW PLAYER ONBOARDING ===
    new_player_bonus_days: int = 7
    new_player_bonus_multiplier: float = 2.0
    new_player_free_packs: int = 1
    
    # === SEASONAL EVENTS ===
    event_frequency_days: int = 30  # Every 30 days
    event_duration_days: int = 7
    event_bonus_multiplier: float = 1.5
    
    # === POPULATION & SPREAD MECHANICS ===
    # Population variables for modeling game spread in a locale
    total_population: int = 100000  # Total population of the area
    population_density_per_quarter_sq_mile: float = 25000.0  # Population density per quarter square mile
    
    # Viral spread mechanics
    viral_spread_percentage: float = 0.40  # 40% of active players recruit new players
    viral_spread_frequency_days: int = 14  # Every 2 weeks
    viral_spread_cap_percentage: float = 0.40  # Maximum 40% of total population can be players
    
    # Organic growth mechanics
    organic_growth_rate_min: float = 0.0002  # 0.02% minimum organic growth per 200 tags per week
    organic_growth_rate_max: float = 0.0005  # 0.05% maximum organic growth per 200 tags per week
    organic_growth_tags_threshold: int = 200  # Number of tags required for organic growth calculation
    
    # Player type distribution for new players
    new_player_type_ratios: Dict[str, float] = None  # Will be set in __post_init__
    
    def __post_init__(self):
        if self.diminishing_rates is None:
            self.diminishing_rates = [1.0, 0.5, 0.25]
        if self.level_multipliers is None:
            self.level_multipliers = [1.0, 1.05, 1.10, 1.15, 1.20]
        if self.new_player_type_ratios is None:
            self.new_player_type_ratios = {
                'whale': 0.05,    # 5% whales
                'grinder': 0.25,  # 25% grinders  
                'casual': 0.70    # 70% casual
            }

@dataclass
class AdvancedPlayer:
    """Enhanced player model with retention and engagement tracking"""
    id: int
    player_type: str  # 'whale', 'grinder', 'casual'
    level: int = 1
    total_points: int = 0
    daily_points: int = 0
    weekly_points: int = 0
    stickers_owned: int = 0
    stickers_placed: int = 0
    money_spent: float = 0.0
    scans_today: int = 0
    unique_scans_today: int = 0
    venues_visited_this_week: set = None
    last_scan_locations: Dict[int, Tuple[float, float]] = None
    last_scan_times: Dict[int, int] = None  # sticker_id -> last_scan_day
    
    # === RETENTION TRACKING ===
    days_since_last_activity: int = 0
    total_days_active: int = 0
    consecutive_days_active: int = 0
    max_consecutive_days: int = 0
    is_active: bool = True
    churn_probability: float = 0.001
    
    # === ENGAGEMENT METRICS ===
    total_scans: int = 0
    total_unique_scans: int = 0
    total_revenue_generated: float = 0.0  # Revenue from their stickers being scanned
    last_scan_day: int = 0
    last_purchase_day: int = 0
    
    # === NEW PLAYER TRACKING ===
    is_new_player: bool = True
    new_player_bonus_remaining: int = 7
    
    def __post_init__(self):
        if self.venues_visited_this_week is None:
            self.venues_visited_this_week = set()
        if self.last_scan_locations is None:
            self.last_scan_locations = {}
        if self.last_scan_times is None:
            self.last_scan_times = {}

@dataclass
class AdvancedSticker:
    """Enhanced sticker model with decay and value tracking"""
    id: int
    owner_id: int
    level: int = 1
    location: Tuple[float, float] = (0.0, 0.0)
    venue_category: str = "general"
    scans_today: int = 0
    unique_scans_today: int = 0
    total_scans: int = 0
    daily_earnings: float = 0.0
    is_active: bool = True
    
    # === VALUE TRACKING ===
    base_value: float = 1.0
    current_value: float = 1.0
    total_earnings: float = 0.0

class AdvancedFYNDRSimulator:
    """Advanced simulator for long-term economy analysis"""
    
    def __init__(self, config: AdvancedGameConfig):
        self.config = config
        self.players: Dict[int, AdvancedPlayer] = {}
        self.stickers: Dict[int, AdvancedSticker] = {}
        self.scan_events: List = []
        self.current_day = 0
        self.current_week = 0
        self.daily_stats = []
        self.weekly_stats = []
        
        # === RETENTION TRACKING ===
        self.total_players_ever = 0
        self.churned_players = 0
        self.retained_players = 0
        
        # === GROWTH TRACKING ===
        self.new_players_today = 0
        self.returning_players_today = 0
        
        # === ECONOMY TRACKING ===
        self.total_revenue = 0.0
        self.organic_purchases = 0
        self.whale_purchases = 0
        self.grinder_purchases = 0
        self.casual_purchases = 0
        
        # === POPULATION & SPREAD TRACKING ===
        self.viral_recruits_today = 0
        self.organic_new_players_today = 0
        self.max_possible_players = int(self.config.total_population * self.config.viral_spread_cap_percentage)
    
    def add_player(self, player_type: str, level: int = 1, is_new: bool = True) -> int:
        """Add a new player to the simulation"""
        player_id = len(self.players) + 1
        self.total_players_ever += 1
        
        player = AdvancedPlayer(
            id=player_id,
            player_type=player_type,
            level=level,
            is_new_player=is_new,
            new_player_bonus_remaining=7 if is_new else 0
        )
        
        # Set churn probability based on player type
        if player_type == "whale":
            player.churn_probability = self.config.churn_probability_whale
        elif player_type == "grinder":
            player.churn_probability = self.config.churn_probability_grinder
        else:
            player.churn_probability = self.config.churn_probability_casual
        
        self.players[player_id] = player
        return player_id
    
    def add_sticker(self, owner_id: int, location: Tuple[float, float], 
                   venue_category: str = "general", level: int = 1) -> int:
        """Add a new sticker to the simulation"""
        sticker_id = len(self.stickers) + 1
        sticker = AdvancedSticker(
            id=sticker_id,
            owner_id=owner_id,
            level=level,
            location=location,
            venue_category=venue_category
        )
        self.stickers[sticker_id] = sticker
        self.players[owner_id].stickers_owned += 1
        return sticker_id
    
    def calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate distance between two locations in meters"""
        return math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2) * 111000
    
    def calculate_scan_points(self, scanner: AdvancedPlayer, sticker: AdvancedSticker, 
                            scan_location: Tuple[float, float]) -> Tuple[float, str, float]:
        """Calculate points earned from a scan with advanced mechanics"""
        base_scanner_points = self.config.scanner_base_points
        base_owner_points = self.config.owner_base_points
        
        # Apply level multiplier
        level_mult = self.config.level_multipliers[min(sticker.level - 1, len(self.config.level_multipliers) - 1)]
        base_scanner_points *= level_mult
        base_owner_points *= level_mult
        
        # Apply sticker decay
        sticker_value_mult = sticker.current_value
        base_scanner_points *= sticker_value_mult
        base_owner_points *= sticker_value_mult
        
        # Diminishing returns for sticker
        if sticker.scans_today < self.config.diminishing_threshold:
            owner_multiplier = self.config.diminishing_rates[0]
        elif sticker.scans_today < self.config.diminishing_threshold * 2:
            owner_multiplier = self.config.diminishing_rates[1]
        else:
            owner_multiplier = self.config.diminishing_rates[2]
        
        # Unique scanner bonus
        unique_bonus = 0.0
        if sticker.unique_scans_today == 0:
            unique_bonus = self.config.unique_scanner_bonus
        
        # Geo diversity bonus
        geo_bonus = 0.0
        if sticker.id in scanner.last_scan_locations:
            last_location = scanner.last_scan_locations[sticker.id]
            distance = self.calculate_distance(last_location, scan_location)
            if distance > self.config.geo_diversity_radius:
                geo_bonus = self.config.geo_diversity_bonus
        
        # Venue variety bonus
        venue_bonus = 0.0
        if sticker.venue_category not in scanner.venues_visited_this_week:
            venue_bonus = self.config.venue_variety_bonus
        
        # New player bonus
        new_player_bonus = 0.0
        if scanner.is_new_player and scanner.new_player_bonus_remaining > 0:
            new_player_bonus = self.config.new_player_bonus_multiplier - 1.0
        
        # Streak bonus
        streak_bonus = 0.0
        if scanner.consecutive_days_active >= self.config.streak_bonus_days:
            streak_bonus = self.config.streak_bonus_multiplier - 1.0
        
        # Comeback bonus
        comeback_bonus = 0.0
        if scanner.days_since_last_activity >= self.config.comeback_bonus_days:
            comeback_bonus = self.config.comeback_bonus_multiplier - 1.0
        
        # Event bonus
        event_bonus = 0.0
        if self.is_event_active():
            event_bonus = self.config.event_bonus_multiplier - 1.0
        
        # Calculate total points
        total_bonus = unique_bonus + geo_bonus + venue_bonus + new_player_bonus + streak_bonus + comeback_bonus + event_bonus
        scanner_points = base_scanner_points * (1 + total_bonus)
        owner_points = base_owner_points * owner_multiplier * (1 + total_bonus)
        
        bonus_type = "base"
        if unique_bonus > 0:
            bonus_type = "unique"
        elif geo_bonus > 0:
            bonus_type = "geo_diversity"
        elif venue_bonus > 0:
            bonus_type = "venue_variety"
        elif new_player_bonus > 0:
            bonus_type = "new_player"
        elif streak_bonus > 0:
            bonus_type = "streak"
        elif comeback_bonus > 0:
            bonus_type = "comeback"
        elif event_bonus > 0:
            bonus_type = "event"
        
        return scanner_points, bonus_type, owner_points
    
    def is_event_active(self) -> bool:
        """Check if a seasonal event is currently active"""
        if self.current_day % self.config.event_frequency_days == 0:
            return True
        event_start = (self.current_day // self.config.event_frequency_days) * self.config.event_frequency_days
        return self.current_day - event_start < self.config.event_duration_days
    
    def simulate_scan(self, scanner_id: int, sticker_id: int, 
                     scan_location: Tuple[float, float]) -> bool:
        """Simulate a scan event with advanced mechanics"""
        if scanner_id not in self.players or sticker_id not in self.stickers:
            return False
        
        scanner = self.players[scanner_id]
        sticker = self.stickers[sticker_id]
        
        # Check per-sticker cooldown (11 hours = ~0.46 days)
        cooldown_days = self.config.sticker_scan_cooldown_hours / 24.0
        if sticker_id in scanner.last_scan_times:
            days_since_last_scan = self.current_day - scanner.last_scan_times[sticker_id]
            if days_since_last_scan < cooldown_days:
                return False
        
        # Calculate points
        scanner_points, bonus_type, owner_points = self.calculate_scan_points(
            scanner, sticker, scan_location
        )
        
        # Update sticker stats
        sticker.scans_today += 1
        sticker.total_scans += 1
        sticker.days_since_last_scan = 0
        if sticker.unique_scans_today == 0:
            sticker.unique_scans_today = 1
        sticker.daily_earnings += owner_points
        sticker.total_earnings += owner_points
        
        # Update scanner stats
        scanner.scans_today += 1
        scanner.unique_scans_today += 1
        scanner.daily_points += scanner_points
        scanner.total_points += scanner_points
        scanner.total_scans += 1
        scanner.last_scan_locations[sticker.id] = scan_location
        scanner.last_scan_times[sticker.id] = self.current_day
        scanner.venues_visited_this_week.add(sticker.venue_category)
        scanner.last_scan_day = self.current_day
        scanner.days_since_last_activity = 0
        
        # Update owner stats
        owner = self.players[sticker.owner_id]
        owner.daily_points += owner_points
        owner.total_points += owner_points
        owner.total_revenue_generated += owner_points
        
        return True
    
    def simulate_player_behavior(self, player_id: int, day: int):
        """Simulate a player's behavior for a day with retention mechanics"""
        player = self.players[player_id]
        
        # Check for churn
        if random.random() < player.churn_probability:
            player.is_active = False
            self.churned_players += 1
            return
        
        # Reset daily counters
        player.scans_today = 0
        player.unique_scans_today = 0
        player.daily_points = 0
        
        # Update activity tracking
        player.total_days_active += 1
        player.consecutive_days_active += 1
        player.max_consecutive_days = max(player.max_consecutive_days, player.consecutive_days_active)
        player.days_since_last_activity = 0
        
        # Update new player status
        if player.is_new_player and player.new_player_bonus_remaining > 0:
            player.new_player_bonus_remaining -= 1
            if player.new_player_bonus_remaining == 0:
                player.is_new_player = False
        
        # Player behavior based on type
        if player.player_type == "whale":
            self.simulate_whale_behavior(player, day)
        elif player.player_type == "grinder":
            self.simulate_grinder_behavior(player, day)
        else:  # casual
            self.simulate_casual_behavior(player, day)
    
    def simulate_whale_behavior(self, player: AdvancedPlayer, day: int):
        """Simulate whale player behavior with enhanced mechanics"""
        # Whales buy packs regularly
        if day % 7 == 0:  # Weekly purchase
            if random.random() < 0.8:  # 80% chance to buy
                packs_bought = random.randint(1, 3)
                cost = packs_bought * self.config.pack_price_dollars
                player.money_spent += cost
                player.total_revenue_generated += cost
                self.total_revenue += cost
                self.whale_purchases += 1
                player.stickers_owned += packs_bought * 6
                player.last_purchase_day = day
                
                # Place some new stickers
                for _ in range(min(packs_bought * 2, 6)):
                    location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                    venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                    self.add_sticker(player.id, location, venue, player.level)
            
            # Weekly reinvestment
            reinvestment_amount = random.uniform(6.0, 12.0)
            player.money_spent += reinvestment_amount
            self.total_revenue += reinvestment_amount
            self.whale_purchases += 1
            reinvestment_points = reinvestment_amount * self.config.points_per_dollar
            packs_from_reinvestment = int(reinvestment_points // self.config.pack_price_points)
            if packs_from_reinvestment > 0:
                player.stickers_owned += packs_from_reinvestment * 6
                for _ in range(min(packs_from_reinvestment * 2, 8)):
                    location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                    venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                    self.add_sticker(player.id, location, venue, player.level)
        
        # Moderate scanning activity
        scans_today = random.randint(5, 12)
        for _ in range(scans_today):
            
            available_stickers = [s for s in self.stickers.values() if s.is_active]
            if available_stickers:
                sticker = random.choice(available_stickers)
                scan_location = (
                    sticker.location[0] + random.uniform(-0.01, 0.01),
                    sticker.location[1] + random.uniform(-0.01, 0.01)
                )
                self.simulate_scan(player.id, sticker.id, scan_location)
    
    def simulate_grinder_behavior(self, player: AdvancedPlayer, day: int):
        """Simulate grinder player behavior with enhanced mechanics"""
        # Grinders scan heavily
        scans_today = random.randint(15, 25)
        for _ in range(scans_today):
            
            available_stickers = [s for s in self.stickers.values() if s.is_active]
            if available_stickers:
                sticker = random.choice(available_stickers)
                scan_location = (
                    sticker.location[0] + random.uniform(-0.01, 0.01),
                    sticker.location[1] + random.uniform(-0.01, 0.01)
                )
                self.simulate_scan(player.id, sticker.id, scan_location)
        
        # Weekly reinvestment
        if day % 7 == 0:
            if player.total_points >= self.config.pack_price_points:
                reinvestment_points = max(int(player.total_points * 0.10), self.config.pack_price_points)
                packs_from_reinvestment = reinvestment_points // self.config.pack_price_points
                if packs_from_reinvestment > 0:
                    player.total_points -= packs_from_reinvestment * self.config.pack_price_points
                    player.stickers_owned += packs_from_reinvestment * 6
                    self.organic_purchases += 1
                    self.grinder_purchases += 1
                    
                    for _ in range(min(packs_from_reinvestment * 2, 6)):
                        location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                        venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                        self.add_sticker(player.id, location, venue, player.level)
        
        # Occasional pack purchase with points
        if day % 21 == 0 and player.total_points >= self.config.pack_price_points:
            if random.random() < 0.2:
                player.total_points -= self.config.pack_price_points
                player.stickers_owned += 6
                self.organic_purchases += 1
                self.grinder_purchases += 1
                
                for _ in range(3):
                    location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                    venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                    self.add_sticker(player.id, location, venue, player.level)
    
    def simulate_casual_behavior(self, player: AdvancedPlayer, day: int):
        """Simulate casual player behavior with enhanced mechanics"""
        # Casual players scan moderately
        scans_today = random.randint(3, 8)
        for _ in range(scans_today):
            
            available_stickers = [s for s in self.stickers.values() if s.is_active]
            if available_stickers:
                sticker = random.choice(available_stickers)
                scan_location = (
                    sticker.location[0] + random.uniform(-0.01, 0.01),
                    sticker.location[1] + random.uniform(-0.01, 0.01)
                )
                self.simulate_scan(player.id, sticker.id, scan_location)
        
        # Weekly reinvestment
        if day % 7 == 0:
            if player.total_points >= self.config.pack_price_points:
                reinvestment_points = max(int(player.total_points * 0.10), self.config.pack_price_points)
                packs_from_reinvestment = reinvestment_points // self.config.pack_price_points
                if packs_from_reinvestment > 0:
                    player.total_points -= packs_from_reinvestment * self.config.pack_price_points
                    player.stickers_owned += packs_from_reinvestment * 6
                    self.organic_purchases += 1
                    self.casual_purchases += 1
                    
                    for _ in range(min(packs_from_reinvestment * 2, 4)):
                        location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                        venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                        self.add_sticker(player.id, location, venue, player.level)
        
        # Occasional purchase
        if day % 28 == 0:
            if random.random() < 0.3:
                cost = self.config.pack_price_dollars
                player.money_spent += cost
                self.total_revenue += cost
                self.organic_purchases += 1
                self.casual_purchases += 1
                player.stickers_owned += 6
                player.last_purchase_day = day
                
                for _ in range(2):
                    location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                    venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                    self.add_sticker(player.id, location, venue, player.level)
    
    # Removed update_sticker_decay - no longer needed
    
    def simulate_new_player_growth(self, day: int):
        """Simulate new player acquisition with population and spread mechanics"""
        current_players = len([p for p in self.players.values() if p.is_active])
        
        # Check if we've reached the population cap
        if current_players >= self.max_possible_players:
            return
        
        new_players_count = 0
        
        # 1. Viral spread mechanics (40% of active players recruit 1 new player per 2 weeks)
        if day % self.config.viral_spread_frequency_days == 0:
            active_players = [p for p in self.players.values() if p.is_active]
            recruiting_players = int(len(active_players) * self.config.viral_spread_percentage)
            viral_recruits = min(recruiting_players, self.max_possible_players - current_players)
            new_players_count += viral_recruits
            self.viral_recruits_today = viral_recruits
        
        # 2. Organic growth based on sticker activity (0.02-0.05% per 200 tags per week)
        if day % 7 == 0:  # Weekly organic growth
            total_active_stickers = len([s for s in self.stickers.values() if s.is_active])
            if total_active_stickers >= self.config.organic_growth_tags_threshold:
                # Calculate organic growth rate based on sticker density
                sticker_density_factor = min(total_active_stickers / self.config.organic_growth_tags_threshold, 3.0)
                organic_rate = random.uniform(
                    self.config.organic_growth_rate_min,
                    self.config.organic_growth_rate_max
                ) * sticker_density_factor
                
                # Apply to total population, not just current players
                organic_new_players = int(self.config.total_population * organic_rate)
                organic_new_players = min(organic_new_players, self.max_possible_players - current_players - new_players_count)
                new_players_count += organic_new_players
                self.organic_new_players_today = organic_new_players
        
        # 3. Event boost for both viral and organic growth
        if self.is_event_active():
            new_players_count = int(new_players_count * 2.0)
        
        # Add new players using the configurable player type ratios
        for _ in range(new_players_count):
            player_type = random.choices(
                list(self.config.new_player_type_ratios.keys()),
                weights=list(self.config.new_player_type_ratios.values())
            )[0]
            self.add_player(player_type, is_new=True)
            self.new_players_today += 1
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        for player in self.players.values():
            if player.is_active:
                player.scans_today = 0
                player.unique_scans_today = 0
                player.daily_points = 0
                player.venues_visited_this_week = set()
            else:
                player.days_since_last_activity += 1
        
        for sticker in self.stickers.values():
            sticker.scans_today = 0
            sticker.unique_scans_today = 0
            sticker.daily_earnings = 0.0
        
        # Reset population tracking variables
        self.viral_recruits_today = 0
        self.organic_new_players_today = 0
    
    def collect_daily_stats(self):
        """Collect comprehensive daily statistics"""
        active_players = [p for p in self.players.values() if p.is_active]
        
        daily_stat = {
            'day': self.current_day,
            'total_players': len(active_players),
            'total_players_ever': self.total_players_ever,
            'churned_players': self.churned_players,
            'retained_players': len(active_players),
            'retention_rate': len(active_players) / max(self.total_players_ever, 1),
            'new_players_today': self.new_players_today,
            'returning_players_today': self.returning_players_today,
            'total_stickers': len([s for s in self.stickers.values() if s.is_active]),
            'total_scans': len([e for e in self.scan_events if e.timestamp.day == self.current_day]),
            'total_points_earned': sum(p.daily_points for p in active_players),
            'total_revenue': self.total_revenue,
            'organic_purchases': self.organic_purchases,
            'whale_purchases': self.whale_purchases,
            'grinder_purchases': self.grinder_purchases,
            'casual_purchases': self.casual_purchases,
            'whale_count': len([p for p in active_players if p.player_type == 'whale']),
            'grinder_count': len([p for p in active_players if p.player_type == 'grinder']),
            'casual_count': len([p for p in active_players if p.player_type == 'casual']),
            'avg_points_per_player': statistics.mean([p.daily_points for p in active_players]) if active_players else 0,
            'avg_scans_per_player': statistics.mean([p.scans_today for p in active_players]) if active_players else 0,
            'avg_consecutive_days': statistics.mean([p.consecutive_days_active for p in active_players]) if active_players else 0,
            'event_active': self.is_event_active(),
            
            # === POPULATION & SPREAD METRICS ===
            'total_population': self.config.total_population,
            'population_density': self.config.population_density_per_quarter_sq_mile,
            'max_possible_players': self.max_possible_players,
            'population_penetration_rate': len(active_players) / self.config.total_population,
            'viral_recruits_today': self.viral_recruits_today,
            'organic_new_players_today': self.organic_new_players_today,
            'population_cap_reached': len(active_players) >= self.max_possible_players,
        }
        self.daily_stats.append(daily_stat)
        return daily_stat
    
    def run_simulation(self, days: int, initial_players: Dict[str, int] = None):
        """Run the advanced simulation for a specified number of days"""
        if initial_players is None:
            initial_players = {'whale': 10, 'grinder': 50, 'casual': 100}
        
        # Initialize players
        for player_type, count in initial_players.items():
            for _ in range(count):
                player_id = self.add_player(player_type, is_new=False)
                # Give initial stickers
                for _ in range(2):
                    location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                    venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                    self.add_sticker(player_id, location, venue)
        
        # Run simulation
        for day in range(1, days + 1):
            self.current_day = day
            self.current_week = (day - 1) // 7 + 1
            self.new_players_today = 0
            self.returning_players_today = 0
            
            # Reset daily stats
            self.reset_daily_stats()
            
            # Simulate new player growth
            self.simulate_new_player_growth(day)
            
            # Simulate each active player's behavior
            for player_id in list(self.players.keys()):
                if self.players[player_id].is_active:
                    self.simulate_player_behavior(player_id, day)
            
            # Collect daily stats
            self.collect_daily_stats()
            
            # Weekly reset
            if day % 7 == 0:
                for player in self.players.values():
                    if player.is_active:
                        player.weekly_points = 0
    
    def get_economy_summary(self) -> Dict:
        """Get a comprehensive summary of the economy"""
        active_players = [p for p in self.players.values() if p.is_active]
        total_revenue = sum(p.money_spent for p in active_players)
        total_points = sum(p.total_points for p in active_players)
        total_scans = len(self.scan_events)
        
        # Player type breakdown
        player_types = Counter(p.player_type for p in active_players)
        
        # Revenue by player type
        revenue_by_type = defaultdict(float)
        for player in active_players:
            revenue_by_type[player.player_type] += player.money_spent
        
        # Retention metrics
        retention_rate = len(active_players) / max(self.total_players_ever, 1)
        
        # Growth metrics
        total_growth = self.total_players_ever - len(active_players)
        
        # Average level calculation
        avg_level = statistics.mean([p.level for p in active_players]) if active_players else 1
        
        return {
            'total_revenue': total_revenue,
            'total_points': total_points,
            'total_scans': total_scans,
            'total_players': len(active_players),
            'total_players_ever': self.total_players_ever,
            'retention_rate': retention_rate,
            'churn_rate': 1 - retention_rate,
            'total_growth': total_growth,
            'total_stickers': len([s for s in self.stickers.values() if s.is_active]),
            'player_types': dict(player_types),
            'revenue_by_type': dict(revenue_by_type),
            'organic_purchases': self.organic_purchases,
            'whale_purchases': self.whale_purchases,
            'grinder_purchases': self.grinder_purchases,
            'casual_purchases': self.casual_purchases,
            'avg_points_per_player': total_points / len(active_players) if active_players else 0,
            'avg_revenue_per_player': total_revenue / len(active_players) if active_players else 0,
            'points_per_scan': total_points / total_scans if total_scans > 0 else 0,
            'organic_purchase_rate': self.organic_purchases / max(len(active_players), 1),
            'avg_level': avg_level,
            'whale_count': player_types.get('whale', 0),
            'grinder_count': player_types.get('grinder', 0),
            'casual_count': player_types.get('casual', 0),
            
            # === POPULATION & SPREAD METRICS ===
            'total_population': self.config.total_population,
            'population_density': self.config.population_density_per_quarter_sq_mile,
            'max_possible_players': self.max_possible_players,
            'population_penetration_rate': len(active_players) / self.config.total_population,
            'population_cap_reached': len(active_players) >= self.max_possible_players,
            'viral_spread_rate': self.config.viral_spread_percentage,
            'organic_growth_rate_range': f"{self.config.organic_growth_rate_min*100:.3f}%-{self.config.organic_growth_rate_max*100:.3f}%",
        }
