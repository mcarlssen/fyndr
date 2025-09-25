# Animated Heatmap Visualization Feature Specification

## Overview

This document outlines the specification for implementing animated heatmap visualizations for the FYNDR Life Simulator. The feature will provide dynamic, time-based visualizations showing how sticker placement, player activity, and value concentration evolve over the simulation period.

## Feature Description

### Core Concept
Create animated heatmaps that visualize:
- **Sticker placement density** over time
- **Player activity hotspots** and movement patterns
- **Value concentration** and economic activity
- **Viral spread patterns** (sneeze mode hotspots)
- **Social hub activity** and attraction effects

### Visualization Types
1. **Sticker Density Heatmap**: Shows where stickers are placed and how density builds up
2. **Player Activity Heatmap**: Shows player movement and activity patterns
3. **Scan Activity Heatmap**: Shows where scanning activity is concentrated
4. **Value Heatmap**: Shows economic value concentration over time
5. **Viral Activity Heatmap**: Shows sneeze mode hotspots and viral spread

## Current Data Analysis

### ✅ Available Data
**Spatial Data:**
- Sticker locations: `location: Tuple[float, float]` (lat, lng coordinates)
- Player locations: `location`, `home_location`, `work_location`, `current_location`
- Social hub locations: Predefined coordinates
- Movement patterns: `daily_routine` paths and movement tracking

**Temporal Data:**
- Daily snapshots: Complete daily stats with day-by-day progression
- Sticker creation day: `creation_day` field
- Player join day: `join_day` for player onboarding
- Scan timestamps: `last_scan_times` dict

**Value/Activity Data:**
- Sticker values: `points_value` for each sticker
- Scan counts: `total_scans` and `unique_scanners` per sticker
- Sneeze mode tracking: `is_in_sneeze_mode` and related fields
- Player activity: Daily patterns, streak days, etc.

### ❌ Missing Data for Full Animation
**High-Resolution Temporal Data:**
- Hourly/daily snapshots (currently only daily aggregates)
- Sticker placement timestamps (have day, not time within day)
- Scan event timestamps (have last scan, not full scan history)
- Player movement timestamps (have patterns, not exact timing)

**Spatial Density Data:**
- Grid-based density calculations
- Heatmap intensity values for each spatial cell over time

## Technical Requirements

### Data Structures

#### Enhanced Spatial Tracking
```python
@dataclass
class SpatialSnapshot:
    """Snapshot of spatial data at a specific time"""
    day: int
    hour: int  # 0-23, or None for daily snapshots
    timestamp: float  # Unix timestamp for precise timing
    
    # Spatial data
    sticker_locations: List[Tuple[float, float, float]]  # lat, lng, value
    player_locations: List[Tuple[float, float, str]]  # lat, lng, player_type
    scan_events: List[Tuple[float, float, int]]  # lat, lng, scan_count
    sneeze_hotspots: List[Tuple[float, float, float]]  # lat, lng, intensity
    
    # Grid-based density data
    grid_density: Dict[Tuple[int, int], Dict[str, float]]  # cell -> metrics
```

#### Spatial Grid System
```python
@dataclass
class SpatialGrid:
    """Grid system for spatial analysis"""
    bounds: Dict[str, Tuple[float, float]]  # lat/lng bounds
    grid_size: int  # Number of cells per dimension
    cell_size: float  # Size of each cell in degrees
    
    def get_cell(self, lat: float, lng: float) -> Tuple[int, int]:
        """Get grid cell coordinates for a location"""
        pass
    
    def calculate_density(self, cell: Tuple[int, int], data: SpatialSnapshot) -> Dict[str, float]:
        """Calculate density metrics for a grid cell"""
        return {
            'sticker_count': int,
            'player_count': int,
            'scan_intensity': float,
            'value_density': float,
            'viral_intensity': float
        }
```

### Implementation Phases

#### Phase 1: Basic Static Heatmaps (1-2 days)
**Goal**: Create static heatmaps using existing data

**Deliverables**:
- Static sticker density heatmap
- Static player distribution heatmap
- Static scan activity heatmap
- Basic visualization framework

