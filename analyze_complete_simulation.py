#!/usr/bin/env python3
"""
Complete FYNDR Life Simulation Analyzer

Analyzes a complete simulation run that was auto-saved across multiple JSON files.
Combines all auto-save files to provide comprehensive analysis of the entire simulation.
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
import glob
import os
from datetime import datetime
from collections import defaultdict

class CompleteSimulationAnalyzer:
    """Analyzer for complete FYNDR Life Simulation runs across multiple files"""
    
    def __init__(self, simulation_prefix: str):
        self.simulation_prefix = simulation_prefix
        self.all_files = self._find_simulation_files()
        self.combined_data = self._load_and_combine_data()
        
        print(f"Found {len(self.all_files)} simulation files")
        print(f"Combined simulation data from {len(self.combined_data['daily_stats'])} days")
    
    def _find_simulation_files(self):
        """Find all simulation files with the given prefix"""
        # Look for files matching the pattern
        pattern = f"{self.simulation_prefix}*.json"
        files = glob.glob(pattern)
        
        if not files:
            print(f"No files found matching pattern: {pattern}")
            return []
        
        # Sort by timestamp in filename
        files.sort()
        return files
    
    def _load_and_combine_data(self):
        """Load and combine data from all simulation files"""
        combined_data = {
            'config': None,
            'daily_stats': [],
            'players': {},
            'stickers': {},
            'total_revenue': 0,
            'total_points_earned': 0,
            'total_scans': 0,
            'total_stickers_placed': 0,
            'current_day': 0
        }
        
        for file_path in self.all_files:
            print(f"Loading {file_path}...")
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping corrupted file {file_path}: {e}")
                continue
            except Exception as e:
                print(f"Warning: Error loading {file_path}: {e}")
                continue
            
            # Use config from the first file
            if combined_data['config'] is None:
                combined_data['config'] = data['config']
            
            # Combine daily stats (avoid duplicates)
            existing_days = {stat['day'] for stat in combined_data['daily_stats']}
            for stat in data['daily_stats']:
                if stat['day'] not in existing_days:
                    combined_data['daily_stats'].append(stat)
            
            # Combine players (use latest data for each player)
            for player_id, player_data in data['players'].items():
                combined_data['players'][player_id] = player_data
            
            # Combine stickers (use latest data for each sticker)
            for sticker_id, sticker_data in data['stickers'].items():
                combined_data['stickers'][sticker_id] = sticker_data
            
            # Update totals (use values from the latest file)
            combined_data['total_revenue'] = data['total_revenue']
            combined_data['total_points_earned'] = data['total_points_earned']
            combined_data['total_scans'] = data['total_scans']
            combined_data['total_stickers_placed'] = data['total_stickers_placed']
            combined_data['current_day'] = data['current_day']
        
        # Sort daily stats by day
        combined_data['daily_stats'].sort(key=lambda x: x['day'])
        
        return combined_data
    
    def generate_complete_summary_report(self):
        """Generate a comprehensive summary report for the entire simulation"""
        if not self.combined_data['daily_stats']:
            print("No daily statistics available")
            return
        
        daily_stats = self.combined_data['daily_stats']
        latest_stats = daily_stats[-1]
        first_stats = daily_stats[0]
        
        print("\n" + "="*80)
        print("COMPLETE FYNDR LIFE SIMULATION ANALYSIS")
        print("="*80)
        
        print(f"\nSimulation Period: {len(daily_stats)} days")
        print(f"Configuration: {self.combined_data['config'].get('simulation_name', 'Unknown')}")
        print(f"Files Analyzed: {len(self.all_files)}")
        
        print(f"\n📊 FINAL METRICS:")
        print(f"  Active Players: {latest_stats['active_players']:,}")
        print(f"  Total Revenue: ${latest_stats['total_revenue']:,.2f}")
        print(f"  Total Scans: {latest_stats['total_scans']:,}")
        # Use actual sticker count from database, not the placement counter
        actual_stickers = len(self.combined_data.get('stickers', {}))
        print(f"  Total Stickers: {actual_stickers:,}")
        print(f"  Total Stickers Placed (attempts): {latest_stats['total_stickers_placed']:,}")
        print(f"  Retention Rate: {latest_stats['retention_rate']:.1%}")
        print(f"  Average Level: {latest_stats['avg_level']:.1f}")
        
        print(f"\n📈 GROWTH METRICS:")
        player_growth = latest_stats['active_players'] - first_stats['active_players']
        revenue_growth = latest_stats['total_revenue'] - first_stats['total_revenue']
        print(f"  Player Growth: {player_growth:+,} players")
        print(f"  Revenue Growth: ${revenue_growth:+,.2f}")
        print(f"  Final Growth Rate: {latest_stats['growth_rate']:+.1%}")
        
        # Calculate average growth rate over time
        if len(daily_stats) > 1:
            avg_growth_rate = np.mean([stat['growth_rate'] for stat in daily_stats])
            print(f"  Average Growth Rate: {avg_growth_rate:+.1%}")
        
        print(f"\n👥 FINAL PLAYER TYPE DISTRIBUTION:")
        for player_type, count in latest_stats['player_type_counts'].items():
            percentage = (count / latest_stats['active_players']) * 100
            print(f"  {player_type.title()}: {count:,} ({percentage:.1f}%)")
        
        print(f"\n💰 FINAL REVENUE BY PLAYER TYPE:")
        for player_type, revenue in latest_stats['revenue_by_type'].items():
            percentage = (revenue / latest_stats['total_revenue']) * 100 if latest_stats['total_revenue'] > 0 else 0
            print(f"  {player_type.title()}: ${revenue:,.2f} ({percentage:.1f}%)")
        
        # Calculate key metrics
        self._calculate_complete_metrics()
        
        # Analyze level mechanics
        self._analyze_level_mechanics()
        
        # Analyze trends
        self._analyze_trends()
    
    def _calculate_complete_metrics(self):
        """Calculate comprehensive performance metrics"""
        latest_stats = self.combined_data['daily_stats'][-1]
        total_days = len(self.combined_data['daily_stats'])
        
        # Revenue per player
        revenue_per_player = latest_stats['total_revenue'] / latest_stats['active_players'] if latest_stats['active_players'] > 0 else 0
        
        # Scans per player per day
        avg_scans_per_player = latest_stats['total_scans'] / (latest_stats['active_players'] * total_days) if latest_stats['active_players'] > 0 else 0
        
        # Stickers per player (use actual sticker count, not placement attempts)
        actual_stickers = len(data.get('stickers', {}))
        stickers_per_player = actual_stickers / latest_stats['active_players'] if latest_stats['active_players'] > 0 else 0
        
        # Daily revenue average
        daily_revenue_avg = latest_stats['total_revenue'] / total_days
        
        print(f"\n🎯 KEY PERFORMANCE INDICATORS:")
        print(f"  Revenue per Player: ${revenue_per_player:.2f}")
        print(f"  Scans per Player per Day: {avg_scans_per_player:.1f}")
        print(f"  Stickers per Player: {stickers_per_player:.1f}")
        print(f"  Average Daily Revenue: ${daily_revenue_avg:.2f}")
        
        # Player type analysis
        self._analyze_complete_player_types()
    
    def _analyze_complete_player_types(self):
        """Analyze player type performance across the entire simulation"""
        players = self.combined_data['players']
        
        whale_players = [p for p in players.values() if p.get('player_type') == 'whale']
        grinder_players = [p for p in players.values() if p.get('player_type') == 'grinder']
        casual_players = [p for p in players.values() if p.get('player_type') == 'casual']
        
        print(f"\n🔍 COMPLETE PLAYER TYPE ANALYSIS:")
        
        for player_type, players_list in [("Whale", whale_players), ("Grinder", grinder_players), ("Casual", casual_players)]:
            if not players_list:
                continue
                
            avg_points = np.mean([p.get('total_points', 0) for p in players_list])
            avg_spent = np.mean([p.get('total_spent', 0) for p in players_list])
            avg_stickers = np.mean([p.get('stickers_placed', 0) for p in players_list])
            avg_scans = np.mean([p.get('stickers_scanned', 0) for p in players_list])
            avg_days_active = np.mean([p.get('days_active', 0) for p in players_list])
            
            print(f"\n  {player_type.upper()} PLAYERS ({len(players_list)} total):")
            print(f"    Average Points: {avg_points:.1f}")
            print(f"    Average Spent: ${avg_spent:.2f}")
            print(f"    Average Stickers Placed: {avg_stickers:.1f}")
            print(f"    Average Scans: {avg_scans:.1f}")
            print(f"    Average Days Active: {avg_days_active:.1f}")
    
    def _analyze_level_mechanics(self):
        """Analyze level-up mechanics and progression"""
        players = self.combined_data['players']
        config = self.combined_data['config']
        max_level = config.get('max_level', 50)
        
        whale_players = [p for p in players.values() if p.get('player_type') == 'whale']
        grinder_players = [p for p in players.values() if p.get('player_type') == 'grinder']
        casual_players = [p for p in players.values() if p.get('player_type') == 'casual']
        
        print(f"\n🎯 LEVEL-UP MECHANICS ANALYSIS:")
        print(f"  Maximum Level: {max_level}")
        
        for player_type, players_list in [("Whale", whale_players), ("Grinder", grinder_players), ("Casual", casual_players)]:
            if not players_list:
                continue
                
            # Get levels for this player type
            levels = [p.get('level', 1) for p in players_list]
            avg_level = np.mean(levels)
            max_level_reached = max(levels)
            min_level = min(levels)
            
            # Count players at max level
            max_level_count = sum(1 for level in levels if level >= max_level)
            max_level_percentage = (max_level_count / len(players_list)) * 100
            
            # Find first player to reach max level (if any)
            first_to_max = None
            if max_level_count > 0:
                # Find players who reached max level and their join day
                max_level_players = [p for p in players_list if p.get('level', 1) >= max_level]
                if max_level_players:
                    first_to_max = min(max_level_players, key=lambda p: p.get('join_day', 0))
                    days_to_max = first_to_max.get('join_day', 0)  # This would need to be calculated differently
                    # For now, we'll use a placeholder since we don't track when they reached max level
            
            print(f"\n  {player_type.upper()} PLAYERS LEVEL ANALYSIS:")
            print(f"    Average Level: {avg_level:.1f}")
            print(f"    Highest Level Reached: {max_level_reached}")
            print(f"    Lowest Level: {min_level}")
            print(f"    Players at Max Level: {max_level_count}/{len(players_list)} ({max_level_percentage:.1f}%)")
            
            if first_to_max:
                print(f"    First to Max Level: Player {first_to_max.get('id', 'Unknown')} (Day {first_to_max.get('join_day', 'Unknown')})")
            else:
                print(f"    First to Max Level: None reached max level")
        
        # Overall level distribution
        all_levels = [p.get('level', 1) for p in players.values()]
        overall_avg_level = np.mean(all_levels)
        overall_max_level = max(all_levels)
        overall_max_level_count = sum(1 for level in all_levels if level >= max_level)
        
        print(f"\n  OVERALL LEVEL STATISTICS:")
        print(f"    Average Level (All Players): {overall_avg_level:.1f}")
        print(f"    Highest Level Reached: {overall_max_level}")
        print(f"    Total Players at Max Level: {overall_max_level_count}/{len(players)} ({(overall_max_level_count/len(players)*100):.1f}%)")
    
    def _analyze_trends(self):
        """Analyze trends over time"""
        daily_stats = self.combined_data['daily_stats']
        
        if len(daily_stats) < 10:
            return
        
        print(f"\n📈 TREND ANALYSIS:")
        
        # Revenue trend
        early_revenue = np.mean([stat['total_revenue'] for stat in daily_stats[:10]])
        late_revenue = np.mean([stat['total_revenue'] for stat in daily_stats[-10:]])
        revenue_trend = ((late_revenue - early_revenue) / early_revenue) * 100
        
        # Player count trend
        early_players = np.mean([stat['active_players'] for stat in daily_stats[:10]])
        late_players = np.mean([stat['active_players'] for stat in daily_stats[-10:]])
        player_trend = ((late_players - early_players) / early_players) * 100
        
        # Retention trend
        early_retention = np.mean([stat['retention_rate'] for stat in daily_stats[:10]])
        late_retention = np.mean([stat['retention_rate'] for stat in daily_stats[-10:]])
        retention_trend = late_retention - early_retention
        
        print(f"  Revenue Trend (early vs late): {revenue_trend:+.1f}%")
        print(f"  Player Count Trend: {player_trend:+.1f}%")
        print(f"  Retention Trend: {retention_trend:+.1%}")
        
        # Find peak performance
        max_revenue_day = max(daily_stats, key=lambda x: x['total_revenue'])
        max_players_day = max(daily_stats, key=lambda x: x['active_players'])
        
        print(f"\n🏆 PEAK PERFORMANCE:")
        print(f"  Highest Revenue: Day {max_revenue_day['day']} (${max_revenue_day['total_revenue']:,.2f})")
        print(f"  Most Players: Day {max_players_day['day']} ({max_players_day['active_players']} players)")
    
    def generate_complete_visualizations(self, output_dir: str = "complete_simulation_analysis"):
        """Generate comprehensive visualization charts for the entire simulation"""
        if not self.combined_data['daily_stats']:
            print("No daily statistics available for visualization")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(self.combined_data['daily_stats'])
        
        # Create figure with subplots (4x3 to include level scatter plot)
        fig, axes = plt.subplots(4, 3, figsize=(24, 24))
        fig.suptitle('Complete FYNDR Life Simulation Analysis', fontsize=20)
        
        # Plot 1: Player count over time
        axes[0, 0].plot(df['day'], df['active_players'], 'b-', linewidth=2)
        axes[0, 0].set_title('Active Players Over Time')
        axes[0, 0].set_xlabel('Day')
        axes[0, 0].set_ylabel('Active Players')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Revenue over time
        axes[0, 1].plot(df['day'], df['total_revenue'], 'g-', linewidth=2)
        axes[0, 1].set_title('Total Revenue Over Time')
        axes[0, 1].set_xlabel('Day')
        axes[0, 1].set_ylabel('Revenue ($)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Scans over time
        axes[0, 2].plot(df['day'], df['total_scans'], 'r-', linewidth=2)
        axes[0, 2].set_title('Total Scans Over Time')
        axes[0, 2].set_xlabel('Day')
        axes[0, 2].set_ylabel('Total Scans')
        axes[0, 2].grid(True, alpha=0.3)
        
        # Plot 4: Stickers over time
        axes[1, 0].plot(df['day'], df['total_stickers_placed'], 'orange', linewidth=2)
        axes[1, 0].set_title('Total Stickers Placed Over Time')
        axes[1, 0].set_xlabel('Day')
        axes[1, 0].set_ylabel('Total Stickers')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 5: Retention rate over time
        axes[1, 1].plot(df['day'], df['retention_rate'], 'purple', linewidth=2)
        axes[1, 1].set_title('Retention Rate Over Time')
        axes[1, 1].set_xlabel('Day')
        axes[1, 1].set_ylabel('Retention Rate')
        axes[1, 1].grid(True, alpha=0.3)
        
        # Plot 6: Growth rate over time
        axes[1, 2].plot(df['day'], df['growth_rate'], 'brown', linewidth=2)
        axes[1, 2].set_title('Growth Rate Over Time')
        axes[1, 2].set_xlabel('Day')
        axes[1, 2].set_ylabel('Growth Rate')
        axes[1, 2].grid(True, alpha=0.3)
        axes[1, 2].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Plot 7: Player type distribution (final)
        latest_stats = self.combined_data['daily_stats'][-1]
        player_types = list(latest_stats['player_type_counts'].keys())
        player_counts = list(latest_stats['player_type_counts'].values())
        axes[2, 0].pie(player_counts, labels=player_types, autopct='%1.1f%%')
        axes[2, 0].set_title('Final Player Type Distribution')
        
        # Plot 8: Revenue by player type (final)
        revenue_types = list(latest_stats['revenue_by_type'].keys())
        revenue_amounts = list(latest_stats['revenue_by_type'].values())
        axes[2, 1].bar(revenue_types, revenue_amounts, color=['gold', 'silver', 'brown'])
        axes[2, 1].set_title('Final Revenue by Player Type')
        axes[2, 1].set_ylabel('Revenue ($)')
        axes[2, 1].tick_params(axis='x', rotation=45)
        
        # Plot 9: Daily revenue (smoothed)
        if len(df) > 7:
            df['revenue_smooth'] = df['total_revenue'].rolling(window=7, center=True).mean()
            axes[2, 2].plot(df['day'], df['revenue_smooth'], 'green', linewidth=3, alpha=0.7)
            axes[2, 2].set_title('Daily Revenue (7-day moving average)')
            axes[2, 2].set_xlabel('Day')
            axes[2, 2].set_ylabel('Revenue ($)')
            axes[2, 2].grid(True, alpha=0.3)
        
        # Plot 10: Player levels scatter plot by type
        self._create_level_scatter_plot(axes[3, 0])
        
        # Plot 11: Level distribution histogram
        self._create_level_histogram(axes[3, 1])
        
        # Plot 12: Level progression over time (if available)
        self._create_level_progression_plot(axes[3, 2], df)
        
        plt.tight_layout()
        
        # Save the plot
        output_file = os.path.join(output_dir, 'complete_simulation_analysis.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Complete visualizations saved to {output_file}")
    
    def _create_level_scatter_plot(self, ax):
        """Create a scatter plot showing player levels by type"""
        players = self.combined_data['players']
        
        # Separate players by type
        whale_players = [p for p in players.values() if p.get('player_type') == 'whale']
        grinder_players = [p for p in players.values() if p.get('player_type') == 'grinder']
        casual_players = [p for p in players.values() if p.get('player_type') == 'casual']
        
        # Create scatter plot data
        whale_levels = [p.get('level', 1) for p in whale_players]
        grinder_levels = [p.get('level', 1) for p in grinder_players]
        casual_levels = [p.get('level', 1) for p in casual_players]
        
        # Create x-coordinates for jittering
        whale_x = np.random.normal(1, 0.1, len(whale_levels))
        grinder_x = np.random.normal(2, 0.1, len(grinder_levels))
        casual_x = np.random.normal(3, 0.1, len(casual_levels))
        
        # Plot each player type
        if whale_levels:
            ax.scatter(whale_x, whale_levels, alpha=0.6, color='gold', s=50, label=f'Whales (n={len(whale_levels)})')
        if grinder_levels:
            ax.scatter(grinder_x, grinder_levels, alpha=0.6, color='silver', s=50, label=f'Grinders (n={len(grinder_levels)})')
        if casual_levels:
            ax.scatter(casual_x, casual_levels, alpha=0.6, color='brown', s=50, label=f'Casuals (n={len(casual_levels)})')
        
        ax.set_xlabel('Player Type')
        ax.set_ylabel('Player Level')
        ax.set_title('Player Levels by Type (Final)')
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(['Whales', 'Grinders', 'Casuals'])
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add average level lines
        if whale_levels:
            ax.axhline(y=np.mean(whale_levels), color='gold', linestyle='--', alpha=0.7, label=f'Whale Avg: {np.mean(whale_levels):.1f}')
        if grinder_levels:
            ax.axhline(y=np.mean(grinder_levels), color='silver', linestyle='--', alpha=0.7, label=f'Grinder Avg: {np.mean(grinder_levels):.1f}')
        if casual_levels:
            ax.axhline(y=np.mean(casual_levels), color='brown', linestyle='--', alpha=0.7, label=f'Casual Avg: {np.mean(casual_levels):.1f}')
    
    def _create_level_histogram(self, ax):
        """Create a histogram showing level distribution"""
        players = self.combined_data['players']
        all_levels = [p.get('level', 1) for p in players.values()]
        
        # Create histogram
        ax.hist(all_levels, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_xlabel('Player Level')
        ax.set_ylabel('Number of Players')
        ax.set_title('Distribution of Player Levels')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        mean_level = np.mean(all_levels)
        median_level = np.median(all_levels)
        ax.axvline(mean_level, color='red', linestyle='--', label=f'Mean: {mean_level:.1f}')
        ax.axvline(median_level, color='green', linestyle='--', label=f'Median: {median_level:.1f}')
        ax.legend()
    
    def _create_level_progression_plot(self, ax, df):
        """Create a plot showing level progression over time (if available)"""
        # Check if we have level data in daily stats
        if 'avg_level' in df.columns:
            ax.plot(df['day'], df['avg_level'], 'purple', linewidth=2)
            ax.set_xlabel('Day')
            ax.set_ylabel('Average Level')
            ax.set_title('Average Player Level Over Time')
            ax.grid(True, alpha=0.3)
        else:
            # If no level progression data, show a placeholder
            ax.text(0.5, 0.5, 'Level progression data\nnot available in daily stats', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title('Level Progression Over Time')
            ax.set_xlabel('Day')
            ax.set_ylabel('Average Level')
    
    def export_complete_data(self, output_dir: str = "complete_simulation_analysis"):
        """Export complete simulation data to CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export daily stats
        df = pd.DataFrame(self.combined_data['daily_stats'])
        daily_file = os.path.join(output_dir, 'complete_daily_stats.csv')
        df.to_csv(daily_file, index=False)
        
        # Export player data
        players_data = []
        for player_id, player in self.combined_data['players'].items():
            player_data = player.copy()
            player_data['player_id'] = player_id
            players_data.append(player_data)
        
        players_df = pd.DataFrame(players_data)
        players_file = os.path.join(output_dir, 'complete_players.csv')
        players_df.to_csv(players_file, index=False)
        
        # Export sticker data
        stickers_data = []
        for sticker_id, sticker in self.combined_data['stickers'].items():
            sticker_data = sticker.copy()
            sticker_data['sticker_id'] = sticker_id
            # Convert set to list for CSV
            if 'unique_scanners' in sticker_data:
                sticker_data['unique_scanners'] = list(sticker_data['unique_scanners'])
            stickers_data.append(sticker_data)
        
        stickers_df = pd.DataFrame(stickers_data)
        stickers_file = os.path.join(output_dir, 'complete_stickers.csv')
        stickers_df.to_csv(stickers_file, index=False)
        
        # Export summary statistics
        summary_data = {
            'metric': [
                'Total Days',
                'Final Active Players',
                'Total Revenue',
                'Total Scans',
                'Total Stickers Placed',
                'Final Retention Rate',
                'Average Daily Revenue',
                'Revenue per Player',
                'Files Analyzed'
            ],
            'value': [
                len(self.combined_data['daily_stats']),
                self.combined_data['daily_stats'][-1]['active_players'],
                self.combined_data['daily_stats'][-1]['total_revenue'],
                self.combined_data['daily_stats'][-1]['total_scans'],
                self.combined_data['daily_stats'][-1]['total_stickers_placed'],
                self.combined_data['daily_stats'][-1]['retention_rate'],
                self.combined_data['daily_stats'][-1]['total_revenue'] / len(self.combined_data['daily_stats']),
                self.combined_data['daily_stats'][-1]['total_revenue'] / self.combined_data['daily_stats'][-1]['active_players'],
                len(self.all_files)
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_file = os.path.join(output_dir, 'simulation_summary.csv')
        summary_df.to_csv(summary_file, index=False)
        
        print(f"Complete data exported to {output_dir}/")
        print(f"  - complete_daily_stats.csv: All daily statistics")
        print(f"  - complete_players.csv: All player data")
        print(f"  - complete_stickers.csv: All sticker data")
        print(f"  - simulation_summary.csv: Key summary metrics")
    
    def generate_level_focused_report(self, output_dir: str = "complete_simulation_analysis"):
        """Generate a focused report on level mechanics and progression"""
        players = self.combined_data['players']
        config = self.combined_data['config']
        max_level = config.get('max_level', 50)
        
        print(f"\n" + "="*80)
        print("LEVEL MECHANICS FOCUSED ANALYSIS")
        print("="*80)
        
        # Overall level statistics
        all_levels = [p.get('level', 1) for p in players.values()]
        overall_stats = {
            'total_players': len(players),
            'avg_level': np.mean(all_levels),
            'median_level': np.median(all_levels),
            'max_level_reached': max(all_levels),
            'min_level': min(all_levels),
            'players_at_max': sum(1 for level in all_levels if level >= max_level),
            'level_std': np.std(all_levels)
        }
        
        print(f"\n📊 OVERALL LEVEL STATISTICS:")
        print(f"  Total Players: {overall_stats['total_players']}")
        print(f"  Average Level: {overall_stats['avg_level']:.2f}")
        print(f"  Median Level: {overall_stats['median_level']:.1f}")
        print(f"  Highest Level Reached: {overall_stats['max_level_reached']}")
        print(f"  Lowest Level: {overall_stats['min_level']}")
        print(f"  Players at Max Level: {overall_stats['players_at_max']} ({overall_stats['players_at_max']/overall_stats['total_players']*100:.1f}%)")
        print(f"  Level Standard Deviation: {overall_stats['level_std']:.2f}")
        
        # Level distribution by player type
        print(f"\n🎯 LEVEL DISTRIBUTION BY PLAYER TYPE:")
        
        for player_type in ['whale', 'grinder', 'casual']:
            type_players = [p for p in players.values() if p.get('player_type') == player_type]
            if not type_players:
                continue
                
            type_levels = [p.get('level', 1) for p in type_players]
            type_stats = {
                'count': len(type_players),
                'avg_level': np.mean(type_levels),
                'max_level': max(type_levels),
                'min_level': min(type_levels),
                'at_max': sum(1 for level in type_levels if level >= max_level),
                'std': np.std(type_levels)
            }
            
            print(f"\n  {player_type.upper()} PLAYERS ({type_stats['count']} total):")
            print(f"    Average Level: {type_stats['avg_level']:.2f}")
            print(f"    Highest Level: {type_stats['max_level']}")
            print(f"    Lowest Level: {type_stats['min_level']}")
            print(f"    At Max Level: {type_stats['at_max']} ({type_stats['at_max']/type_stats['count']*100:.1f}%)")
            print(f"    Level Std Dev: {type_stats['std']:.2f}")
        
        # Level progression analysis
        print(f"\n📈 LEVEL PROGRESSION INSIGHTS:")
        
        # Find players who reached high levels
        high_level_players = [p for p in players.values() if p.get('level', 1) >= max_level * 0.8]
        print(f"  Players at 80%+ of max level: {len(high_level_players)} ({len(high_level_players)/len(players)*100:.1f}%)")
        
        # Find the most active players (by level)
        top_level_players = sorted(players.values(), key=lambda p: p.get('level', 1), reverse=True)[:10]
        print(f"\n  TOP 10 PLAYERS BY LEVEL:")
        for i, player in enumerate(top_level_players, 1):
            print(f"    {i:2d}. Player {player.get('id', 'Unknown')} - Level {player.get('level', 1)} ({player.get('player_type', 'Unknown')})")
        
        # Save level-focused data
        os.makedirs(output_dir, exist_ok=True)
        
        # Export level data
        level_data = []
        for player_id, player in players.items():
            level_data.append({
                'player_id': player_id,
                'player_type': player.get('player_type', 'unknown'),
                'level': player.get('level', 1),
                'total_points': player.get('total_points', 0),
                'total_xp': player.get('total_xp', 0),
                'days_active': player.get('days_active', 0),
                'join_day': player.get('join_day', 0)
            })
        
        level_df = pd.DataFrame(level_data)
        level_file = os.path.join(output_dir, 'player_levels.csv')
        level_df.to_csv(level_file, index=False)
        
        print(f"\n💾 Level data exported to {level_file}")
        
        return overall_stats

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Analyze complete FYNDR Life Simulation run')
    parser.add_argument('simulation_prefix', help='Prefix of simulation files (e.g., "fyndr_life_sim_20250917_183014")')
    parser.add_argument('--output-dir', default='complete_simulation_analysis', help='Output directory for analysis files')
    parser.add_argument('--no-viz', action='store_true', help='Skip visualization generation')
    parser.add_argument('--no-csv', action='store_true', help='Skip CSV export')
    
    args = parser.parse_args()
    
    try:
        analyzer = CompleteSimulationAnalyzer(args.simulation_prefix)
        
        if not analyzer.all_files:
            print(f"No simulation files found with prefix: {args.simulation_prefix}")
            return 1
        
        # Generate complete summary report
        analyzer.generate_complete_summary_report()
        
        # Generate level-focused report
        analyzer.generate_level_focused_report(args.output_dir)
        
        # Generate visualizations
        if not args.no_viz:
            analyzer.generate_complete_visualizations(args.output_dir)
        
        # Export to CSV
        if not args.no_csv:
            analyzer.export_complete_data(args.output_dir)
        
        print(f"\nComplete analysis finished! Check {args.output_dir}/ for detailed results.")
        
    except Exception as e:
        print(f"Error analyzing complete simulation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
