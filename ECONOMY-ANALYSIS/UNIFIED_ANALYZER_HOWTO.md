# Unified FYNDR Analyzer - How-To Manual

## Overview

The `unified_fyndr_analyzer.py` script combines all the best features from the five original analysis scripts into a single, powerful tool for analyzing the FYNDR game economy. This script provides comprehensive 270-day simulations to find optimal parameter ranges for player growth, retention, and organic purchases.

## What It Does

The unified analyzer performs two main types of analysis:

1. **Focused Parameter Analysis** - Systematically tests critical game mechanics with specific parameter variations
2. **Comprehensive Optimization** - Uses parallel processing to test thousands of random parameter combinations

## Key Features

- **Advanced Simulation Engine** - 270-day simulations with retention mechanics, sticker decay, and seasonal events
- **Parallel Processing** - Uses multiple CPU cores to speed up optimization
- **Multiple Analysis Modes** - Focused testing, optimization, or both
- **Comprehensive Reporting** - Detailed analysis with parameter correlation
- **Multiple Export Formats** - JSON and CSV output for further analysis
- **Command-Line Interface** - Easy to use with various options

## Prerequisites

Before running the analyzer, ensure you have:

1. **Python 3.7+** installed
2. **Required dependencies**:
   - `numpy`
   - `pandas` (if using analysis tools)
   - `matplotlib` (if using visualization)
3. **The advanced simulator** - `advanced_economy_simulator.py` must be in the same directory

## Installation

1. Navigate to the `ECONOMY-ANALYSIS` directory
2. Ensure `advanced_economy_simulator.py` is present
3. Install dependencies if needed:
   ```bash
   pip install numpy pandas matplotlib
   ```

## Basic Usage

### Quick Start

Run the analyzer with default settings (both focused and optimization analysis):

```bash
python unified_fyndr_analyzer.py
```

### Command Line Options

```bash
python unified_fyndr_analyzer.py [OPTIONS]
```

**Available Options:**

- `--mode {focused,optimize,both,quick}` - Analysis mode to run (default: both)
- `--combinations N` - Number of parameter combinations for optimization (default: 500)
- `--days D` - Number of days to simulate (default: 270)
- `--processes P` - Number of parallel processes to use (default: auto-detect)
- `--prefix PREFIX` - Prefix for output files (default: unified_analysis)

### Analysis Modes

#### 1. Focused Analysis (`--mode focused`)

Tests specific parameter categories with predefined variations:

- **Pack Pricing** - Tests different price points and point costs
- **Scoring Mechanics** - Tests base points and unique scanner bonuses
- **Diversity Bonuses** - Tests geo diversity and venue variety bonuses
- **Retention Mechanics** - Tests churn rates and engagement bonuses
- **Engagement Mechanics** - Tests scan caps and player bonuses
- **Sticker Decay** - Tests decay rates and minimum values

**Example:**
```bash
python unified_fyndr_analyzer.py --mode focused
```

#### 2. Optimization Analysis (`--mode optimize`)

Runs comprehensive optimization across the entire parameter space:

- Tests random combinations of all parameters
- Uses parallel processing for speed
- Finds optimal parameter ranges through statistical analysis
- Provides parameter correlation analysis

**Example:**
```bash
python unified_fyndr_analyzer.py --mode optimize --combinations 1000
```

#### 3. Both Analyses (`--mode both`)

Runs both focused and optimization analysis (default):

**Example:**
```bash
python unified_fyndr_analyzer.py --mode both --combinations 500
```

#### 4. Quick Analysis (`--mode quick`)

Runs focused analysis + quick optimization (100 combinations):

**Example:**
```bash
python unified_fyndr_analyzer.py --mode quick
```

## Understanding the Output

### Console Output

The analyzer provides real-time progress updates and a comprehensive report:

```
Unified FYNDR Economy Analyzer
==================================================
Mode: both
Simulation Days: 270
Parameter Combinations: 500

================================================================================
FOCUSED PARAMETER ANALYSIS
================================================================================
Testing critical parameters for optimal game economy...

Running _test_pack_pricing...
  Completed: 7 tests
Running _test_scoring_mechanics...
  Completed: 7 tests
...

Focused analysis completed in 45.23 seconds
Total tests: 42

================================================================================
COMPREHENSIVE OPTIMIZATION ANALYSIS
================================================================================
Running optimization with 500 combinations over 270 days

Generated 500 parameter combinations
Using 8 processes
Completed 50/500 simulations
Completed 100/500 simulations
...

Optimization analysis completed in 234.56 seconds
Successful simulations: 487
```

### Comprehensive Report

The analyzer generates a detailed report including:

1. **Focused Analysis Results** - Best configurations by category
2. **Optimization Results** - Top 5 overall configurations
3. **Parameter Impact Analysis** - Most influential parameters
4. **Final Recommendations** - Optimal parameter ranges

### Export Files

The analyzer creates several output files:

