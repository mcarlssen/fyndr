#!/usr/bin/env python3
"""
Deep Simulation Runner for FYNDR Life Simulator

This module provides functionality to run multiple simulations and average their results
to reduce variance from minmax spreads and provide more stable analysis.

Key Features:
- Runs 15 simulations with the same configuration
- Averages all simulation data (daily stats, players, stickers)
- Executes analysis on the averaged results
- Provides optional deep simulation mode
"""

import json
import os
import time
import random
import statistics
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# Import the main simulator and analyzer
from fyndr_life_simulator import FYNDRLifeSimulator, LifeSimConfig
from analyze_complete_simulation import CompleteSimulationAnalyzer


@dataclass
class AveragedDailyStats:
    """Averaged daily statistics across multiple simulations"""
    day: int
    total_players: float
    active_players: float
    new_players: float
    churned_players: float
    total_revenue: float
    total_points_earned: float
    total_scans: float
    total_stickers_placed: float
    player_type_counts: Dict[str, float]
    revenue_by_type: Dict[str, float]
    avg_level: float
    retention_rate: float
    growth_rate: float
    
    # Sticker economy analytics
    total_stickers_purchased: float = 0.0
    total_sticker_packs_purchased: float = 0.0
    total_sticker_packs_earned: float = 0.0
    purchase_to_placement_ratio: float = 0.0
    
    # Population & spread metrics
    total_population: float = 100000.0
    population_density: float = 25000.0
    max_possible_players: float = 40000.0
    population_penetration_rate: float = 0.0
    viral_recruits_today: float = 0.0
    organic_new_players_today: float = 0.0
    population_cap_reached: bool = False
    
    # Sticker density tracking
    current_sticker_density: float = 0.0
    max_stickers_allowed: float = 0.0
    sticker_density_cap_reached: bool = False
    
    # Social sneeze mode tracking
    stickers_in_sneeze_mode: float = 0.0
    sneeze_mode_hotspots: List[Tuple[float, float]] = None
    
    # Social hub tracking
    active_social_hubs: float = 0.0
    social_hub_locations: List[Tuple[float, float]] = None
    players_in_social_hubs: float = 0.0
    
    # Event tracking
    events_today: List[Any] = None
    active_events: List[str] = None
    event_impacts: Dict[str, float] = None
    
    # Comeback tracking
    comeback_players_today: float = 0.0


@dataclass
class AveragedPlayer:
    """Averaged player data across multiple simulations"""
    id: int
    player_type: str
    level: float = 1.0
    total_points: float = 0.0
    total_xp: float = 0.0
    wallet_balance: float = 0.0
    total_spent: float = 0.0
    stickers_placed: float = 0.0
    stickers_scanned: float = 0.0
    days_active: float = 0.0
    days_since_last_scan: float = 0.0
    days_since_last_placement: float = 0.0
    
    # Sticker inventory tracking
    stickers_owned: float = 0.0
    sticker_packs_purchased: float = 0.0
    sticker_packs_earned: float = 0.0
    total_stickers_purchased: float = 0.0
    
    # Streak tracking
    streak_days: float = 0.0
    scan_streak_days: float = 0.0
    placement_streak_days: float = 0.0
    last_activity_day: float = 0.0
    scanned_today: bool = False
    placed_today: bool = False
    last_scan_times: Dict[str, float] = None
    favorite_venues: List[str] = None
    location: Tuple[float, float] = None
    join_day: float = 0.0
    is_active: bool = True
    churn_day: Optional[int] = None
    
    # Movement pattern tracking
    home_location: Tuple[float, float] = None
    work_location: Tuple[float, float] = None
    social_hubs: List[Tuple[float, float]] = None
    daily_routine: List[Tuple[float, float]] = None
    current_location: Tuple[float, float] = None
    last_movement_time: float = 0.0
    movement_speed: float = 1.0
    
    # Referral tracking
    referred_by: Optional[int] = None
    referrals_made: float = 0.0
    referral_bonus_remaining: float = 0.0
    
    # Comeback tracking
    comeback_eligible_day: Optional[int] = None
    has_received_comeback_bonus: bool = False
    
    # Level-up tracking
    last_level_up_day: Optional[int] = None


