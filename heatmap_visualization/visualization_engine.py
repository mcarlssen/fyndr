"""
Visualization Engine for Animated Heatmaps

Provides animated heatmap generation using matplotlib and plotly.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import os
import json
from .spatial_analysis import SpatialAnalyzer, create_spatial_analyzer_from_simulation


class HeatmapVisualizer:
    """Generate animated heatmaps from simulation data"""
    
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
    
    def create_animated_heatmap(self, simulation_data: Dict[str, Any], 
                              heatmap_type: str = 'sticker_density',
                              fps: int = 5, duration: int = 10) -> str:
        """Create animated heatmap for a specific metric"""
        
        analyzer = create_spatial_analyzer_from_simulation(simulation_data)
        
        if not analyzer.snapshots:
            raise ValueError("No spatial data available for animation")
        
        # Get animation data
        metric_map = {
            'sticker_density': 'sticker_count',
            'player_activity': 'player_count',
            'scan_activity': 'scan_intensity',
            'value_concentration': 'sticker_value',
            'viral_activity': 'viral_intensity'
        }
        
        metric = metric_map.get(heatmap_type, 'sticker_count')
        animation_data = analyzer.get_animation_data(metric)
        
        if not animation_data:
            raise ValueError("No animation data available")
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Set up the plot
        vmin = min(matrix.min() for matrix in animation_data if matrix.size > 0)
        vmax = max(matrix.max() for matrix in animation_data if matrix.size > 0)
        
        if vmin == vmax:
            vmin = 0
            vmax = 1
        
        im = ax.imshow(animation_data[0], cmap=self.color_schemes[heatmap_type], 
                      origin='lower', aspect='auto', vmin=vmin, vmax=vmax)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label(f'{heatmap_type.replace("_", " ").title()}')
        
        # Set title and labels
        ax.set_title(f'{heatmap_type.replace("_", " ").title()} Animation')
        ax.set_xlabel('Longitude Grid')
        ax.set_ylabel('Latitude Grid')
        
        # Animation function
        def animate(frame):
            if frame < len(animation_data):
                im.set_array(animation_data[frame])
                ax.set_title(f'{heatmap_type.replace("_", " ").title()} - Day {frame}')
            return [im]
        
        # Create animation
        anim = animation.FuncAnimation(fig, animate, frames=len(animation_data),
                                     interval=1000//fps, blit=True, repeat=True)
        
        # Save animation
        output_file = os.path.join(self.output_dir, f'{heatmap_type}_animation.gif')
        anim.save(output_file, writer='pillow', fps=fps)
        
        plt.close()
        
        return output_file
    
    def create_multi_metric_animation(self, simulation_data: Dict[str, Any], 
                                    metrics: List[str] = None,
                                    fps: int = 5) -> str:
        """Create animation showing multiple metrics side by side"""
        
        if metrics is None:
            metrics = ['sticker_density', 'player_activity', 'scan_activity']
        
        analyzer = create_spatial_analyzer_from_simulation(simulation_data)
        
        if not analyzer.snapshots:
            raise ValueError("No spatial data available for animation")
        
        # Get animation data for all metrics
        metric_map = {
            'sticker_density': 'sticker_count',
            'player_activity': 'player_count',
            'scan_activity': 'scan_intensity',
            'value_concentration': 'sticker_value',
            'viral_activity': 'viral_intensity'
        }
        
        animation_data = {}
        for metric in metrics:
            mapped_metric = metric_map.get(metric, 'sticker_count')
            animation_data[metric] = analyzer.get_animation_data(mapped_metric)
        
        if not any(animation_data.values()):
            raise ValueError("No animation data available")
        
        # Create subplots
        n_metrics = len(metrics)
        fig, axes = plt.subplots(1, n_metrics, figsize=(6*n_metrics, 6))
        if n_metrics == 1:
            axes = [axes]
        
        # Set up plots
        images = []
        for i, metric in enumerate(metrics):
            data = animation_data[metric]
            if not data:
                continue
                
            vmin = min(matrix.min() for matrix in data if matrix.size > 0)
            vmax = max(matrix.max() for matrix in data if matrix.size > 0)
            
            if vmin == vmax:
                vmin = 0
                vmax = 1
            
            im = axes[i].imshow(data[0], cmap=self.color_schemes[metric], 
                              origin='lower', aspect='auto', vmin=vmin, vmax=vmax)
            images.append(im)
            
            axes[i].set_title(metric.replace('_', ' ').title())
            axes[i].set_xlabel('Longitude Grid')
            axes[i].set_ylabel('Latitude Grid')
            
            # Add colorbar
            plt.colorbar(im, ax=axes[i], label=metric.replace('_', ' ').title())
        
        # Animation function
        def animate(frame):
            for i, metric in enumerate(metrics):
                data = animation_data[metric]
                if frame < len(data):
                    images[i].set_array(data[frame])
                    axes[i].set_title(f'{metric.replace("_", " ").title()} - Day {frame}')
            return images
        
        # Create animation
        max_frames = max(len(data) for data in animation_data.values())
        anim = animation.FuncAnimation(fig, animate, frames=max_frames,
                                     interval=1000//fps, blit=True, repeat=True)
        
        # Save animation
        output_file = os.path.join(self.output_dir, 'multi_metric_animation.gif')
        anim.save(output_file, writer='pillow', fps=fps)
        
        plt.close()
        
        return output_file
    
    def create_heatmap_evolution(self, simulation_data: Dict[str, Any], 
                               heatmap_type: str = 'sticker_density',
                               days: List[int] = None) -> str:
        """Create a static visualization showing heatmap evolution over time"""
        
        analyzer = create_spatial_analyzer_from_simulation(simulation_data)
        
        if not analyzer.snapshots:
            raise ValueError("No spatial data available")
        
        # Get available days
        available_days = sorted(set(snap.day for snap in analyzer.snapshots))
        
        if days is None:
            # Select representative days
            if len(available_days) <= 6:
                days = available_days
            else:
                # Select evenly spaced days
                step = len(available_days) // 6
                days = available_days[::step][:6]
        
        # Get metric
        metric_map = {
            'sticker_density': 'sticker_count',
            'player_activity': 'player_count',
            'scan_activity': 'scan_intensity',
            'value_concentration': 'sticker_value',
            'viral_activity': 'viral_intensity'
        }
        
        metric = metric_map.get(heatmap_type, 'sticker_count')
        
        # Create subplots
        n_days = len(days)
        cols = min(3, n_days)
        rows = (n_days + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(6*cols, 5*rows))
        if n_days == 1:
            axes = [axes]
        elif rows == 1:
            axes = axes.reshape(1, -1)
        
        # Plot each day
        for i, day in enumerate(days):
            row = i // cols
            col = i % cols
            ax = axes[row, col] if rows > 1 else axes[col]
            
            matrix = analyzer.get_density_matrix(day, metric)
            
            im = ax.imshow(matrix, cmap=self.color_schemes[heatmap_type], 
                          origin='lower', aspect='auto')
            ax.set_title(f'Day {day}')
            ax.set_xlabel('Longitude Grid')
            ax.set_ylabel('Latitude Grid')
            
            # Add colorbar
            plt.colorbar(im, ax=ax, label=metric.replace('_', ' ').title())
        
        # Hide unused subplots
        for i in range(n_days, rows * cols):
            row = i // cols
            col = i % cols
            if rows > 1:
                axes[row, col].set_visible(False)
            else:
                axes[col].set_visible(False)
        
        plt.suptitle(f'{heatmap_type.replace("_", " ").title()} Evolution', fontsize=16)
        plt.tight_layout()
        
        # Save plot
        output_file = os.path.join(self.output_dir, f'{heatmap_type}_evolution.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def generate_all_animations(self, simulation_file: str, 
                              heatmap_types: List[str] = None,
                              fps: int = 5, output_dir: str = None) -> Dict[str, str]:
        """Generate all types of animated heatmaps"""
        
        if heatmap_types is None:
            heatmap_types = ['sticker_density', 'player_activity', 'scan_activity', 
                           'value_concentration', 'viral_activity']
        
        # Use organized output directory if provided
        if output_dir:
            self.output_dir = output_dir
            os.makedirs(output_dir, exist_ok=True)
        
        # Load simulation data
        with open(simulation_file, 'r') as f:
            simulation_data = json.load(f)
        
        results = {}
        
        # Generate individual animations
        for heatmap_type in heatmap_types:
            print(f"Generating {heatmap_type} animation...")
            try:
                output_file = self.create_animated_heatmap(simulation_data, heatmap_type, fps)
                results[heatmap_type] = output_file
                print(f"  Saved: {output_file}")
            except Exception as e:
                print(f"  Error generating {heatmap_type}: {e}")
                results[heatmap_type] = None
        
        # Generate multi-metric animation
        print("Generating multi-metric animation...")
        try:
            output_file = self.create_multi_metric_animation(simulation_data, fps=fps)
            results['multi_metric'] = output_file
            print(f"  Saved: {output_file}")
        except Exception as e:
            print(f"  Error generating multi-metric animation: {e}")
            results['multi_metric'] = None
        
        # Generate evolution plots
        for heatmap_type in heatmap_types:
            print(f"Generating {heatmap_type} evolution plot...")
            try:
                output_file = self.create_heatmap_evolution(simulation_data, heatmap_type)
                results[f'{heatmap_type}_evolution'] = output_file
                print(f"  Saved: {output_file}")
            except Exception as e:
                print(f"  Error generating {heatmap_type} evolution: {e}")
                results[f'{heatmap_type}_evolution'] = None
        
        return results


def main():
    """Main function for testing animated heatmap generation"""
    visualizer = HeatmapVisualizer()
    
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
    
    # Generate animations
    results = visualizer.generate_all_animations(latest_file)
    
    print("\nGenerated animations:")
    for name, file in results.items():
        if file:
            print(f"  {name}: {file}")
        else:
            print(f"  {name}: Failed to generate")


if __name__ == "__main__":
    main()