**Technical Approach**:
```python
def create_static_heatmap(simulation_data, heatmap_type='sticker_density'):
    """Create static heatmap from simulation data"""
    # Extract spatial data from existing simulation results
    # Create grid-based density calculations
    # Generate matplotlib/plotly heatmap
    # Save as static image
```

#### Phase 2: Enhanced Data Collection (3-5 days)
**Goal**: Add high-resolution temporal tracking to simulation

**Deliverables**:
- Hourly snapshot system
- Enhanced scan event tracking
- Spatial grid integration
- Improved movement pattern tracking

**Code Changes Required**:
```python
# Add to FYNDRLifeSimulator class
class FYNDRLifeSimulator:
    def __init__(self, config: LifeSimConfig):
        # ... existing code ...
        self.spatial_snapshots: List[SpatialSnapshot] = []
        self.spatial_grid = SpatialGrid(config.simulation_bounds)
    
    def run_day(self):
        """Enhanced to capture spatial snapshots"""
        # ... existing simulation logic ...
        
        # Capture spatial snapshot every hour
        for hour in range(24):
            snapshot = self._capture_spatial_snapshot(hour)
            self.spatial_snapshots.append(snapshot)
    
    def _capture_spatial_snapshot(self, hour: int) -> SpatialSnapshot:
        """Capture spatial state at specific time"""
        # Collect all spatial data
        # Calculate grid-based densities
        # Return structured snapshot
```

#### Phase 3: Animation System (2-3 days)
**Goal**: Create animated heatmap visualizations

**Deliverables**:
- Time-series heatmap data generation
- Animated visualization engine
- Interactive controls (play/pause, scrubbing)
- Multiple heatmap types

**Technical Implementation**:
```python
def generate_animated_heatmap(simulation_data, output_file, heatmap_type='sticker_density'):
    """Generate animated heatmap visualization"""
    # Process spatial snapshots into animation frames
    # Create matplotlib animation or plotly animation
    # Add interactive controls
    # Export as video or interactive HTML
```

### Visualization Specifications

#### Heatmap Types

1. **Sticker Density Heatmap**
   - **Data Source**: Sticker locations and creation times
   - **Visualization**: Color intensity based on sticker count per grid cell
   - **Animation**: Show sticker placement over time
   - **Color Scheme**: Blue (low) → Green → Yellow → Red (high density)

2. **Player Activity Heatmap**
   - **Data Source**: Player locations and movement patterns
   - **Visualization**: Color intensity based on player count and activity
   - **Animation**: Show player movement and activity patterns
   - **Color Scheme**: Purple (low) → Blue → Green → Yellow (high activity)

3. **Scan Activity Heatmap**
   - **Data Source**: Scan events and locations
   - **Visualization**: Color intensity based on scan frequency
   - **Animation**: Show scanning hotspots and viral spread
   - **Color Scheme**: Dark blue (low) → Light blue → Green → Red (high activity)

4. **Value Concentration Heatmap**
   - **Data Source**: Sticker values and economic activity
   - **Visualization**: Color intensity based on economic value
   - **Animation**: Show value accumulation over time
   - **Color Scheme**: Dark green (low) → Light green → Yellow → Gold (high value)

5. **Viral Activity Heatmap**
   - **Data Source**: Sneeze mode stickers and viral spread
   - **Visualization**: Color intensity based on viral activity
   - **Animation**: Show viral hotspots and spread patterns
   - **Color Scheme**: Dark red (low) → Light red → Orange → Bright yellow (high viral)

#### Interactive Controls
- **Play/Pause**: Control animation playback
- **Time Scrubber**: Jump to specific time points
- **Speed Control**: Adjust animation speed (0.5x, 1x, 2x, 4x)
- **Layer Toggle**: Show/hide different heatmap types
- **Zoom/Pan**: Navigate the spatial area
- **Legend**: Show color scale and data ranges

### File Structure

```
fyndr/
├── heatmap_visualization/
│   ├── __init__.py
│   ├── spatial_analysis.py      # Grid system and density calculations
│   ├── data_collection.py      # Enhanced data tracking
│   ├── visualization_engine.py # Animation and rendering
│   ├── static_heatmaps.py      # Phase 1 static visualizations
│   └── animated_heatmaps.py    # Phase 3 animated visualizations
├── fyndr_life_simulator.py     # Enhanced with spatial tracking
└── analysis_tools.py           # Enhanced with heatmap analysis
```