#### JSON Files
- `{prefix}_focused_results.json` - Detailed focused analysis results
- `{prefix}_optimization_results.json` - Optimization results with parameter analysis

#### CSV Files
- `{prefix}_focused_results.csv` - Focused results in spreadsheet format
- `{prefix}_optimization_results.csv` - Optimization results in spreadsheet format

## Interpreting Results

### Key Metrics

The analyzer calculates three main scores:

1. **Growth Score** - Based on total players and retention rate
2. **Retention Score** - Based on retention rate and engagement
3. **Organic Purchase Score** - Based on non-whale purchases

**Overall Score** = (Growth × 0.4) + (Retention × 0.3) + (Organic × 0.3)

### Parameter Analysis

The analyzer provides correlation analysis showing which parameters most impact performance:

- **Positive Correlation** - Higher values improve performance
- **Negative Correlation** - Lower values improve performance
- **Near Zero** - Parameter has little impact

### Best Practices

1. **Start with Focused Analysis** - Use focused mode to understand basic parameter impacts
2. **Run Optimization** - Use optimization mode to find optimal combinations
3. **Analyze Correlations** - Look at parameter correlation to understand relationships
4. **Test Multiple Scenarios** - Run different combinations to validate findings
5. **Export and Analyze** - Use CSV files for deeper analysis in Excel/Google Sheets

## Advanced Usage

### Custom Parameter Ranges

To modify parameter ranges, edit the `_define_parameter_ranges()` method in the script:

```python
def _define_parameter_ranges(self) -> List[ParameterRange]:
    return [
        # Add or modify parameter ranges here
        ParameterRange("pack_price_dollars", 1.0, 6.0, 0.5, "float"),
        # ... other parameters
    ]
```

### Custom Scoring

To modify scoring algorithms, edit the scoring methods:

```python
def _calculate_growth_score(self, summary: Dict[str, Any]) -> float:
    # Modify growth score calculation here
    pass
```

### Custom Test Categories

To add new test categories, create new test methods:

```python
def _test_custom_mechanics(self) -> List[FocusedTestResult]:
    # Add custom test logic here
    pass
```

## Troubleshooting

### Common Issues

1. **Import Errors** - Ensure `advanced_economy_simulator.py` is in the same directory
2. **Memory Issues** - Reduce `--combinations` for large parameter spaces
3. **Slow Performance** - Increase `--processes` if you have more CPU cores
4. **Missing Dependencies** - Install required Python packages

### Performance Tips

1. **Use Quick Mode** - For initial testing and validation
2. **Adjust Combinations** - Start with fewer combinations and increase gradually
3. **Parallel Processing** - Use all available CPU cores for faster execution
4. **Monitor Progress** - Watch console output for progress updates

## Example Workflows

### 1. Initial Analysis

```bash
# Quick analysis to get started
python unified_fyndr_analyzer.py --mode quick

# Review results, then run full analysis
python unified_fyndr_analyzer.py --mode both --combinations 1000
```

### 2. Parameter Optimization

```bash
# Focus on optimization with many combinations
python unified_fyndr_analyzer.py --mode optimize --combinations 2000 --processes 16
```

### 3. Quick Testing

```bash
# Test specific parameters quickly
python unified_fyndr_analyzer.py --mode focused --days 90
```

### 4. Production Analysis

```bash
# Full analysis with custom output prefix
python unified_fyndr_analyzer.py --mode both --combinations 5000 --prefix production_analysis
```

## Output File Structure

### Focused Results CSV

| Column | Description |
|--------|-------------|
| test_name | Name of the test configuration |
| overall_score | Overall performance score |
| growth_score | Growth performance score |
| retention_score | Retention performance score |
| organic_purchase_score | Organic purchase performance score |
| total_players | Total active players |
| retention_rate | Player retention rate |
| organic_purchases | Number of organic purchases |
| total_revenue | Total revenue generated |

### Optimization Results CSV

| Column | Description |
|--------|-------------|
| overall_score | Overall performance score |
| growth_score | Growth performance score |
| retention_score | Retention performance score |
| organic_purchase_score | Organic purchase performance score |
| [parameter_name] | Value of each tested parameter |

## Next Steps

After running the analyzer:

1. **Review the Console Report** - Understand the key findings
2. **Analyze Export Files** - Use CSV files for deeper analysis
3. **Implement Recommendations** - Apply optimal parameters to your game
4. **A/B Test** - Test the recommended parameters in real scenarios
5. **Iterate** - Run additional analyses as you gather more data

## Support

For questions or issues:

1. Check the console output for error messages
2. Review the parameter ranges and test configurations
3. Ensure all dependencies are installed
4. Verify the advanced simulator is working correctly

## Conclusion

The Unified FYNDR Analyzer provides a comprehensive tool for understanding and optimizing your game economy. By combining focused parameter testing with comprehensive optimization, it helps you find the optimal balance between player growth, retention, and monetization.

Use this tool regularly as you develop your game to ensure your economy remains balanced and engaging for all player types.
