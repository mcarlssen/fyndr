#!/usr/bin/env python3
"""
FYNDR Simulator Analysis Tools

Provides analysis and visualization capabilities for simulation results.
"""

import json
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import seaborn as sns
from collections import defaultdict

class FYNDRAnalyzer:
    """Analyzes simulation results and provides insights"""
    
    def __init__(self, simulator_results: Dict[str, Any] = None):
        self.results = simulator_results or {}
        self.daily_data = None
        self.player_data = None
        self.sticker_data = None
    
    def load_simulation_data(self, daily_stats_file: str, players_file: str, stickers_file: str):
        """Load simulation data from CSV files"""
        self.daily_data = pd.read_csv(daily_stats_file)
        self.player_data = pd.read_csv(players_file)
        self.sticker_data = pd.read_csv(stickers_file)
    
    def analyze_economy_health(self) -> Dict[str, Any]:
        """Analyze the overall health of the game economy"""
        if self.daily_data is None or self.player_data is None:
            raise ValueError("No data loaded. Call load_simulation_data() first.")
        
        analysis = {}
        
        # Revenue analysis
        total_revenue = self.player_data['money_spent'].sum()
        analysis['total_revenue'] = total_revenue
        
        # Revenue distribution
        revenue_by_type = self.player_data.groupby('player_type')['money_spent'].sum()
        analysis['revenue_by_type'] = revenue_by_type.to_dict()
        
        # Player engagement
        avg_points_by_type = self.player_data.groupby('player_type')['total_points'].mean()
        analysis['avg_points_by_type'] = avg_points_by_type.to_dict()
        
        # Daily trends
        daily_revenue = self.daily_data['total_revenue'].diff().fillna(0)
        analysis['revenue_growth_rate'] = daily_revenue.mean()
        analysis['revenue_volatility'] = daily_revenue.std()
        
        # Player retention (simplified)
        total_players = len(self.player_data)
        active_players = len(self.player_data[self.player_data['total_points'] > 0])
        analysis['player_retention'] = active_players / total_players if total_players > 0 else 0
        
        # Economy balance metrics
        whale_revenue_share = revenue_by_type.get('whale', 0) / total_revenue if total_revenue > 0 else 0
        analysis['whale_revenue_share'] = whale_revenue_share
        
        # Points economy health
        total_points = self.player_data['total_points'].sum()
        total_scans = self.daily_data['total_scans'].sum()
        analysis['points_per_scan'] = total_points / total_scans if total_scans > 0 else 0
        
        return analysis
    
    def analyze_player_behavior(self) -> Dict[str, Any]:
        """Analyze player behavior patterns"""
        if self.player_data is None:
            raise ValueError("No player data loaded.")
        
        analysis = {}
        
        # Player type distribution
        player_distribution = self.player_data['player_type'].value_counts()
        analysis['player_distribution'] = player_distribution.to_dict()
        
        # Spending patterns
        spending_stats = self.player_data.groupby('player_type')['money_spent'].agg(['mean', 'std', 'max'])
        analysis['spending_stats'] = spending_stats.to_dict()
        
        # Points earning patterns
        points_stats = self.player_data.groupby('player_type')['total_points'].agg(['mean', 'std', 'max'])
        analysis['points_stats'] = points_stats.to_dict()
        
        # Sticker ownership patterns
        sticker_stats = self.player_data.groupby('player_type')['stickers_owned'].agg(['mean', 'std', 'max'])
        analysis['sticker_stats'] = sticker_stats.to_dict()
        
        # Level progression
        level_distribution = self.player_data['level'].value_counts().sort_index()
        analysis['level_distribution'] = level_distribution.to_dict()
        
        return analysis
    
    def analyze_sticker_performance(self) -> Dict[str, Any]:
        """Analyze sticker performance and placement effectiveness"""
        if self.sticker_data is None:
            raise ValueError("No sticker data loaded.")
        
        analysis = {}
        
        # Overall sticker performance
        analysis['total_stickers'] = len(self.sticker_data)
        analysis['active_stickers'] = len(self.sticker_data[self.sticker_data['is_active'] == True])
        analysis['avg_scans_per_sticker'] = self.sticker_data['total_scans'].mean()
        
        # Performance by venue category
        venue_performance = self.sticker_data.groupby('venue_category')['total_scans'].agg(['mean', 'std', 'count'])
        analysis['venue_performance'] = venue_performance.to_dict()
        
        # Performance by level
        level_performance = self.sticker_data.groupby('level')['total_scans'].agg(['mean', 'std', 'count'])
        analysis['level_performance'] = level_performance.to_dict()
        
        # Top performing stickers
        top_stickers = self.sticker_data.nlargest(10, 'total_scans')
        analysis['top_stickers'] = top_stickers[['id', 'owner_id', 'venue_category', 'total_scans']].to_dict('records')
        
        return analysis
    
    def generate_economy_report(self) -> str:
        """Generate a comprehensive economy report"""
        economy_health = self.analyze_economy_health()
        player_behavior = self.analyze_player_behavior()
        sticker_performance = self.analyze_sticker_performance()
        
        report = []
        report.append("FYNDR GAME ECONOMY ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Economy Health Section
        report.append("ECONOMY HEALTH")
        report.append("-" * 20)
        report.append(f"Total Revenue: ${economy_health['total_revenue']:.2f}")
        report.append(f"Player Retention: {economy_health['player_retention']:.1%}")
        report.append(f"Whale Revenue Share: {economy_health['whale_revenue_share']:.1%}")
        report.append(f"Revenue Growth Rate: ${economy_health['revenue_growth_rate']:.2f}/day")
        report.append(f"Revenue Volatility: ${economy_health['revenue_volatility']:.2f}")
        report.append(f"Points per Scan: {economy_health['points_per_scan']:.2f}")
        report.append("")
        
        # Revenue by Player Type
        report.append("REVENUE BY PLAYER TYPE")
        report.append("-" * 25)
        for player_type, revenue in economy_health['revenue_by_type'].items():
            report.append(f"{player_type.title()}: ${revenue:.2f}")
        report.append("")
        
        # Player Behavior Section
        report.append("PLAYER BEHAVIOR")
        report.append("-" * 15)
        report.append("Player Distribution:")
        for player_type, count in player_behavior['player_distribution'].items():
            report.append(f"  {player_type.title()}: {count}")
        report.append("")
        
        report.append("Average Points by Type:")
        for player_type, points in player_behavior['avg_points_by_type'].items():
            report.append(f"  {player_type.title()}: {points:.1f}")
        report.append("")
        
        # Sticker Performance Section
        report.append("STICKER PERFORMANCE")
        report.append("-" * 20)
        report.append(f"Total Stickers: {sticker_performance['total_stickers']}")
        report.append(f"Active Stickers: {sticker_performance['active_stickers']}")
        report.append(f"Average Scans per Sticker: {sticker_performance['avg_scans_per_sticker']:.1f}")
        report.append("")
        
        report.append("Performance by Venue Category:")
        for venue, stats in sticker_performance['venue_performance']['mean'].items():
            report.append(f"  {venue.title()}: {stats:.1f} avg scans")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 15)
        
        if economy_health['whale_revenue_share'] < 0.3:
            report.append("• Consider increasing whale incentives (higher multipliers, exclusive content)")
        
        if economy_health['player_retention'] < 0.8:
            report.append("• Focus on improving player retention (better onboarding, daily rewards)")
        
        if economy_health['points_per_scan'] < 1.5:
            report.append("• Consider increasing base point rewards to improve engagement")
        
        if sticker_performance['avg_scans_per_sticker'] < 5:
            report.append("• Improve sticker discovery mechanisms (better placement guidance, hotspots)")
        
        return "\n".join(report)
    
    def create_visualizations(self, output_dir: str = "analysis_plots"):
        """Create visualization plots for the analysis"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        if self.daily_data is None or self.player_data is None:
            raise ValueError("No data loaded. Call load_simulation_data() first.")
        
        # Set style
        plt.style.use('seaborn-v0_8')
        
        # 1. Daily Revenue Trend
        plt.figure(figsize=(12, 6))
        plt.plot(self.daily_data['day'], self.daily_data['total_revenue'], linewidth=2)
        plt.title('Daily Revenue Trend', fontsize=16, fontweight='bold')
        plt.xlabel('Day')
        plt.ylabel('Total Revenue ($)')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/daily_revenue_trend.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Player Type Distribution
        plt.figure(figsize=(10, 6))
        player_counts = self.player_data['player_type'].value_counts()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        plt.pie(player_counts.values, labels=player_counts.index, autopct='%1.1f%%', 
                colors=colors, startangle=90)
        plt.title('Player Type Distribution', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/player_type_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Revenue by Player Type
        plt.figure(figsize=(10, 6))
        revenue_by_type = self.player_data.groupby('player_type')['money_spent'].sum()
        bars = plt.bar(revenue_by_type.index, revenue_by_type.values, color=colors)
        plt.title('Revenue by Player Type', fontsize=16, fontweight='bold')
        plt.xlabel('Player Type')
        plt.ylabel('Total Revenue ($)')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/revenue_by_player_type.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Points Distribution by Player Type
        plt.figure(figsize=(12, 6))
        for player_type in self.player_data['player_type'].unique():
            data = self.player_data[self.player_data['player_type'] == player_type]['total_points']
            plt.hist(data, alpha=0.7, label=player_type.title(), bins=20)
        plt.title('Points Distribution by Player Type', fontsize=16, fontweight='bold')
        plt.xlabel('Total Points')
        plt.ylabel('Number of Players')
        plt.legend()
        plt.yscale('log')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/points_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 5. Daily Activity Metrics
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Daily scans
        axes[0, 0].plot(self.daily_data['day'], self.daily_data['total_scans'], color='#FF6B6B')
        axes[0, 0].set_title('Daily Total Scans')
        axes[0, 0].set_xlabel('Day')
        axes[0, 0].set_ylabel('Scans')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Daily points
        axes[0, 1].plot(self.daily_data['day'], self.daily_data['total_points_earned'], color='#4ECDC4')
        axes[0, 1].set_title('Daily Points Earned')
        axes[0, 1].set_xlabel('Day')
        axes[0, 1].set_ylabel('Points')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Average points per player
        axes[1, 0].plot(self.daily_data['day'], self.daily_data['avg_points_per_player'], color='#45B7D1')
        axes[1, 0].set_title('Average Points per Player')
        axes[1, 0].set_xlabel('Day')
        axes[1, 0].set_ylabel('Points')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Average scans per player
        axes[1, 1].plot(self.daily_data['day'], self.daily_data['avg_scans_per_player'], color='#96CEB4')
        axes[1, 1].set_title('Average Scans per Player')
        axes[1, 1].set_xlabel('Day')
        axes[1, 1].set_ylabel('Scans')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/daily_activity_metrics.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to {output_dir}/")
    
    def export_analysis(self, filename: str = "economy_analysis.json"):
        """Export analysis results to JSON"""
        analysis = {
            'economy_health': self.analyze_economy_health(),
            'player_behavior': self.analyze_player_behavior(),
            'sticker_performance': self.analyze_sticker_performance(),
            'generated_at': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"Analysis exported to {filename}")

def main():
    """Main function for testing the analyzer"""
    print("FYNDR Analysis Tools")
    print("=" * 30)
    print("This tool analyzes simulation results and generates reports.")
    print("Make sure you have run a simulation first to generate CSV files.")

if __name__ == "__main__":
    main()
EOF 