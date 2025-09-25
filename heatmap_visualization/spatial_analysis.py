"""
Spatial Analysis Module for FYNDR Heatmap Visualizations

Provides grid-based spatial analysis and density calculations for heatmap generation.
"""

import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
from collections import defaultdict


@dataclass
class SpatialSnapshot:
    """Snapshot of spatial data at a specific time"""
    day: int
    hour: Optional[int] = None  # 0-23, or None for daily snapshots
    timestamp: float = 0.0  # Unix timestamp for precise timing
    
    # Spatial data
    sticker_locations: List[Tuple[float, float, float]] = None  # lat, lng, value
    player_locations: List[Tuple[float, float, str]] = None  # lat, lng, player_type
    scan_events: List[Tuple[float, float, int]] = None  # lat, lng, scan_count
    sneeze_hotspots: List[Tuple[float, float, float]] = None  # lat, lng, intensity
    
    # Grid-based density data
    grid_density: Dict[Tuple[int, int], Dict[str, float]] = None
    
    def __post_init__(self):
        if self.sticker_locations is None:
            self.sticker_locations = []
        if self.player_locations is None:
            self.player_locations = []
        if self.scan_events is None:
            self.scan_events = []
        if self.sneeze_hotspots is None:
            self.sneeze_hotspots = []
        if self.grid_density is None:
            self.grid_density = {}


@dataclass
class SpatialGrid:
    """Grid system for spatial analysis"""
    bounds: Dict[str, Tuple[float, float]]  # lat/lng bounds
    grid_size: int  # Number of cells per dimension
    cell_size: float  # Size of each cell in degrees
    
    def __post_init__(self):
        """Calculate cell size based on bounds and grid size"""
        lat_range = self.bounds['lat'][1] - self.bounds['lat'][0]
        lng_range = self.bounds['lng'][1] - self.bounds['lng'][0]
        self.cell_size = max(lat_range, lng_range) / self.grid_size
    
    def get_cell(self, lat: float, lng: float) -> Tuple[int, int]:
        """Get grid cell coordinates for a location"""
        lat_cell = int((lat - self.bounds['lat'][0]) / self.cell_size)
        lng_cell = int((lng - self.bounds['lng'][0]) / self.cell_size)
        
        # Clamp to grid bounds
        lat_cell = max(0, min(self.grid_size - 1, lat_cell))
        lng_cell = max(0, min(self.grid_size - 1, lng_cell))
        
        return (lat_cell, lng_cell)
    
    def get_cell_bounds(self, cell: Tuple[int, int]) -> Dict[str, Tuple[float, float]]:
        """Get lat/lng bounds for a grid cell"""
        lat_start = self.bounds['lat'][0] + cell[0] * self.cell_size
        lat_end = lat_start + self.cell_size
        lng_start = self.bounds['lng'][0] + cell[1] * self.cell_size
        lng_end = lng_start + self.cell_size
        
        return {
            'lat': (lat_start, lat_end),
            'lng': (lng_start, lng_end)
        }
    
    def calculate_density(self, cell: Tuple[int, int], snapshot: SpatialSnapshot) -> Dict[str, float]:
        """Calculate density metrics for a grid cell"""
        cell_bounds = self.get_cell_bounds(cell)
        
        # Count stickers in cell
        stickers_in_cell = 0
        sticker_value = 0.0
        for lat, lng, value in snapshot.sticker_locations:
            if (cell_bounds['lat'][0] <= lat < cell_bounds['lat'][1] and 
                cell_bounds['lng'][0] <= lng < cell_bounds['lng'][1]):
                stickers_in_cell += 1
                sticker_value += value
        
        # Count players in cell
        players_in_cell = 0
        player_types = defaultdict(int)
        for lat, lng, player_type in snapshot.player_locations:
            if (cell_bounds['lat'][0] <= lat < cell_bounds['lat'][1] and 
                cell_bounds['lng'][0] <= lng < cell_bounds['lng'][1]):
                players_in_cell += 1
                player_types[player_type] += 1
        
        # Count scan events in cell
        scan_intensity = 0
        for lat, lng, scan_count in snapshot.scan_events:
            if (cell_bounds['lat'][0] <= lat < cell_bounds['lat'][1] and 
                cell_bounds['lng'][0] <= lng < cell_bounds['lng'][1]):
                scan_intensity += scan_count
        
        # Count sneeze hotspots in cell
        viral_intensity = 0.0
        for lat, lng, intensity in snapshot.sneeze_hotspots:
            if (cell_bounds['lat'][0] <= lat < cell_bounds['lat'][1] and 
                cell_bounds['lng'][0] <= lng < cell_bounds['lng'][1]):
                viral_intensity += intensity
        
        return {
            'sticker_count': stickers_in_cell,
            'sticker_value': sticker_value,
            'player_count': players_in_cell,
            'scan_intensity': scan_intensity,
            'viral_intensity': viral_intensity,
            'player_types': dict(player_types)
        }
    
    def calculate_all_densities(self, snapshot: SpatialSnapshot) -> Dict[Tuple[int, int], Dict[str, float]]:
        """Calculate density for all grid cells"""
        densities = {}
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cell = (i, j)
                densities[cell] = self.calculate_density(cell, snapshot)
        return densities


