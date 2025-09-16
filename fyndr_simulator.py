#!/usr/bin/env python3
"""
FYNDR Game Economy Simulator

A comprehensive simulation tool for testing and refining the FYNDR game economy.
Models player behavior (whales vs grinders), economic mechanics, and various scenarios.

Key Features:
- Player behavior modeling (whales, grinders, casual players)
- Economic mechanics simulation (points, stickers, purchases)
- Configurable parameters for easy testing
- Multiple scenario analysis
- Data export for further analysis
"""

import random
import math
import json
import csv
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, Counter

@dataclass
class GameConfig:
    """Configuration parameters for the game economy"""
    # Base scoring
    owner_base_points: float = 2.0
    scanner_base_points: float = 1.0
    unique_scanner_bonus: float = 1.0
    
    # Diminishing returns
    diminishing_threshold: int = 3  # scans per day per sticker
    diminishing_rates: List[float] = None  # [1.0, 0.5, 0.25] for full, half, quarter
    
    # Diversity bonuses
    geo_diversity_radius: float = 500.0  # meters
    geo_diversity_bonus: float = 1.0
    venue_variety_bonus: float = 1.0
    
    # Social mechanics
    social_sneeze_threshold: int = 3
    social_sneeze_bonus: float = 3.0
    social_sneeze_cap: int = 1  # per chain per week
    
    # Progression
    level_multipliers: List[float] = None  # [1.0, 1.05, 1.10, 1.15, 1.20]
    points_per_level: int = 100
    
    # Economy
    pack_price_points: int = 300
    pack_price_dollars: float = 3.0
    points_per_dollar: float = 100.0  # wallet top-up conversion
    
    # Player behavior
    daily_scan_cap: int = 20
    weekly_earn_cap: int = 500
    
    def __post_init__(self):
        if self.diminishing_rates is None:
            self.diminishing_rates = [1.0, 0.5, 0.25]
        if self.level_multipliers is None:
            self.level_multipliers = [1.0, 1.05, 1.10, 1.15, 1.20]

@dataclass
class Player:
    """Represents a player in the simulation"""
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
    last_scan_locations: Dict[int, Tuple[float, float]] = None  # sticker_id -> (lat, lon)
    
    def __post_init__(self):
        if self.venues_visited_this_week is None:
            self.venues_visited_this_week = set()
        if self.last_scan_locations is None:
            self.last_scan_locations = {}

@dataclass
class Sticker:
    """Represents a sticker in the game"""
    id: int
    owner_id: int
    level: int = 1
    location: Tuple[float, float] = (0.0, 0.0)  # (lat, lon)
    venue_category: str = "general"
    scans_today: int = 0
    unique_scans_today: int = 0
    total_scans: int = 0
    daily_earnings: float = 0.0
    is_active: bool = True

@dataclass
class ScanEvent:
    """Represents a scan event"""
    scanner_id: int
    sticker_id: int
    timestamp: datetime
    location: Tuple[float, float]
    points_earned: float
    bonus_type: str = "base"

