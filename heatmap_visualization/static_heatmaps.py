"""
Static Heatmap Generation for FYNDR Simulations

Provides static heatmap visualizations using existing simulation data.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import json
import os
from .spatial_analysis import SpatialAnalyzer, create_spatial_analyzer_from_simulation


class StaticHeatmapGenerator:
    """Generate static heatmaps from simulation data"""
    
    def __init__(self, output_dir: str = "heatmap_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Color schemes for different heatmap types
        self.color_schemes = {
            'sticker_density': 'Blues',
            'player_activity': 'Purples', 
            'scan_activity': 'Reds',
            'value_concentration': 'Greens',
            'viral_activity': 'Oranges'
        }
    
    def load_simulation_data(self, simulation_file: str) -> Dict[str, Any]:
        """Load simulation data from JSON file"""
        with open(simulation_file, 'r') as f:
            return json.load(f)
    
    def create_sticker_density_heatmap(self, simulation_data: Dict[str, Any], day: Optional[int] = None) -> str:
        """Create sticker density heatmap"""
        analyzer = create_spatial_analyzer_from_simulation(simulation_data)
        
        if day is None:
            # Use the last day
            day = max(snap.day for snap in analyzer.snapshots) if analyzer.snapshots else 0
        
        matrix = analyzer.get_density_matrix(day, 'sticker_count')
        
        plt.figure(figsize=(12, 10))
        plt.imshow(matrix, cmap=self.color_schemes['sticker_density'], origin='lower', aspect='auto')
        plt.colorbar(label='Sticker Count')
        plt.title(f'Sticker Density Heatmap - Day {day}')
        plt.xlabel('Longitude Grid')
        plt.ylabel('Latitude Grid')
        
        output_file = os.path.join(self.output_dir, f'sticker_density_day_{day}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def create_player_activity_heatmap(self, simulation_data: Dict[str, Any], day: Optional[int] = None) -> str:
        """Create player activity heatmap"""
        analyzer = create_spatial_analyzer_from_simulation(simulation_data)
        
        if day is None:
            day = max(snap.day for snap in analyzer.snapshots) if analyzer.snapshots else 0
        
        matrix = analyzer.get_density_matrix(day, 'player_count')
        
        plt.figure(figsize=(12, 10))
        plt.imshow(matrix, cmap=self.color_schemes['player_activity'], origin='lower', aspect='auto')
        plt.colorbar(label='Player Count')
        plt.title(f'Player Activity Heatmap - Day {day}')
        plt.xlabel('Longitude Grid')
        plt.ylabel('Latitude Grid')
        
        output_file = os.path.join(self.output_dir, f'player_activity_day_{day}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def create_scan_activity_heatmap(self, simulation_data: Dict[str, Any], day: Optional[int] = None) -> str:
        """Create scan activity heatmap"""
        analyzer = create_spatial_analyzer_from_simulation(simulation_data)
        
        if day is None:
            day = max(snap.day for snap in analyzer.snapshots) if analyzer.snapshots else 0
        
        matrix = analyzer.get_density_matrix(day, 'scan_intensity')
        
        plt.figure(figsize=(12, 10))
        plt.imshow(matrix, cmap=self.color_schemes['scan_activity'], origin='lower', aspect='auto')
        plt.colorbar(label='Scan Intensity')
        plt.title(f'Scan Activity Heatmap - Day {day}')
        plt.xlabel('Longitude Grid')
        plt.ylabel('Latitude Grid')
        
        output_file = os.path.join(self.output_dir, f'scan_activity_day_{day}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def create_value_concentration_heatmap(self, simulation_data: Dict[str, Any], day: Optional[int] = None) -> str:
        """Create value concentration heatmap"""
        analyzer = create_spatial_analyzer_from_simulation(simulation_data)
        
        if day is None:
            day = max(snap.day for snap in analyzer.snapshots) if analyzer.snapshots else 0
        
        matrix = analyzer.get_density_matrix(day, 'sticker_value')
        
        plt.figure(figsize=(12, 10))
        plt.imshow(matrix, cmap=self.color_schemes['value_concentration'], origin='lower', aspect='auto')
        plt.colorbar(label='Total Value')
        plt.title(f'Value Concentration Heatmap - Day {day}')
        plt.xlabel('Longitude Grid')
        plt.ylabel('Latitude Grid')
        
        output_file = os.path.join(self.output_dir, f'value_concentration_day_{day}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def create_viral_activity_heatmap(self, simulation_data: Dict[str, Any], day: Optional[int] = None) -> str:
        """Create viral activity heatmap"""
        analyzer = create_spatial_analyzer_from_simulation(simulation_data)
        
        if day is None:
            day = max(snap.day for snap in analyzer.snapshots) if analyzer.snapshots else 0
        
        matrix = analyzer.get_density_matrix(day, 'viral_intensity')
        
        plt.figure(figsize=(12, 10))
        plt.imshow(matrix, cmap=self.color_schemes['viral_activity'], origin='lower', aspect='auto')
        plt.colorbar(label='Viral Intensity')
        plt.title(f'Viral Activity Heatmap - Day {day}')
        plt.xlabel('Longitude Grid')
        plt.ylabel('Latitude Grid')
        
        output_file = os.path.join(self.output_dir, f'viral_activity_day_{day}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def create_comprehensive_heatmap(self, simulation_data: Dict[str, Any], day: Optional[int] = None) -> str:
        """Create a comprehensive heatmap with multiple metrics"""
        analyzer = create_spatial_analyzer_from_simulation(simulation_data)
        
        if day is None:
            day = max(snap.day for snap in analyzer.snapshots) if analyzer.snapshots else 0
        
        # Create subplots for different metrics
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Comprehensive Heatmap Analysis - Day {day}', fontsize=16)
        
        metrics = [
            ('sticker_count', 'Sticker Density', 'Blues'),
            ('player_count', 'Player Activity', 'Purples'),
            ('scan_intensity', 'Scan Activity', 'Reds'),
            ('sticker_value', 'Value Concentration', 'Greens'),
            ('viral_intensity', 'Viral Activity', 'Oranges')
        ]
        
        for i, (metric, title, cmap) in enumerate(metrics):
            row = i // 3
            col = i % 3
            ax = axes[row, col]
            
            matrix = analyzer.get_density_matrix(day, metric)
            im = ax.imshow(matrix, cmap=cmap, origin='lower', aspect='auto')
            ax.set_title(title)
            ax.set_xlabel('Longitude Grid')
            ax.set_ylabel('Latitude Grid')
            plt.colorbar(im, ax=ax, label=title)
        
        # Hide the last subplot if we have an odd number of metrics
        if len(metrics) < 6:
            axes[1, 2].set_visible(False)
        
        plt.tight_layout()
        
        output_file = os.path.join(self.output_dir, f'comprehensive_heatmap_day_{day}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def generate_all_static_heatmaps(self, simulation_file: str, days: Optional[List[int]] = None, output_dir: str = None) -> Dict[str, List[str]]:
        """Generate all static heatmaps for specified days"""
        simulation_data = self.load_simulation_data(simulation_file)
        
        # Use organized output directory if provided
        if output_dir:
            self.output_dir = output_dir
            os.makedirs(output_dir, exist_ok=True)
        
        if days is None:
            # Generate for the last day only
            daily_stats = simulation_data.get('daily_stats', [])
            if daily_stats:
                days = [max(stat['day'] for stat in daily_stats)]
            else:
                days = [0]
        
        results = {
            'sticker_density': [],
            'player_activity': [],
            'scan_activity': [],
            'value_concentration': [],
            'viral_activity': [],
            'comprehensive': []
        }
        
        for day in days:
            print(f"Generating heatmaps for day {day}...")
            
            # Generate individual heatmaps
            results['sticker_density'].append(
                self.create_sticker_density_heatmap(simulation_data, day)
            )
            results['player_activity'].append(
                self.create_player_activity_heatmap(simulation_data, day)
            )
            results['scan_activity'].append(
                self.create_scan_activity_heatmap(simulation_data, day)
            )
            results['value_concentration'].append(
                self.create_value_concentration_heatmap(simulation_data, day)
            )
            results['viral_activity'].append(
                self.create_viral_activity_heatmap(simulation_data, day)
            )
            results['comprehensive'].append(
                self.create_comprehensive_heatmap(simulation_data, day)
            )
        
        return results


def main():
    """Main function for testing static heatmap generation"""
    generator = StaticHeatmapGenerator()
    
    # Find simulation files
    simulation_files = []
    for file in os.listdir('.'):
        if file.startswith('fyndr_life_sim_') and file.endswith('.json'):
            simulation_files.append(file)
    
    if not simulation_files:
        print("No simulation files found. Please run a simulation first.")
        return
    
    # Use the most recent simulation file
    latest_file = max(simulation_files, key=os.path.getctime)
    print(f"Using simulation file: {latest_file}")
    
    # Generate heatmaps
    results = generator.generate_all_static_heatmaps(latest_file)
    
    print("\nGenerated heatmaps:")
    for heatmap_type, files in results.items():
        print(f"\n{heatmap_type}:")
        for file in files:
            print(f"  - {file}")


if __name__ == "__main__":
    main()