@dataclass
class AveragedSticker:
    """Averaged sticker data across multiple simulations"""
    id: int
    owner_id: int
    venue_type: str
    location: Tuple[float, float]
    points_value: float
    is_active: bool = True
    creation_day: float = 0.0
    total_scans: float = 0.0
    unique_scanners: float = 0.0
    
    # Social sneeze mode tracking
    is_in_sneeze_mode: bool = False
    sneeze_mode_start_time: float = 0.0
    sneeze_mode_triggered_at_scans: float = 0.0


class DeepSimulationRunner:
    """Runs multiple simulations and averages their results"""
    
    def __init__(self, config: LifeSimConfig, num_simulations: int = 15):
        self.config = config
        self.num_simulations = num_simulations
        self.simulation_results = []
        self.averaged_data = None
        
    def run_deep_simulation(self, max_days: int = 365, 
                           enable_console_output: bool = False,
                           auto_analyze: bool = True) -> Dict[str, Any]:
        """
        Run multiple simulations and return averaged results
        
        Args:
            max_days: Number of days to simulate
            enable_console_output: Whether to show console output during simulations
            auto_analyze: Whether to run analysis on completion
            
        Returns:
            Dictionary containing averaged simulation data
        """
        print("=" * 80)
        print("DEEP SIMULATION RUNNER")
        print("=" * 80)
        print(f"Running {self.num_simulations} simulations with {max_days} days each")
        print(f"Configuration: {self.config.simulation_name}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Disable console output for individual simulations to reduce noise
        original_console_output = self.config.enable_console_output
        self.config.enable_console_output = enable_console_output
        
        # Disable auto-analysis for individual simulations
        original_auto_analyze = self.config.auto_analyze_on_completion
        self.config.auto_analyze_on_completion = False
        
        try:
            # Run all simulations
            for i in range(self.num_simulations):
                print(f"\nRunning simulation {i+1}/{self.num_simulations}...")
                
                # Create fresh simulator for each run
                simulator = FYNDRLifeSimulator(self.config)
                
                # Run simulation
                simulator.run_simulation(max_days)
                
                # Collect results
                result = self._extract_simulation_data(simulator)
                self.simulation_results.append(result)
                
                # Get final active player count from daily stats
                final_active_players = 0
                if simulator.daily_stats:
                    final_active_players = simulator.daily_stats[-1].active_players
                else:
                    # Fallback to counting active players
                    final_active_players = len([p for p in simulator.players.values() if p.is_active])
                
                print(f"  Completed: {final_active_players} active players, "
                      f"${simulator.total_revenue:.2f} revenue, "
                      f"{simulator.total_scans} scans, "
                      f"{simulator.total_stickers_placed} stickers placed")
            
            # Calculate averages
            print(f"\nCalculating averages across {self.num_simulations} simulations...")
            self.averaged_data = self._calculate_averages()
            
            # Run analysis on averaged results if requested
            if auto_analyze:
                print("\nRunning analysis on averaged results...")
                self._run_analysis_on_averaged_results()
            
            end_time = time.time()
            print(f"\nDeep simulation completed in {end_time - start_time:.2f} seconds")
            
            return self.averaged_data
            
        finally:
            # Restore original settings
            self.config.enable_console_output = original_console_output
            self.config.auto_analyze_on_completion = original_auto_analyze
    
    def _extract_simulation_data(self, simulator: FYNDRLifeSimulator) -> Dict[str, Any]:
        """Extract all relevant data from a completed simulation"""
        return {
            'config': asdict(simulator.config),
            'current_day': simulator.current_day,
            'total_revenue': simulator.total_revenue,
            'total_points_earned': simulator.total_points_earned,
            'total_scans': simulator.total_scans,
            'total_stickers_placed': simulator.total_stickers_placed,
            'players': {k: asdict(v) for k, v in simulator.players.items()},
            'stickers': {k: asdict(v) for k, v in simulator.stickers.items()},
            'daily_stats': [asdict(s) for s in simulator.daily_stats],
            'game_events': [asdict(e) for e in simulator.game_events]
        }
    
    def _calculate_averages(self) -> Dict[str, Any]:
        """Calculate averages across all simulation results"""
        if not self.simulation_results:
            raise ValueError("No simulation results to average")
        
        print("  Averaging daily statistics...")
        averaged_daily_stats = self._average_daily_stats()
        
        print("  Averaging player data...")
        averaged_players = self._average_players()
        
        print("  Averaging sticker data...")
        averaged_stickers = self._average_stickers()
        
        # Calculate summary statistics
        total_revenues = [r['total_revenue'] for r in self.simulation_results]
        total_scans = [r['total_scans'] for r in self.simulation_results]
        total_stickers = [r['total_stickers_placed'] for r in self.simulation_results]
        
        # Get final active player counts from the last day's daily stats
        final_player_counts = []
        for result in self.simulation_results:
            if result['daily_stats']:
                # Get the last day's active_players count
                final_day_stats = result['daily_stats'][-1]
                final_player_counts.append(final_day_stats['active_players'])
            else:
                # Fallback to total players if no daily stats
                final_player_counts.append(len(result['players']))
        
        return {
            'config': self.simulation_results[0]['config'],
            'num_simulations': self.num_simulations,
            'current_day': self.simulation_results[0]['current_day'],
            'total_revenue': statistics.mean(total_revenues),
            'total_revenue_std': statistics.stdev(total_revenues) if len(total_revenues) > 1 else 0,
            'total_points_earned': statistics.mean([r['total_points_earned'] for r in self.simulation_results]),
            'total_scans': statistics.mean(total_scans),
            'total_scans_std': statistics.stdev(total_scans) if len(total_scans) > 1 else 0,
            'total_stickers_placed': statistics.mean(total_stickers),
            'total_stickers_std': statistics.stdev(total_stickers) if len(total_stickers) > 1 else 0,
            'final_player_count': statistics.mean(final_player_counts),
            'final_player_count_std': statistics.stdev(final_player_counts) if len(final_player_counts) > 1 else 0,
            'players': averaged_players,
            'stickers': averaged_stickers,
            'daily_stats': averaged_daily_stats,
            'game_events': self.simulation_results[0]['game_events'],  # Use first simulation's events
            'simulation_variance': {
                'revenue_coefficient_of_variation': statistics.stdev(total_revenues) / statistics.mean(total_revenues) if statistics.mean(total_revenues) > 0 else 0,
                'scans_coefficient_of_variation': statistics.stdev(total_scans) / statistics.mean(total_scans) if statistics.mean(total_scans) > 0 else 0,
                'players_coefficient_of_variation': statistics.stdev(final_player_counts) / statistics.mean(final_player_counts) if statistics.mean(final_player_counts) > 0 else 0
            }
        }
    
    def _average_daily_stats(self) -> List[AveragedDailyStats]:
        """Average daily statistics across all simulations"""
        # Find the maximum number of days across all simulations
        max_days = max(len(r['daily_stats']) for r in self.simulation_results)
        
        averaged_stats = []
        
        for day in range(max_days):
            # Collect stats for this day from all simulations that have data for it
            day_stats = []
            for result in self.simulation_results:
                if day < len(result['daily_stats']):
                    day_stats.append(result['daily_stats'][day])
            
            if not day_stats:
                continue
            
            # Average all numeric fields
            avg_stats = {}
            for field in day_stats[0].keys():
                if field == 'day':
                    avg_stats[field] = day
                elif field in ['event_impacts', 'player_type_counts', 'revenue_by_type']:
                    # Average dictionary fields
                    all_dicts = defaultdict(list)
                    for stats in day_stats:
                        if field in stats and stats[field]:
                            for key, value in stats[field].items():
                                all_dicts[key].append(value)
                    
                    avg_stats[field] = {
                        key: statistics.mean(values) 
                        for key, values in all_dicts.items()
                    }
                elif field in ['sneeze_mode_hotspots', 'social_hub_locations']:
                    # For list fields, use the first simulation's data
                    avg_stats[field] = day_stats[0].get(field, [])
                elif field in ['events_today', 'active_events']:
                    # For list fields, use the first simulation's data
                    avg_stats[field] = day_stats[0].get(field, [])
                elif field in ['population_cap_reached', 'sticker_density_cap_reached']:
                    # For boolean fields, use the most common value
                    values = [stats.get(field, False) for stats in day_stats]
                    avg_stats[field] = max(set(values), key=values.count)
                else:
                    # Average numeric fields - skip non-numeric types
                    values = []
                    for stats in day_stats:
                        if field in stats:
                            value = stats[field]
                            # Only include numeric values
                            if isinstance(value, (int, float)):
                                values.append(value)
                    
                    if values:
                        avg_stats[field] = statistics.mean(values)
                    else:
                        avg_stats[field] = 0
            
            averaged_stats.append(AveragedDailyStats(**avg_stats))
        
        return averaged_stats
    
    def _average_players(self) -> Dict[str, AveragedPlayer]:
        """Average player data across all simulations"""
        # Collect all unique player IDs across all simulations
        all_player_ids = set()
        for result in self.simulation_results:
            all_player_ids.update(result['players'].keys())
        
        averaged_players = {}
        
        for player_id in all_player_ids:
            # Collect this player's data from all simulations
            player_data = []
            for result in self.simulation_results:
                if player_id in result['players']:
                    player_data.append(result['players'][player_id])
            
            if not player_data:
                continue
            
            # Average all numeric fields
            avg_player = {}
            for field in player_data[0].keys():
                if field == 'id':
                    avg_player[field] = int(player_id)
                elif field == 'last_scan_times':
                    # Average last scan times
                    all_scan_times = defaultdict(list)
                    for player in player_data:
                        if 'last_scan_times' in player and player['last_scan_times']:
                            for sticker_id, scan_time in player['last_scan_times'].items():
                                all_scan_times[sticker_id].append(scan_time)
                    
                    avg_player[field] = {
                        sticker_id: statistics.mean(times) 
                        for sticker_id, times in all_scan_times.items()
                    }
                elif field in ['favorite_venues', 'social_hubs', 'daily_routine']:
                    # For list fields, use the first simulation's data
                    avg_player[field] = player_data[0].get(field, [])
                elif field in ['location', 'home_location', 'work_location', 'current_location']:
                    # For tuple fields, use the first simulation's data
                    avg_player[field] = player_data[0].get(field, None)
                elif field in ['is_active', 'scanned_today', 'placed_today', 'has_received_comeback_bonus']:
                    # For boolean fields, use the most common value
                    values = [player.get(field, False) for player in player_data]
                    if values:
                        avg_player[field] = max(set(values), key=values.count)
                    else:
                        avg_player[field] = False
                elif field in ['churn_day', 'referred_by', 'comeback_eligible_day', 'last_level_up_day']:
                    # For optional int fields, use the most common non-None value
                    values = [player.get(field) for player in player_data if player.get(field) is not None]
                    if values:
                        avg_player[field] = max(set(values), key=values.count)
                    else:
                        avg_player[field] = None
                else:
                    # Average numeric fields - skip non-numeric types
                    values = []
                    for player in player_data:
                        if field in player:
                            value = player[field]
                            # Only include numeric values
                            if isinstance(value, (int, float)):
                                values.append(value)
                    
                    if values:
                        avg_player[field] = statistics.mean(values)
                    else:
                        avg_player[field] = 0
            
            averaged_players[player_id] = AveragedPlayer(**avg_player)
        
        return averaged_players
    
    def _average_stickers(self) -> Dict[str, AveragedSticker]:
        """Average sticker data across all simulations"""
        # For deep simulation, we don't need to combine sticker databases
        # as this breaks density mechanics. Instead, we return an empty dict
        # and let the analyzer work with averaged metrics from daily_stats
        return {}
    
    def _run_analysis_on_averaged_results(self):
        """Run analysis on the averaged simulation results"""
        if not self.averaged_data:
            print("No averaged data available for analysis")
            return
        
        # Create a timestamp for the deep simulation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        deep_sim_prefix = f"deep_sim_{timestamp}"
        
        # Save averaged data to a file that the analyzer can read
        self._save_averaged_simulation_state(deep_sim_prefix)
        
        try:
            # Create analyzer instance
            analyzer = CompleteSimulationAnalyzer(deep_sim_prefix)
            
            if not analyzer.all_files:
                print(f"No simulation files found with prefix: {deep_sim_prefix}")
                return
            
            # Generate complete analysis
            print("Generating complete analysis of averaged results...")
            analyzer.generate_complete_summary_report()
            analyzer.generate_level_focused_report()
            analyzer.generate_complete_visualizations()
            
            print(f"Deep simulation analysis saved to: {deep_sim_prefix}_analysis/")
            
            # Print summary
            print("\n" + "="*60)
            print("DEEP SIMULATION ANALYSIS SUMMARY")
            print("="*60)
            print(f"Number of simulations averaged: {self.num_simulations}")
            print(f"Final Active Players: {self.averaged_data['final_player_count']:.1f} ± {self.averaged_data['final_player_count_std']:.1f}")
            print(f"Total Revenue: ${self.averaged_data['total_revenue']:.2f} ± ${self.averaged_data['total_revenue_std']:.2f}")
            print(f"Total Scans: {self.averaged_data['total_scans']:.0f} ± {self.averaged_data['total_scans_std']:.0f}")
            print(f"Total Stickers: {self.averaged_data['total_stickers_placed']:.0f} ± {self.averaged_data['total_stickers_std']:.0f}")
            
            # Print variance information
            variance = self.averaged_data['simulation_variance']
            print(f"\nSimulation Variance (Coefficient of Variation):")
            print(f"  Revenue: {variance['revenue_coefficient_of_variation']:.1%}")
            print(f"  Scans: {variance['scans_coefficient_of_variation']:.1%}")
            print(f"  Players: {variance['players_coefficient_of_variation']:.1%}")
            
        except Exception as e:
            print(f"Error running analysis on averaged results: {e}")
            import traceback
            traceback.print_exc()
    
    def _save_averaged_simulation_state(self, prefix: str):
        """Save averaged simulation state to a file"""
        # Convert averaged data to the format expected by the analyzer
        # NOTE: We don't include the combined sticker database as it breaks density mechanics
        # Instead, we use averaged metrics and let the analyzer work with those
        state = {
            "config": self.averaged_data['config'],
            "current_day": self.averaged_data['current_day'],
            "total_revenue": self.averaged_data['total_revenue'],
            "total_points_earned": self.averaged_data['total_points_earned'],
            "total_scans": self.averaged_data['total_scans'],
            "total_stickers_placed": self.averaged_data['total_stickers_placed'],
            "players": {k: asdict(v) for k, v in self.averaged_data['players'].items()},
            # Don't include combined sticker database - it breaks density mechanics
            # The analyzer should work with averaged metrics instead
            "stickers": {},  # Empty sticker database to avoid density issues
            "daily_stats": [asdict(s) for s in self.averaged_data['daily_stats']],
            "game_events": self.averaged_data['game_events']
        }
        
        filename = f"{prefix}.json"
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"Averaged simulation state saved to {filename}")