class FYNDRSimulator:
    """Main simulator class"""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.players: Dict[int, Player] = {}
        self.stickers: Dict[int, Sticker] = {}
        self.scan_events: List[ScanEvent] = []
        self.current_day = 0
        self.current_week = 0
        self.daily_stats = []
        self.weekly_stats = []
        
    def add_player(self, player_type: str, level: int = 1) -> int:
        """Add a new player to the simulation"""
        player_id = len(self.players) + 1
        player = Player(
            id=player_id,
            player_type=player_type,
            level=level
        )
        self.players[player_id] = player
        return player_id
    
    def add_sticker(self, owner_id: int, location: Tuple[float, float], 
                   venue_category: str = "general", level: int = 1) -> int:
        """Add a new sticker to the simulation"""
        sticker_id = len(self.stickers) + 1
        sticker = Sticker(
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
        """Calculate distance between two locations in meters (simplified)"""
        # Simplified distance calculation (not accurate for real lat/lon)
        return math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2) * 111000  # rough meters
    
    def calculate_scan_points(self, scanner: Player, sticker: Sticker, 
                            scan_location: Tuple[float, float]) -> Tuple[float, str, float]:
        """Calculate points earned from a scan"""
        base_scanner_points = self.config.scanner_base_points
        base_owner_points = self.config.owner_base_points
        
        # Apply level multiplier
        level_mult = self.config.level_multipliers[min(sticker.level - 1, len(self.config.level_multipliers) - 1)]
        base_scanner_points *= level_mult
        base_owner_points *= level_mult
        
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
        
        # Calculate total points
        scanner_points = base_scanner_points + unique_bonus + geo_bonus + venue_bonus
        owner_points = base_owner_points * owner_multiplier
        
        bonus_type = "base"
        if unique_bonus > 0:
            bonus_type = "unique"
        elif geo_bonus > 0:
            bonus_type = "geo_diversity"
        elif venue_bonus > 0:
            bonus_type = "venue_variety"
        
        return scanner_points, bonus_type, owner_points
    
    def simulate_scan(self, scanner_id: int, sticker_id: int, 
                     scan_location: Tuple[float, float]) -> bool:
        """Simulate a scan event"""
        if scanner_id not in self.players or sticker_id not in self.stickers:
            return False
        
        scanner = self.players[scanner_id]
        sticker = self.stickers[sticker_id]
        
        # Check daily caps
        if scanner.scans_today >= self.config.daily_scan_cap:
            return False
        
        # Calculate points
        scanner_points, bonus_type, owner_points = self.calculate_scan_points(
            scanner, sticker, scan_location
        )
        
        # Update sticker stats
        sticker.scans_today += 1
        sticker.total_scans += 1
        if sticker.unique_scans_today == 0:
            sticker.unique_scans_today = 1
        sticker.daily_earnings += owner_points
        
        # Update scanner stats
        scanner.scans_today += 1
        scanner.unique_scans_today += 1
        scanner.daily_points += scanner_points
        scanner.total_points += scanner_points
        scanner.last_scan_locations[sticker.id] = scan_location
        scanner.venues_visited_this_week.add(sticker.venue_category)
        
        # Update owner stats
        owner = self.players[sticker.owner_id]
        owner.daily_points += owner_points
        owner.total_points += owner_points
        
        # Record scan event
        scan_event = ScanEvent(
            scanner_id=scanner_id,
            sticker_id=sticker_id,
            timestamp=datetime.now(),
            location=scan_location,
            points_earned=scanner_points,
            bonus_type=bonus_type
        )
        self.scan_events.append(scan_event)
        
        return True
    
    def simulate_player_behavior(self, player_id: int, day: int):
        """Simulate a player's behavior for a day"""
        player = self.players[player_id]
        
        # Reset daily counters
        player.scans_today = 0
        player.unique_scans_today = 0
        player.daily_points = 0
        
        # Player behavior based on type
        if player.player_type == "whale":
            # Whales: high spending, moderate scanning
            self.simulate_whale_behavior(player, day)
        elif player.player_type == "grinder":
            # Grinders: high scanning, low spending
            self.simulate_grinder_behavior(player, day)
        else:  # casual
            # Casual: moderate scanning, occasional spending
            self.simulate_casual_behavior(player, day)
    
    def simulate_whale_behavior(self, player: Player, day: int):
        """Simulate whale player behavior"""
        # Whales buy packs regularly
        if day % 7 == 0:  # Weekly purchase
            if random.random() < 0.8:  # 80% chance to buy
                packs_bought = random.randint(1, 3)
                cost = packs_bought * self.config.pack_price_dollars
                player.money_spent += cost
                player.stickers_owned += packs_bought * 6  # 6 stickers per pack
                
                # Place some new stickers
                for _ in range(min(packs_bought * 2, 6)):  # Place up to 2 stickers per pack
                    location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                    venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                    self.add_sticker(player.id, location, venue, player.level)
            
            # Weekly reinvestment: $6-12 variable amount
            reinvestment_amount = random.uniform(6.0, 12.0)
            player.money_spent += reinvestment_amount
            # Convert dollars to points for reinvestment
            reinvestment_points = reinvestment_amount * self.config.points_per_dollar
            # Buy packs with reinvestment points
            packs_from_reinvestment = int(reinvestment_points // self.config.pack_price_points)
            if packs_from_reinvestment > 0:
                player.stickers_owned += packs_from_reinvestment * 6
                # Place new stickers from reinvestment
                for _ in range(min(packs_from_reinvestment * 2, 8)):  # Place up to 2 stickers per pack
                    location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                    venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                    self.add_sticker(player.id, location, venue, player.level)
        
        # Moderate scanning activity
        scans_today = random.randint(5, 12)
        for _ in range(scans_today):
            if player.scans_today >= self.config.daily_scan_cap:
                break
            
            # Find a random sticker to scan
            available_stickers = [s for s in self.stickers.values() if s.is_active]
            if available_stickers:
                sticker = random.choice(available_stickers)
                scan_location = (
                    sticker.location[0] + random.uniform(-0.01, 0.01),
                    sticker.location[1] + random.uniform(-0.01, 0.01)
                )
                self.simulate_scan(player.id, sticker.id, scan_location)
    
    def simulate_grinder_behavior(self, player: Player, day: int):
        """Simulate grinder player behavior"""
        # Grinders scan heavily
        scans_today = random.randint(15, 25)
        for _ in range(scans_today):
            if player.scans_today >= self.config.daily_scan_cap:
                break
            
            # Find a random sticker to scan
            available_stickers = [s for s in self.stickers.values() if s.is_active]
            if available_stickers:
                sticker = random.choice(available_stickers)
                scan_location = (
                    sticker.location[0] + random.uniform(-0.01, 0.01),
                    sticker.location[1] + random.uniform(-0.01, 0.01)
                )
                self.simulate_scan(player.id, sticker.id, scan_location)
        
        # Weekly reinvestment: 10% of total points (minimum 1 pack worth)
        if day % 7 == 0:  # Weekly reinvestment
            if player.total_points >= self.config.pack_price_points:
                reinvestment_points = max(int(player.total_points * 0.10), self.config.pack_price_points)
                # Buy packs with reinvestment points
                packs_from_reinvestment = reinvestment_points // self.config.pack_price_points
                if packs_from_reinvestment > 0:
                    player.total_points -= packs_from_reinvestment * self.config.pack_price_points
                    player.stickers_owned += packs_from_reinvestment * 6
                    
                    # Place new stickers from reinvestment
                    for _ in range(min(packs_from_reinvestment * 2, 6)):  # Place up to 2 stickers per pack
                        location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                        venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                        self.add_sticker(player.id, location, venue, player.level)
        
        # Occasional pack purchase with points (less frequent now due to weekly reinvestment)
        if day % 21 == 0 and player.total_points >= self.config.pack_price_points:
            if random.random() < 0.2:  # 20% chance to buy with points (reduced from 30%)
                player.total_points -= self.config.pack_price_points
                player.stickers_owned += 6
                
                # Place new stickers
                for _ in range(3):
                    location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                    venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                    self.add_sticker(player.id, location, venue, player.level)
    
    def simulate_casual_behavior(self, player: Player, day: int):
        """Simulate casual player behavior"""
        # Casual players scan moderately
        scans_today = random.randint(3, 8)
        for _ in range(scans_today):
            if player.scans_today >= self.config.daily_scan_cap:
                break
            
            # Find a random sticker to scan
            available_stickers = [s for s in self.stickers.values() if s.is_active]
            if available_stickers:
                sticker = random.choice(available_stickers)
                scan_location = (
                    sticker.location[0] + random.uniform(-0.01, 0.01),
                    sticker.location[1] + random.uniform(-0.01, 0.01)
                )
                self.simulate_scan(player.id, sticker.id, scan_location)
        
        # Weekly reinvestment: 10% of total points (minimum 1 pack worth)
        if day % 7 == 0:  # Weekly reinvestment
            if player.total_points >= self.config.pack_price_points:
                reinvestment_points = max(int(player.total_points * 0.10), self.config.pack_price_points)
                # Buy packs with reinvestment points
                packs_from_reinvestment = reinvestment_points // self.config.pack_price_points
                if packs_from_reinvestment > 0:
                    player.total_points -= packs_from_reinvestment * self.config.pack_price_points
                    player.stickers_owned += packs_from_reinvestment * 6
                    
                    # Place new stickers from reinvestment
                    for _ in range(min(packs_from_reinvestment * 2, 4)):  # Place up to 2 stickers per pack
                        location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                        venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                        self.add_sticker(player.id, location, venue, player.level)
        
        # Occasional purchase (less frequent now due to weekly reinvestment)
        if day % 28 == 0:  # Every 4 weeks (increased from 3 weeks)
            if random.random() < 0.3:  # 30% chance to buy (reduced from 40%)
                cost = self.config.pack_price_dollars
                player.money_spent += cost
                player.stickers_owned += 6
                
                # Place a few stickers
                for _ in range(2):
                    location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                    venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                    self.add_sticker(player.id, location, venue, player.level)
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        for player in self.players.values():
            player.scans_today = 0
            player.unique_scans_today = 0
            player.daily_points = 0
            player.venues_visited_this_week = set()
        
        for sticker in self.stickers.values():
            sticker.scans_today = 0
            sticker.unique_scans_today = 0
            sticker.daily_earnings = 0.0
    
    def reset_weekly_stats(self):
        """Reset weekly statistics"""
        for player in self.players.values():
            player.weekly_points = 0
    
    def collect_daily_stats(self):
        """Collect daily statistics"""
        daily_stat = {
            'day': self.current_day,
            'total_players': len(self.players),
            'total_stickers': len(self.stickers),
            'total_scans': len([e for e in self.scan_events if e.timestamp.day == self.current_day]),
            'total_points_earned': sum(p.daily_points for p in self.players.values()),
            'total_revenue': sum(p.money_spent for p in self.players.values()),
            'whale_count': len([p for p in self.players.values() if p.player_type == 'whale']),
            'grinder_count': len([p for p in self.players.values() if p.player_type == 'grinder']),
            'casual_count': len([p for p in self.players.values() if p.player_type == 'casual']),
            'avg_points_per_player': statistics.mean([p.daily_points for p in self.players.values()]) if self.players else 0,
            'avg_scans_per_player': statistics.mean([p.scans_today for p in self.players.values()]) if self.players else 0,
        }
        self.daily_stats.append(daily_stat)
        return daily_stat
    
    def run_simulation(self, days: int, initial_players: Dict[str, int] = None):
        """Run the simulation for a specified number of days"""
        if initial_players is None:
            initial_players = {'whale': 10, 'grinder': 50, 'casual': 100}
        
        # Initialize players
        for player_type, count in initial_players.items():
            for _ in range(count):
                player_id = self.add_player(player_type)
                # Give initial stickers
                for _ in range(2):
                    location = (random.uniform(40.0, 41.0), random.uniform(-74.0, -73.0))
                    venue = random.choice(["campus", "coffee", "library", "park", "restaurant"])
                    self.add_sticker(player_id, location, venue)
        
        # Run simulation
        for day in range(1, days + 1):
            self.current_day = day
            self.current_week = (day - 1) // 7 + 1
            
            # Reset daily stats
            self.reset_daily_stats()
            
            # Simulate each player's behavior
            for player_id in self.players:
                self.simulate_player_behavior(player_id, day)
            
            # Collect daily stats
            self.collect_daily_stats()
            
            # Weekly reset
            if day % 7 == 0:
                self.reset_weekly_stats()
    
    def get_economy_summary(self) -> Dict:
        """Get a summary of the economy"""
        total_revenue = sum(p.money_spent for p in self.players.values())
        total_points = sum(p.total_points for p in self.players.values())
        total_scans = len(self.scan_events)
        
        # Player type breakdown
        player_types = Counter(p.player_type for p in self.players.values())
        
        # Revenue by player type
        revenue_by_type = defaultdict(float)
        for player in self.players.values():
            revenue_by_type[player.player_type] += player.money_spent
        
        return {
            'total_revenue': total_revenue,
            'total_points': total_points,
            'total_scans': total_scans,
            'total_players': len(self.players),
            'total_stickers': len(self.stickers),
            'player_types': dict(player_types),
            'revenue_by_type': dict(revenue_by_type),
            'avg_points_per_player': total_points / len(self.players) if self.players else 0,
            'avg_revenue_per_player': total_revenue / len(self.players) if self.players else 0,
            'points_per_scan': total_points / total_scans if total_scans > 0 else 0,
        }
    
    def export_data(self, filename_prefix: str = "fyndr_sim"):
        """Export simulation data to CSV files"""
        # Export daily stats
        with open(f"{filename_prefix}_daily_stats.csv", 'w', newline='') as f:
            if self.daily_stats:
                writer = csv.DictWriter(f, fieldnames=self.daily_stats[0].keys())
                writer.writeheader()
                writer.writerows(self.daily_stats)
        
        # Export player data
        with open(f"{filename_prefix}_players.csv", 'w', newline='') as f:
            if self.players:
                writer = csv.DictWriter(f, fieldnames=['id', 'player_type', 'level', 'total_points', 
                                                     'stickers_owned', 'money_spent'])
                writer.writeheader()
                for player in self.players.values():
                    writer.writerow({
                        'id': player.id,
                        'player_type': player.player_type,
                        'level': player.level,
                        'total_points': player.total_points,
                        'stickers_owned': player.stickers_owned,
                        'money_spent': player.money_spent
                    })
        
        # Export sticker data
        with open(f"{filename_prefix}_stickers.csv", 'w', newline='') as f:
            if self.stickers:
                writer = csv.DictWriter(f, fieldnames=['id', 'owner_id', 'level', 'venue_category', 
                                                     'total_scans', 'is_active'])
                writer.writeheader()
                for sticker in self.stickers.values():
                    writer.writerow({
                        'id': sticker.id,
                        'owner_id': sticker.owner_id,
                        'level': sticker.level,
                        'venue_category': sticker.venue_category,
                        'total_scans': sticker.total_scans,
                        'is_active': sticker.is_active
                    })

def main():
    """Main function to run the simulator"""
    print("FYNDR Game Economy Simulator")
    print("=" * 50)
    
    # Create default configuration
    config = GameConfig()
    
    # Create simulator
    simulator = FYNDRSimulator(config)
    
    # Run simulation
    print("Running 30-day simulation...")
    simulator.run_simulation(30)
    
    # Get and display results
    summary = simulator.get_economy_summary()
    
    print("\nSimulation Results:")
    print(f"Total Revenue: ${summary['total_revenue']:.2f}")
    print(f"Total Points Earned: {summary['total_points']:,}")
    print(f"Total Scans: {summary['total_scans']:,}")
    print(f"Total Players: {summary['total_players']}")
    print(f"Total Stickers: {summary['total_stickers']}")
    
    print(f"\nPlayer Distribution:")
    for player_type, count in summary['player_types'].items():
        print(f"  {player_type.title()}: {count}")
    
    print(f"\nRevenue by Player Type:")
    for player_type, revenue in summary['revenue_by_type'].items():
        print(f"  {player_type.title()}: ${revenue:.2f}")
    
    print(f"\nEconomy Metrics:")
    print(f"  Average Points per Player: {summary['avg_points_per_player']:.1f}")
    print(f"  Average Revenue per Player: ${summary['avg_revenue_per_player']:.2f}")
    print(f"  Points per Scan: {summary['points_per_scan']:.2f}")
    
    # Export data
    simulator.export_data()
    print(f"\nData exported to CSV files.")
    
    return simulator

if __name__ == "__main__":
    simulator = main()