# FYNDR Life Simulator Manual

## Overview

The FYNDR Life Simulator is a comprehensive, indefinite-running simulator that models the day-to-day life of the FYNDR game using optimized parameters from the OKR analysis. It simulates real player behavior, economic interactions, and game growth over time.

## Key Features

- **Indefinite Running**: Can run forever or for a specified number of days
- **Real-time Monitoring**: Live console output with key metrics
- **JSON Configuration**: Easy parameter modification via JSON files
- **State Persistence**: Save and load simulation states
- **OKR Integration**: Automatically loads optimized parameters from OKR analysis
- **Comprehensive Game Mechanics**: All game features implemented
- **Growth Modeling**: Realistic player acquisition and churn
- **Economic Tracking**: Revenue, points, and monetization metrics

## Quick Start

### 1. Generate Configuration Template
```bash
python fyndr_life_simulator.py --template
```

### 2. Run with OKR-Optimized Parameters
```bash
python fyndr_life_simulator.py --okr-results ECONOMY-ANALYSIS/okr_v2_optimized_results.json --days 365 --speed 5
```

### 3. Run with Custom Configuration
```bash
python fyndr_life_simulator.py --config my_config.json --days 0 --speed 1
```

## Command Line Options

- `--config FILE`: Load configuration from JSON file
- `--okr-results FILE`: Load configuration from OKR optimization results
- `--days N`: Run for N days (0 = unlimited)
- `--speed X`: Simulation speed multiplier (1.0 = real time, 10.0 = 10x faster)
- `--template`: Generate configuration template file
- `--load-state FILE`: Load existing simulation state

## Configuration Parameters

### Simulation Control
- `simulation_name`: Name for this simulation run
- `max_days`: Maximum days to run (0 = unlimited)
- `real_time_speed`: Speed multiplier for simulation
- `auto_save_interval`: Days between automatic saves
- `enable_visualization`: Enable real-time charts (future feature)
- `enable_console_output`: Show daily progress in console

### Core Scoring Parameters
- `owner_base_points`: Points awarded for placing a sticker
- `scanner_base_points`: Base points for scanning a sticker
- `unique_scanner_bonus`: Bonus for being first to scan a sticker
- `diminishing_threshold`: Number of scans before diminishing returns kick in
- `diminishing_rates`: List of diminishing return multipliers

### Diversity Bonuses
- `geo_diversity_radius`: Minimum distance (meters) for geographic diversity
- `geo_diversity_bonus`: Bonus multiplier for geographic diversity
- `venue_variety_bonus`: Bonus multiplier for venue variety

### Social Mechanics
- `social_sneeze_threshold`: Minimum scans needed for social sneeze bonus
- `social_sneeze_bonus`: Bonus multiplier for social sneeze
- `social_sneeze_cap`: Maximum social sneeze bonuses per day

### Leveling System
- `level_multipliers`: List of level-based point multipliers
- `points_per_level`: Points required to level up
- `max_level`: Maximum player level

### Monetization
- `pack_price_points`: Points cost for a sticker pack
- `pack_price_dollars`: Dollar cost for a sticker pack
- `points_per_dollar`: Points received per dollar spent
- `wallet_topup_min`: Minimum wallet top-up amount
- `wallet_topup_max`: Maximum wallet top-up amount

### Earning Caps
- `weekly_earn_cap`: Maximum points earned per week
- `daily_passive_cap`: Maximum passive points per day

### Scanning Mechanics
- `sticker_scan_cooldown_hours`: Hours before a sticker can be scanned again

### Churn and Retention
- `churn_probability_base`: Base churn probability
- `churn_probability_whale`: Whale churn probability
- `churn_probability_grinder`: Grinder churn probability
- `churn_probability_casual`: Casual churn probability

### Bonus Systems
- `streak_bonus_days`: Days of activity needed for streak bonus
- `streak_bonus_multiplier`: Streak bonus multiplier
- `comeback_bonus_days`: Days away needed for comeback bonus
- `comeback_bonus_multiplier`: Comeback bonus multiplier

### New Player Onboarding
- `new_player_bonus_days`: Days new players get bonus
- `new_player_bonus_multiplier`: New player bonus multiplier
- `new_player_free_packs`: Free packs for new players

### Events
- `event_frequency_days`: Days between special events
- `event_duration_days`: Duration of special events
- `event_bonus_multiplier`: Event bonus multiplier