def run_deep_simulation(config_file: str = None, 
                       okr_results_file: str = None,
                       days: int = 365,
                       num_simulations: int = 15,
                       enable_console_output: bool = False,
                       auto_analyze: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run a deep simulation
    
    Args:
        config_file: Path to configuration file
        okr_results_file: Path to OKR results file
        days: Number of days to simulate
        num_simulations: Number of simulations to run and average
        enable_console_output: Whether to show console output during simulations
        auto_analyze: Whether to run analysis on completion
        
    Returns:
        Dictionary containing averaged simulation data
    """
    # Load configuration
    if okr_results_file:
        print(f"Loading configuration from OKR results: {okr_results_file}")
        from fyndr_life_simulator import load_config_from_okr_results
        config = load_config_from_okr_results(okr_results_file)
    elif config_file:
        print(f"Loading configuration from: {config_file}")
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        config = LifeSimConfig(**config_data)
    else:
        print("Using default configuration")
        config = LifeSimConfig()
    
    # Create and run deep simulation
    runner = DeepSimulationRunner(config, num_simulations)
    return runner.run_deep_simulation(days, enable_console_output, auto_analyze)


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deep Simulation Runner for FYNDR Life Simulator')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--okr-results', type=str, help='OKR optimization results file')
    parser.add_argument('--days', type=int, default=365, help='Number of days to simulate')
    parser.add_argument('--simulations', type=int, default=15, help='Number of simulations to run and average')
    parser.add_argument('--console-output', action='store_true', help='Enable console output during simulations')
    parser.add_argument('--no-analysis', action='store_true', help='Skip analysis on completion')
    
    args = parser.parse_args()
    
    # Run deep simulation
    result = run_deep_simulation(
        config_file=args.config,
        okr_results_file=args.okr_results,
        days=args.days,
        num_simulations=args.simulations,
        enable_console_output=args.console_output,
        auto_analyze=not args.no_analysis
    )
    
    print("\nDeep simulation completed successfully!")
    return result


if __name__ == "__main__":
    main()
