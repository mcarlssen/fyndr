#!/usr/bin/env python3
"""
FYNDR Life Simulation Analyzer

Analyzes simulation results and generates reports and visualizations.
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
from datetime import datetime
import os

class LifeSimulationAnalyzer:
    """Analyzer for FYNDR Life Simulation results"""
    
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.load_simulation_state()
    
    def load_simulation_state(self):
        """Load simulation state from file"""
        with open(self.state_file, 'r') as f:
            self.state = json.load(f)
        
        self.config = self.state['config']
        self.daily_stats = self.state['daily_stats']
        self.players = self.state['players']
        self.stickers = self.state['stickers']
        
        print(f"Loaded simulation state from {self.state_file}")
        print(f"Simulation ran for {len(self.daily_stats)} days")
        print(f"Total players: {len(self.players)}")
        print(f"Total stickers: {len(self.stickers)}")
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        if not self.daily_stats:
            print("No daily statistics available")
            return
        
        latest_stats = self.daily_stats[-1]
        first_stats = self.daily_stats[0]
        
        print("\n" + "="*60)
        print("FYNDR LIFE SIMULATION SUMMARY REPORT")
        print("="*60)
        
        print(f"\nSimulation Period: {len(self.daily_stats)} days")
        print(f"Configuration: {self.config.get('simulation_name', 'Unknown')}")
        
        print(f"\n📊 FINAL METRICS:")
        print(f"  Active Players: {latest_stats['active_players']:,}")
        print(f"  Total Revenue: ${latest_stats['total_revenue']:,.2f}")
        print(f"  Total Scans: {latest_stats['total_scans']:,}")
        print(f"  Total Stickers Placed: {latest_stats['total_stickers_placed']:,}")
        print(f"  Retention Rate: {latest_stats['retention_rate']:.1%}")
        print(f"  Average Level: {latest_stats['avg_level']:.1f}")
        
        print(f"\n📈 GROWTH METRICS:")
        player_growth = latest_stats['active_players'] - first_stats['active_players']
        revenue_growth = latest_stats['total_revenue'] - first_stats['total_revenue']
        print(f"  Player Growth: {player_growth:+,} players")
        print(f"  Revenue Growth: ${revenue_growth:+,.2f}")
        print(f"  Daily Growth Rate: {latest_stats['growth_rate']:+.1%}")
        
        print(f"\n👥 PLAYER TYPE DISTRIBUTION:")
        for player_type, count in latest_stats['player_type_counts'].items():
            percentage = (count / latest_stats['active_players']) * 100
            print(f"  {player_type.title()}: {count:,} ({percentage:.1f}%)")
        
        print(f"\n💰 REVENUE BY PLAYER TYPE:")
        for player_type, revenue in latest_stats['revenue_by_type'].items():
            percentage = (revenue / latest_stats['total_revenue']) * 100 if latest_stats['total_revenue'] > 0 else 0
            print(f"  {player_type.title()}: ${revenue:,.2f} ({percentage:.1f}%)")
        
        # Calculate key metrics
        self._calculate_key_metrics()
    
    def _calculate_key_metrics(self):
        """Calculate key performance metrics"""
        if len(self.daily_stats) < 2:
            return
        
        # Revenue per player
        latest_stats = self.daily_stats[-1]
        revenue_per_player = latest_stats['total_revenue'] / latest_stats['active_players'] if latest_stats['active_players'] > 0 else 0
        
        # Scans per player per day
        avg_scans_per_player = latest_stats['total_scans'] / (latest_stats['active_players'] * len(self.daily_stats)) if latest_stats['active_players'] > 0 else 0
        
        # Stickers per player
        stickers_per_player = latest_stats['total_stickers_placed'] / latest_stats['active_players'] if latest_stats['active_players'] > 0 else 0
        
        print(f"\n🎯 KEY PERFORMANCE INDICATORS:")
        print(f"  Revenue per Player: ${revenue_per_player:.2f}")
        print(f"  Scans per Player per Day: {avg_scans_per_player:.1f}")
        print(f"  Stickers per Player: {stickers_per_player:.1f}")
        
        # Player type analysis
        self._analyze_player_types()
    
    def _analyze_player_types(self):
        """Analyze player type performance"""
        whale_players = [p for p in self.players.values() if p.get('player_type') == 'whale']
        grinder_players = [p for p in self.players.values() if p.get('player_type') == 'grinder']
        casual_players = [p for p in self.players.values() if p.get('player_type') == 'casual']
        
        print(f"\n🔍 PLAYER TYPE ANALYSIS:")
        
        for player_type, players in [("Whale", whale_players), ("Grinder", grinder_players), ("Casual", casual_players)]:
            if not players:
                continue
                
            avg_points = np.mean([p.get('total_points', 0) for p in players])
            avg_spent = np.mean([p.get('total_spent', 0) for p in players])
            avg_stickers = np.mean([p.get('stickers_placed', 0) for p in players])
            avg_scans = np.mean([p.get('stickers_scanned', 0) for p in players])
            
            print(f"\n  {player_type.upper()} PLAYERS ({len(players)} total):")
            print(f"    Average Points: {avg_points:.1f}")
            print(f"    Average Spent: ${avg_spent:.2f}")
            print(f"    Average Stickers Placed: {avg_stickers:.1f}")
            print(f"    Average Scans: {avg_scans:.1f}")
    
    def generate_visualizations(self, output_dir: str = "simulation_analysis"):
        """Generate visualization charts"""
        if not self.daily_stats:
            print("No daily statistics available for visualization")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(self.daily_stats)
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('FYNDR Life Simulation Analysis', fontsize=16)
        
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
        
        # Plot 4: Player type distribution
        latest_stats = self.daily_stats[-1]
        player_types = list(latest_stats['player_type_counts'].keys())
        player_counts = list(latest_stats['player_type_counts'].values())
        axes[1, 0].pie(player_counts, labels=player_types, autopct='%1.1f%%')
        axes[1, 0].set_title('Player Type Distribution')
        
        # Plot 5: Revenue by player type
        revenue_types = list(latest_stats['revenue_by_type'].keys())
        revenue_amounts = list(latest_stats['revenue_by_type'].values())
        axes[1, 1].bar(revenue_types, revenue_amounts, color=['gold', 'silver', 'brown'])
        axes[1, 1].set_title('Revenue by Player Type')
        axes[1, 1].set_ylabel('Revenue ($)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # Plot 6: Retention rate over time
        axes[1, 2].plot(df['day'], df['retention_rate'], 'purple', linewidth=2)
        axes[1, 2].set_title('Retention Rate Over Time')
        axes[1, 2].set_xlabel('Day')
        axes[1, 2].set_ylabel('Retention Rate')
        axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the plot
        output_file = os.path.join(output_dir, 'simulation_analysis.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to {output_file}")
    
    def export_to_csv(self, output_dir: str = "simulation_analysis"):
        """Export simulation data to CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export daily stats
        df = pd.DataFrame(self.daily_stats)
        daily_file = os.path.join(output_dir, 'daily_stats.csv')
        df.to_csv(daily_file, index=False)
        
        # Export player data
        players_data = []
        for player_id, player in self.players.items():
            player_data = player.copy()
            player_data['player_id'] = player_id
            players_data.append(player_data)
        
        players_df = pd.DataFrame(players_data)
        players_file = os.path.join(output_dir, 'players.csv')
        players_df.to_csv(players_file, index=False)
        
        # Export sticker data
        stickers_data = []
        for sticker_id, sticker in self.stickers.items():
            sticker_data = sticker.copy()
            sticker_data['sticker_id'] = sticker_id
            # Convert set to list for CSV
            if 'unique_scanners' in sticker_data:
                sticker_data['unique_scanners'] = list(sticker_data['unique_scanners'])
            stickers_data.append(sticker_data)
        
        stickers_df = pd.DataFrame(stickers_data)
        stickers_file = os.path.join(output_dir, 'stickers.csv')
        stickers_df.to_csv(stickers_file, index=False)
        
        print(f"CSV files exported to {output_dir}/")
        print(f"  - daily_stats.csv: Daily simulation statistics")
        print(f"  - players.csv: Player data and statistics")
        print(f"  - stickers.csv: Sticker data and statistics")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Analyze FYNDR Life Simulation results')
    parser.add_argument('state_file', help='Simulation state file to analyze')
    parser.add_argument('--output-dir', default='simulation_analysis', help='Output directory for analysis files')
    parser.add_argument('--no-viz', action='store_true', help='Skip visualization generation')
    parser.add_argument('--no-csv', action='store_true', help='Skip CSV export')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.state_file):
        print(f"Error: State file {args.state_file} not found")
        return 1
    
    try:
        analyzer = LifeSimulationAnalyzer(args.state_file)
        
        # Generate summary report
        analyzer.generate_summary_report()
        
        # Generate visualizations
        if not args.no_viz:
            analyzer.generate_visualizations(args.output_dir)
        
        # Export to CSV
        if not args.no_csv:
            analyzer.export_to_csv(args.output_dir)
        
        print(f"\nAnalysis complete! Check {args.output_dir}/ for detailed results.")
        
    except Exception as e:
        print(f"Error analyzing simulation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