### Configuration Options

```python
@dataclass
class HeatmapConfig:
    """Configuration for heatmap visualizations"""
    
    # Spatial settings
    grid_size: int = 50  # 50x50 grid cells
    simulation_bounds: Dict[str, Tuple[float, float]] = None  # lat/lng bounds
    
    # Temporal settings
    snapshot_frequency: str = 'hourly'  # 'daily', 'hourly', 'custom'
    animation_fps: int = 10  # Frames per second for animation
    
    # Visualization settings
    heatmap_types: List[str] = None  # Types to generate
    color_schemes: Dict[str, str] = None  # Color schemes per type
    output_formats: List[str] = None  # ['png', 'gif', 'mp4', 'html']
    
    # Performance settings
    max_frames: int = 1000  # Maximum frames for animation
    compression_quality: int = 85  # Image compression quality
```

### Performance Considerations

#### Data Storage
- **Spatial snapshots**: Store only essential data, compress older data
- **Grid calculations**: Cache density calculations, update incrementally
- **Animation frames**: Generate on-demand, cache frequently accessed frames

#### Rendering Performance
- **Grid resolution**: Configurable grid size (25x25, 50x50, 100x100)
- **Frame rate**: Adjustable FPS for different use cases
- **Compression**: Use efficient image formats and compression
- **Streaming**: For large animations, implement frame streaming

#### Memory Management
- **Lazy loading**: Load spatial data as needed
- **Frame caching**: Cache recent frames, purge old ones
- **Data compression**: Use efficient data structures and compression

### Testing Strategy

#### Unit Tests
- Grid system calculations
- Density computation algorithms
- Data structure serialization/deserialization

#### Integration Tests
- End-to-end heatmap generation
- Animation frame consistency
- Performance benchmarks

#### Visual Tests
- Compare generated heatmaps with expected patterns
- Validate color schemes and intensity ranges
- Test interactive controls and responsiveness

### Success Metrics

#### Functional Requirements
- ✅ Generate static heatmaps from existing data
- ✅ Create animated heatmaps with smooth transitions
- ✅ Support multiple heatmap types simultaneously
- ✅ Provide interactive controls for navigation

#### Performance Requirements
- ✅ Render 1000+ frame animations in <5 minutes
- ✅ Support real-time playback at 10+ FPS
- ✅ Handle simulations with 10,000+ stickers/players
- ✅ Generate output files <100MB for typical simulations

#### User Experience Requirements
- ✅ Intuitive controls for animation playback
- ✅ Clear visual distinction between heatmap types
- ✅ Smooth transitions between time periods
- ✅ Responsive interface for large datasets

## Implementation Timeline

### Week 1: Foundation
- **Days 1-2**: Phase 1 - Static heatmaps using existing data
- **Days 3-5**: Phase 2 - Enhanced data collection system

### Week 2: Animation
- **Days 1-3**: Phase 3 - Animation system and interactive controls
- **Days 4-5**: Testing, optimization, and documentation

### Week 3: Polish
- **Days 1-2**: Performance optimization and memory management
- **Days 3-5**: Advanced features, multiple heatmap types, export options

## Future Enhancements

### Advanced Features
- **3D Heatmaps**: Add elevation data for terrain-based analysis
- **Predictive Heatmaps**: Show predicted future activity patterns
- **Comparative Analysis**: Side-by-side heatmap comparisons
- **Export Options**: High-resolution video, interactive web visualizations

### Integration Opportunities
- **Real-time Analysis**: Live heatmap updates during simulation
- **Machine Learning**: Pattern recognition in heatmap data
- **API Integration**: REST API for heatmap data access
- **Dashboard Integration**: Embed heatmaps in analysis dashboards

## Conclusion

The animated heatmap visualization feature will provide powerful insights into the spatial and temporal dynamics of the FYNDR game simulation. By leveraging existing data and adding targeted enhancements, we can create compelling visualizations that reveal how player behavior, economic activity, and viral spread patterns evolve over time.

The phased implementation approach ensures we can deliver value incrementally while building toward a comprehensive visualization system that enhances the understanding and analysis of simulation results.