### Growth Parameters
- `new_player_daily_probability`: Daily probability of new players
- `new_player_whale_probability`: Probability new player is whale
- `new_player_grinder_probability`: Probability new player is grinder
- `new_player_casual_probability`: Probability new player is casual

### Venue Diversity
- `venue_types`: List of venue types
- `venue_type_weights`: Probability weights for venue types

## Player Types

### Whales (5% of population)
- High spending behavior
- Frequent sticker placement
- High scanning activity
- Low churn probability
- High wallet top-ups

### Grinders (25% of population)
- Very active scanning
- Frequent sticker placement
- No spending behavior
- Low churn probability
- High engagement

### Casual Players (70% of population)
- Moderate activity
- Occasional spending
- Social engagement focus
- Higher churn probability
- Balanced behavior

## Daily Statistics

The simulator tracks comprehensive daily statistics:

- **Player Metrics**: Total players, active players, new players, churned players
- **Economic Metrics**: Total revenue, revenue by player type
- **Engagement Metrics**: Total scans, stickers placed, points earned
- **Growth Metrics**: Retention rate, growth rate, average level
- **Player Distribution**: Count by player type

## File Outputs

### Simulation State Files
- `fyndr_life_sim_YYYYMMDD_HHMMSS.json`: Complete simulation state
- Contains all players, stickers, daily stats, and configuration
- Can be loaded to resume simulation

### Configuration Files
- `fyndr_life_config_template.json`: Template configuration
- `fyndr_okr_optimized_config.json`: OKR-optimized configuration

## Usage Examples

### Run a 30-day simulation with OKR parameters
```bash
python fyndr_life_simulator.py --okr-results ECONOMY-ANALYSIS/okr_v2_optimized_results.json --days 30 --speed 10
```

### Run indefinitely with custom config
```bash
python fyndr_life_simulator.py --config my_config.json --days 0 --speed 1
```

### Generate and modify configuration
```bash
python fyndr_life_simulator.py --template
# Edit fyndr_life_config_template.json
python fyndr_life_simulator.py --config fyndr_life_config_template.json --days 100
```

### Resume from saved state
```bash
python fyndr_life_simulator.py --load-state fyndr_life_sim_20250917_175329.json --days 0
```

## Monitoring and Analysis

### Console Output
The simulator provides real-time console output showing:
- Current day
- Active player count
- Total revenue
- Total scans
- Stickers placed
- Retention rate
- Growth rate

### State Files
Simulation state files contain complete game state and can be analyzed for:
- Player behavior patterns
- Economic trends
- Growth trajectories
- Engagement metrics

## Advanced Features

### Real-time Speed Control
- `--speed 0.1`: 10x slower than real time (detailed observation)
- `--speed 1.0`: Real time
- `--speed 10.0`: 10x faster than real time (quick runs)

### Auto-save
- Automatically saves state every N days (configurable)
- Prevents data loss during long runs
- Enables resuming interrupted simulations

### Parameter Modification
- All parameters can be modified via JSON configuration
- Changes take effect immediately when loaded
- No code changes required for parameter tuning

## Integration with OKR Analysis

The simulator seamlessly integrates with the OKR optimization results:

1. **Automatic Parameter Loading**: Loads best parameters from OKR analysis
2. **Optimized Starting Point**: Uses proven optimal configurations
3. **Real-world Validation**: Tests parameters in realistic long-term scenarios
4. **Performance Monitoring**: Tracks how optimized parameters perform over time

## Troubleshooting

### Common Issues

1. **JSON Serialization Errors**: Fixed in latest version
2. **Memory Usage**: Long runs may use significant memory
3. **File Permissions**: Ensure write access for state files
4. **Configuration Errors**: Validate JSON syntax before running

### Performance Tips

1. **Use Higher Speed**: Set `--speed 10` for faster runs
2. **Reduce Auto-save Frequency**: Set higher `auto_save_interval`
3. **Monitor Memory**: Long runs with many players use more memory
4. **Save Regularly**: Use auto-save to prevent data loss

## Future Enhancements

- Real-time visualization dashboard
- Advanced analytics and reporting
- Multi-threaded simulation for faster processing
- Web-based monitoring interface
- Export to CSV/Excel for analysis
- Integration with external analytics tools

## Support

For issues or questions:
1. Check the console output for error messages
2. Validate JSON configuration files
3. Ensure all required parameters are set
4. Check file permissions for state saving
