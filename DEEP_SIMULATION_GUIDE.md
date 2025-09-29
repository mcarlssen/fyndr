# Deep Simulation Guide

## Overview

The Deep Simulation feature addresses the variance issue in FYNDR Life Simulator where minmax spreads can cause simulations to vary widely in output. By running multiple simulations and averaging their results, you get more stable and reliable analysis.

## Key Features

- **Multi-run Averaging**: Runs 15 simulations (configurable) and averages all results
- **Variance Analysis**: Provides coefficient of variation metrics to understand simulation stability
- **Comprehensive Analysis**: Executes full analysis on averaged results
- **Flexible Configuration**: Works with any configuration file or OKR results

## Usage

### Command Line Interface

#### Using the Main Simulator
```bash
# Run deep simulation with default settings (15 runs, 365 days)
python fyndr_life_simulator.py --deep-simulation --days 365

# Run with custom number of simulations
python fyndr_life_simulator.py --deep-simulation --days 180 --deep-simulations 10

# Run with console output during simulations
python fyndr_life_simulator.py --deep-simulation --days 365 --deep-console-output

# Use with OKR results
python fyndr_life_simulator.py --deep-simulation --okr-results results.json --days 270
```

#### Using the Deep Simulation Runner Directly
```bash
# Basic usage
python deep_simulation_runner.py --days 365

# With custom configuration
python deep_simulation_runner.py --config my_config.json --days 180 --simulations 20

# With OKR results
python deep_simulation_runner.py --okr-results okr_results.json --days 270 --simulations 15

# Skip analysis (faster for testing)
python deep_simulation_runner.py --days 30 --simulations 5 --no-analysis
```

### Programmatic Usage

```python
from deep_simulation_runner import run_deep_simulation, DeepSimulationRunner
from fyndr_life_simulator import LifeSimConfig

# Method 1: Convenience function
result = run_deep_simulation(
    config_file="my_config.json",
    days=365,
    num_simulations=15,
    enable_console_output=False,
    auto_analyze=True
)

# Method 2: Direct usage
config = LifeSimConfig()
runner = DeepSimulationRunner(config, num_simulations=15)
result = runner.run_deep_simulation(days=365, auto_analyze=True)
```

## Output and Analysis

### Generated Files

The deep simulation creates several output files:

1. **Averaged Simulation State**: `deep_sim_YYYYMMDD_HHMMSS.json`
2. **Analysis Directory**: `deep_sim_YYYYMMDD_HHMMSS_analysis/`
   - Complete summary report
   - Level-focused analysis
   - Visualizations
   - CSV exports

### Key Metrics

The deep simulation provides enhanced metrics:

- **Averaged Values**: Mean values across all simulations
- **Standard Deviation**: Variability of each metric
- **Coefficient of Variation**: Relative variability (lower = more stable)

Example output:
```
DEEP SIMULATION ANALYSIS SUMMARY
============================================================
Number of simulations averaged: 15
Final Active Players: 1,234.5 ± 45.2
Total Revenue: $12,345.67 ± $1,234.56
Total Scans: 45,678 ± 2,345
Total Stickers: 8,901 ± 456

Simulation Variance (Coefficient of Variation):
  Revenue: 10.0%
  Scans: 5.1%
  Players: 3.7%
```

## When to Use Deep Simulation

### Recommended Scenarios

1. **Parameter Optimization**: When testing new game parameters
2. **Economic Analysis**: When analyzing revenue and retention patterns
3. **Long-term Planning**: For strategic decisions requiring stable metrics
4. **Research**: When publishing results that need statistical validity

### When NOT to Use

1. **Quick Testing**: For rapid iteration during development
2. **Real-time Monitoring**: When you need immediate feedback
3. **Resource Constraints**: When computational resources are limited

## Performance Considerations

### Computational Cost

- **Time**: ~15x longer than single simulation
- **Memory**: Similar to single simulation (runs sequentially)
- **Storage**: Generates more output files

### Optimization Tips

1. **Reduce Days**: Use shorter simulations for initial testing
2. **Fewer Simulations**: Start with 5-10 simulations for testing
3. **Disable Analysis**: Use `--no-analysis` for faster testing
4. **Parallel Processing**: Future enhancement planned

## Configuration Options

### Deep Simulation Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--simulations` | 15 | Number of simulations to run |
| `--days` | 365 | Days per simulation |
| `--console-output` | False | Show progress during simulations |
| `--no-analysis` | False | Skip analysis generation |

### Integration with Existing Features

- **OKR Results**: Works with optimized parameters from OKR analysis
- **Configuration Files**: Compatible with all existing config formats
- **Analysis Tools**: Uses existing analysis infrastructure
- **Visualizations**: Generates same charts as single simulations

## Troubleshooting

### Common Issues

1. **Memory Errors**: Reduce number of simulations or days
2. **Long Runtime**: Use shorter simulations for testing
3. **No Variance**: Check if parameters have sufficient randomness
4. **Analysis Errors**: Ensure all dependencies are installed

### Debug Mode

For troubleshooting, run with console output:
```bash
python fyndr_life_simulator.py --deep-simulation --deep-console-output --days 30 --deep-simulations 3
```

## Testing

Run the test suite to verify functionality:
```bash
python test_deep_simulation.py
```

This will:
1. Test individual simulation variance
2. Test deep simulation averaging
3. Verify analysis generation
4. Provide usage examples

## Future Enhancements

Planned improvements:
- **Parallel Processing**: Run simulations concurrently
- **Progressive Averaging**: Show results as simulations complete
- **Variance Thresholds**: Stop when variance is below threshold
- **Custom Metrics**: User-defined averaging functions
- **Real-time Monitoring**: Live progress updates

## Technical Details

### Averaging Algorithm

The deep simulation uses statistical averaging:

1. **Numeric Fields**: Arithmetic mean across all simulations
2. **Boolean Fields**: Most common value (mode)
3. **Categorical Fields**: Most common value
4. **Time Series**: Day-by-day averaging
5. **Variance Metrics**: Standard deviation and coefficient of variation

### Data Structures

- **AveragedDailyStats**: Averaged daily statistics
- **AveragedPlayer**: Averaged player data
- **AveragedSticker**: Averaged sticker data
- **Variance Metrics**: Statistical variance information

### Analysis Integration

The deep simulation integrates with existing analysis tools:
- **CompleteSimulationAnalyzer**: For comprehensive analysis
- **Visualization Engine**: For charts and graphs
- **CSV Export**: For spreadsheet analysis
- **JSON Export**: For programmatic access

## Examples

### Basic Deep Simulation
```bash
# Run 15 simulations of 365 days each
python fyndr_life_simulator.py --deep-simulation --days 365
```

### Custom Configuration
```bash
# Use custom config with 10 simulations
python fyndr_life_simulator.py --deep-simulation --config my_config.json --days 180 --deep-simulations 10
```

### OKR Optimized Deep Simulation
```bash
# Use OKR-optimized parameters
python fyndr_life_simulator.py --deep-simulation --okr-results okr_results.json --days 270
```

### Testing Mode
```bash
# Quick test with minimal simulations
python fyndr_life_simulator.py --deep-simulation --days 30 --deep-simulations 3 --deep-console-output
```

This deep simulation feature provides a robust solution for reducing variance in simulation results while maintaining all the analytical capabilities of the original simulator.