class SpatialAnalyzer:
    """Main class for spatial analysis operations"""
    
    def __init__(self, bounds: Dict[str, Tuple[float, float]], grid_size: int = 50):
        self.grid = SpatialGrid(bounds, grid_size, 0.0)  # cell_size will be calculated in __post_init__
        self.snapshots: List[SpatialSnapshot] = []
    
    def add_snapshot(self, snapshot: SpatialSnapshot):
        """Add a spatial snapshot"""
        # Calculate grid densities for this snapshot
        snapshot.grid_density = self.grid.calculate_all_densities(snapshot)
        self.snapshots.append(snapshot)
    
    def get_density_matrix(self, day: int, metric: str = 'sticker_count') -> np.ndarray:
        """Get density matrix for a specific day and metric"""
        # Find snapshot for the day
        snapshot = None
        for snap in self.snapshots:
            if snap.day == day:
                snapshot = snap
                break
        
        if snapshot is None:
            return np.zeros((self.grid.grid_size, self.grid.grid_size))
        
        # Create matrix from grid densities
        matrix = np.zeros((self.grid.grid_size, self.grid.grid_size))
        for cell, densities in snapshot.grid_density.items():
            matrix[cell[0], cell[1]] = densities.get(metric, 0)
        
        return matrix
    
    def get_animation_data(self, metric: str = 'sticker_count') -> List[np.ndarray]:
        """Get animation data for all days"""
        animation_data = []
        max_day = max(snap.day for snap in self.snapshots) if self.snapshots else 0
        
        for day in range(max_day + 1):
            matrix = self.get_density_matrix(day, metric)
            animation_data.append(matrix)
        
        return animation_data
    
    def get_bounds_from_data(self, data: List[Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """Calculate bounds from coordinate data"""
        if not data:
            return {'lat': (0, 0.1), 'lng': (0, 0.1)}  # Default bounds
        
        lats = [point[0] for point in data]
        lngs = [point[1] for point in data]
        
        # Add some padding
        lat_range = max(lats) - min(lats)
        lng_range = max(lngs) - min(lngs)
        lat_padding = lat_range * 0.1 if lat_range > 0 else 0.01
        lng_padding = lng_range * 0.1 if lng_range > 0 else 0.01
        
        return {
            'lat': (min(lats) - lat_padding, max(lats) + lat_padding),
            'lng': (min(lngs) - lng_padding, max(lngs) + lng_padding)
        }


def create_spatial_analyzer_from_simulation(simulation_data: Dict[str, Any], grid_size: int = 50) -> SpatialAnalyzer:
    """Create spatial analyzer from existing simulation data"""
    
    # Extract bounds from sticker and player locations
    all_locations = []
    
    # Add sticker locations
    for sticker_data in simulation_data.get('stickers', {}).values():
        if 'location' in sticker_data:
            location = sticker_data['location']  # Already a list
            all_locations.append(location)
    
    # Add player locations
    for player_data in simulation_data.get('players', {}).values():
        if 'location' in player_data:
            location = player_data['location']  # Already a list
            all_locations.append(location)
    
    # Calculate bounds
    bounds = SpatialAnalyzer({'lat': (0, 0.1), 'lng': (0, 0.1)}, grid_size).get_bounds_from_data(all_locations)
    analyzer = SpatialAnalyzer(bounds, grid_size)
    
    # Create snapshots from daily data
    daily_stats = simulation_data.get('daily_stats', [])
    stickers_data = simulation_data.get('stickers', {})
    players_data = simulation_data.get('players', {})
    
    for day_stats in daily_stats:
        day = day_stats['day']
        
        # Create snapshot for this day
        snapshot = SpatialSnapshot(day=day)
        
        # Add sticker locations
        for sticker_id, sticker_data in stickers_data.items():
            if sticker_data.get('creation_day', 0) <= day and sticker_data.get('is_active', True):
                location = sticker_data['location']  # Already a list
                value = sticker_data.get('points_value', 0)
                snapshot.sticker_locations.append((location[0], location[1], value))
        
        # Add player locations
        for player_id, player_data in players_data.items():
            if player_data.get('is_active', True):
                location = player_data['location']  # Already a list
                player_type = player_data.get('player_type', 'casual')
                snapshot.player_locations.append((location[0], location[1], player_type))
        
        # Add sneeze hotspots if available
        if 'sneeze_mode_hotspots' in day_stats and day_stats['sneeze_mode_hotspots']:
            for hotspot in day_stats['sneeze_mode_hotspots']:
                if isinstance(hotspot, list) and len(hotspot) >= 2:
                    snapshot.sneeze_hotspots.append((hotspot[0], hotspot[1], 1.0))
        
        analyzer.add_snapshot(snapshot)
    
    return analyzer
