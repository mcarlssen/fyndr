# FYNDR Game Economy Simulator - User's Manual

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Understanding the Simulator](#understanding-the-simulator)
4. [Configuration Options](#configuration-options)
5. [Running Simulations](#running-simulations)
6. [Interpreting Results](#interpreting-results)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

## Overview

The FYNDR Game Economy Simulator is a comprehensive tool designed to test and refine the game's economic balance. It models three distinct player types (whales, grinders, and casual players) and simulates their interactions with the sticker-based economy over time.

### What the Simulator Does
- **Models Player Behavior**: Simulates realistic player actions based on their type
- **Tracks Economic Metrics**: Monitors revenue, points, engagement, and balance
- **Tests Scenarios**: Allows you to experiment with different economic configurations
- **Exports Data**: Generates CSV files for detailed analysis

### Key Components
- **Core Simulator** (`fyndr_simulator.py`): Main simulation engine
- **Configuration Manager** (`config_manager.py`): Pre-built scenarios and custom configurations
- **Analysis Tools** (`analysis_tools.py`): Data analysis and visualization
- **Interactive Interface** (`simulator_interface.py`): User-friendly command-line interface

## Quick Start

### Basic Simulation
```python
from fyndr_simulator import FYNDRSimulator, GameConfig

# Create a simulator with default settings
config = GameConfig()
simulator = FYNDRSimulator(config)

# Run a 30-day simulation
simulator.run_simulation(30)

# Get results
summary = simulator.get_economy_summary()
print(f"Total Revenue: ${summary['total_revenue']:.2f}")
print(f"Total Points: {summary['total_points']:,}")

# Export data to CSV files
simulator.export_data("my_simulation")
```

### Using Pre-built Scenarios
```python
from config_manager import ConfigManager

# Load scenario manager
manager = ConfigManager()

# Run a specific scenario
simulator = manager.run_scenario('whale_heavy')

# Compare multiple scenarios
results = manager.compare_scenarios(['baseline', 'whale_heavy', 'grinder_friendly'])
```

## Understanding the Simulator

### Player Types

**Whales (High Spenders)**
- **Behavior**: Buy sticker packs weekly (80% chance)
- **Spending**: $3-9 per week on average
- **Activity**: 5-12 scans per day
- **Strategy**: Focus on sticker placement for passive income

**Grinders (High Activity)**
- **Behavior**: Scan heavily (15-25 scans per day)
- **Spending**: Occasional pack purchase with earned points
- **Activity**: Most scanning activity in the game
- **Strategy**: Maximize points through active scanning

**Casual Players (Moderate Engagement)**
- **Behavior**: Moderate scanning (3-8 scans per day)
- **Spending**: Infrequent purchases (every 3 weeks, 40% chance)
- **Activity**: Baseline engagement
- **Strategy**: Occasional participation

### Economic Mechanics

**Point System**
- **Scanner Points**: 1.0 base points per scan
- **Owner Points**: 2.0 base points per scan of their sticker
- **Bonuses**: Unique scan (+1), geo diversity (+1), venue variety (+1)
- **Diminishing Returns**: Reduced rewards after 3+ scans per sticker per day

**Monetization**
- **Pack Price**: $3.00 (configurable)
- **Point Cost**: 300 points per pack (configurable)
- **Revenue Sources**: Pack sales, wallet top-ups, rewarded ads

**Balance Mechanisms**
- **Daily Scan Cap**: 20 scans per player per day
- **Weekly Earn Cap**: 500 points per player per week
- **Level Multipliers**: 1.0x to 1.2x based on progression

## Configuration Options

### GameConfig Parameters

**Base Scoring**
```python
config = GameConfig(
    owner_base_points=2.0,      # Points owner gets per scan
    scanner_base_points=1.0,    # Points scanner gets per scan
    unique_scanner_bonus=1.0,   # Bonus for first scan of sticker
)
```

**Diminishing Returns**
```python
config = GameConfig(
    diminishing_threshold=3,           # Scans before diminishing returns
    diminishing_rates=[1.0, 0.5, 0.25] # Full, half, quarter rewards
)
```

**Diversity Bonuses**
```python
config = GameConfig(
    geo_diversity_radius=500.0,    # Meters for geo diversity
    geo_diversity_bonus=1.0,       # Points for geo diversity
    venue_variety_bonus=1.0,       # Points for venue variety
)
```

**Economy Settings**
```python
config = GameConfig(
    pack_price_dollars=3.0,    # Real money price
    pack_price_points=300,     # Points cost
    points_per_dollar=100.0,   # Wallet conversion rate
)
```

**Player Behavior**
```python
config = GameConfig(
    daily_scan_cap=20,         # Max scans per day
    weekly_earn_cap=500,       # Max points per week
)
```

### Pre-built Scenarios

**Baseline Economy**
- Balanced whale/grinder/casual distribution
- Standard pricing and mechanics
- Good starting point for testing

**Whale-Heavy Economy**
- 25 whales, 30 grinders, 50 casuals
- Lower pack price ($2.50) to encourage purchases
- Higher owner rewards (2.5 points)

**Grinder-Friendly Economy**
- 5 whales, 80 grinders, 50 casuals
- Lower point cost (250 points per pack)
- Higher scanner rewards (1.5 points)
- Higher daily scan cap (30)

**High-Engagement Economy**
- Emphasizes social and exploration behaviors
- Higher social sneeze bonus (5.0 points)
- Higher diversity bonuses (2.0 points each)

**Premium Pricing Economy**
- Higher pack price ($5.00)
- Higher point cost (500 points)
- Enhanced level multipliers (up to 1.4x)

## Running Simulations

### Method 1: Direct Python Script
```python
from fyndr_simulator import FYNDRSimulator, GameConfig

# Create custom configuration
config = GameConfig()
config.pack_price_dollars = 4.0
config.scanner_base_points = 1.5

# Run simulation
simulator = FYNDRSimulator(config)
simulator.run_simulation(60)  # 60-day simulation

# Get results
summary = simulator.get_economy_summary()
print(f"Revenue: ${summary['total_revenue']:.2f}")
```

### Method 2: Using Configuration Manager
```python
from config_manager import ConfigManager

manager = ConfigManager()

# Run single scenario
simulator = manager.run_scenario('whale_heavy')

# Compare scenarios
results = manager.compare_scenarios(['baseline', 'whale_heavy'])

# Create custom scenario
custom_config = {
    'pack_price_dollars': 3.5,
    'scanner_base_points': 1.2,
    'daily_scan_cap': 25
}
scenario_id = manager.create_custom_scenario(
    name="Custom Test",
    description="Testing $3.50 pack price",
    config_dict=custom_config,
    initial_players={'whale': 15, 'grinder': 60, 'casual': 80}
)
```

### Method 3: Interactive Interface
```bash
python simulator_interface.py
```

This launches an interactive menu where you can:
- Run default simulations
- Compare scenarios
- Create custom scenarios
- Analyze results

## Interpreting Results

### Key Metrics

**Revenue Metrics**
- `total_revenue`: Total money spent by all players
- `avg_revenue_per_player`: Average spending per player
- `revenue_by_type`: Revenue breakdown by player type

**Engagement Metrics**
- `total_points`: Total points earned by all players
- `total_scans`: Total number of scan events
- `points_per_scan`: Average points per scan event
- `avg_points_per_player`: Average points per player

**Player Distribution**
- `player_types`: Count of each player type
- `total_players`: Total number of players
- `total_stickers`: Total number of stickers in game

### Understanding the Data

**Revenue Analysis**
- **Whale Revenue Share**: Should be 30-50% for healthy balance
- **Revenue Growth**: Look for steady growth over time
- **Revenue Volatility**: Lower is better for stability

**Engagement Analysis**
- **Points per Scan**: Should be 1.5-2.0 for good balance
- **Player Retention**: Percentage of players with >0 points
- **Activity Distribution**: How scanning is distributed among player types

**Balance Indicators**
- **Whale Advantage**: Whales should have higher revenue but not overwhelming
- **Grinder Viability**: Grinders should be able to compete through activity
- **Casual Accessibility**: Casual players should have meaningful progression

### CSV Output Files

**Daily Stats** (`*_daily_stats.csv`)
- Day-by-day metrics
- Player counts, revenue, points, scans
- Useful for trend analysis

**Player Data** (`*_players.csv`)
- Individual player statistics
- Points, spending, stickers owned
- Useful for player behavior analysis

**Sticker Data** (`*_stickers.csv`)
- Individual sticker performance
- Scans, earnings, venue categories
- Useful for placement strategy analysis

## Advanced Usage

### Custom Player Distributions
```python
# Test different player mixes
distributions = [
    {'whale': 10, 'grinder': 50, 'casual': 100},  # Baseline
    {'whale': 25, 'grinder': 30, 'casual': 50},   # Whale-heavy
    {'whale': 5, 'grinder': 80, 'casual': 50},    # Grinder-heavy
]

for dist in distributions:
    simulator = FYNDRSimulator(GameConfig())
    simulator.run_simulation(30, dist)
    summary = simulator.get_economy_summary()
    print(f"Distribution {dist}: Revenue ${summary['total_revenue']:.2f}")
```

### Price Sensitivity Testing
```python
# Test different pack prices
prices = [2.0, 3.0, 4.0, 5.0]
for price in prices:
    config = GameConfig()
    config.pack_price_dollars = price
    simulator = FYNDRSimulator(config)
    simulator.run_simulation(30)
    summary = simulator.get_economy_summary()
    print(f"Price ${price}: Revenue ${summary['total_revenue']:.2f}")
```

### Long-term Analysis
```python
# Run extended simulation
simulator = FYNDRSimulator(GameConfig())
simulator.run_simulation(90)  # 3-month simulation

# Analyze trends
daily_data = simulator.daily_stats
revenue_trend = [day['total_revenue'] for day in daily_data]
print(f"Revenue growth: {revenue_trend[-1] - revenue_trend[0]:.2f}")
```

### Using Analysis Tools
```python
from analysis_tools import FYNDRAnalyzer

# Load simulation data
analyzer = FYNDRAnalyzer()
analyzer.load_simulation_data(
    'my_simulation_daily_stats.csv',
    'my_simulation_players.csv',
    'my_simulation_stickers.csv'
)

# Generate analysis report
report = analyzer.generate_economy_report()
print(report)

# Create visualizations
analyzer.create_visualizations('analysis_plots')
```

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure all Python files are in the same directory
- Check that required packages are installed (pandas, matplotlib, seaborn)

**Configuration Errors**
- Verify parameter values are within reasonable ranges
- Check that player distributions sum to expected totals

**Simulation Issues**
- Ensure sufficient players for meaningful results (minimum 50 total)
- Check that simulation duration is appropriate (7+ days recommended)

**Data Export Issues**
- Verify write permissions in output directory
- Check that simulation has completed successfully before exporting

### Performance Tips

**Large Simulations**
- Use fewer players for quick testing
- Increase simulation duration gradually
- Monitor memory usage for very large simulations

**Data Analysis**
- Use CSV files for external analysis tools
- Consider sampling for very large datasets
- Export only necessary data to reduce file sizes

### Getting Help

**Debugging**
- Add print statements to track simulation progress
- Use smaller simulations to test configurations
- Check individual player and sticker data for anomalies

**Configuration Testing**
- Start with baseline scenario and modify one parameter at a time
- Use scenario comparison to identify optimal settings
- Document successful configurations for future reference

---

## Conclusion

The FYNDR Game Economy Simulator provides a powerful tool for testing and optimizing your game's economic balance. By understanding the different player types, configuration options, and result interpretation, you can make data-driven decisions about pricing, mechanics, and balance.

Remember to:
- Start with baseline scenarios
- Test one parameter at a time
- Use multiple simulation runs for statistical significance
- Analyze both revenue and engagement metrics
- Consider long-term trends and player retention

Happy simulating!