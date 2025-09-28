#!/usr/bin/env python3
"""
Visualization Engine for OKR-Optimized FYNDR Economy Analyzer

This module provides comprehensive visualization capabilities for analyzing
parameter relationships, correlations, and optimization results.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import json
from typing import List, Dict, Any, Tuple
import os
from dataclasses import asdict

class FYNDRVisualizationEngine:
    """Comprehensive visualization engine for FYNDR economy analysis"""
    
    def __init__(self, output_dir: str = "visualizations"):
        self.output_dir = output_dir
        self.setup_plotting_style()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def setup_plotting_style(self):
        """Setup consistent plotting style"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Set figure parameters
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
    
    def create_parameter_score_scatter(self, results_data: List[Dict], player_type: str, 
                                     parameter_name: str, score_name: str) -> str:
        """Create scatter plot of parameter values vs scores"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract data
        param_values = []
        scores = []
        
        for result in results_data:
            if result.get('config', {}).get(parameter_name) is not None:
                param_values.append(result['config'][parameter_name])
                scores.append(result[score_name])
        
        # Create scatter plot
        scatter = ax.scatter(param_values, scores, alpha=0.7, s=60, 
                           c=scores, cmap='viridis', edgecolors='black', linewidth=0.5)
        
        # Add trend line
        if len(param_values) > 1:
            z = np.polyfit(param_values, scores, 1)
            p = np.poly1d(z)
            ax.plot(param_values, p(param_values), "r--", alpha=0.8, linewidth=2)
        
        # Customize plot
        ax.set_xlabel(f'{parameter_name.replace("_", " ").title()}')
        ax.set_ylabel(f'{score_name.replace("_", " ").title()}')
        ax.set_title(f'{player_type.title()} Optimization: {parameter_name.replace("_", " ").title()} vs {score_name.replace("_", " ").title()}')
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label(f'{score_name.replace("_", " ").title()}')
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Save plot
        filename = f"{self.output_dir}/{player_type}_{parameter_name}_vs_{score_name}_scatter.svg"
        plt.tight_layout()
        plt.savefig(filename, format='svg', dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def create_correlation_heatmap(self, results_data: List[Dict], player_type: str) -> str:
        """Create correlation heatmap for all parameters and scores"""
        # Prepare data for correlation analysis
        data_dict = {}
        
        # Extract all parameter values and scores
        for result in results_data:
            config = result.get('config', {})
            for param_name, param_value in config.items():
                if isinstance(param_value, (int, float)) and not isinstance(param_value, bool):
                    if param_name not in data_dict:
                        data_dict[param_name] = []
                    data_dict[param_name].append(param_value)
        
        # Add score columns
        score_columns = ['whale_score', 'grinder_score', 'casual_score', 'overall_score', 'revenue', 'userbase']
        for score_col in score_columns:
            if score_col in results_data[0]:
                data_dict[score_col] = [result.get(score_col, 0) for result in results_data]
        
        # Create DataFrame
        df = pd.DataFrame(data_dict)
        
        # Calculate correlation matrix
        correlation_matrix = df.corr()
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(16, 12))
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        # Create heatmap
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdBu_r', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, fmt='.2f')
        
        ax.set_title(f'{player_type.title()} Optimization: Parameter Correlation Matrix')
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        # Save plot
        filename = f"{self.output_dir}/{player_type}_correlation_heatmap.svg"
        plt.tight_layout()
        plt.savefig(filename, format='svg', dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def create_parameter_distribution_plot(self, results_data: List[Dict], player_type: str) -> str:
        """Create distribution plots for key parameters"""
        # Select key parameters to visualize
        key_params = [
            'owner_base_points', 'scanner_base_points', 'pack_price_dollars', 
            'geo_diversity_bonus', 'social_sneeze_bonus', 'churn_probability_whale',
            'churn_probability_grinder', 'churn_probability_casual'
        ]
        
        # Create subplots
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        axes = axes.flatten()
        
        for i, param in enumerate(key_params):
            if i >= len(axes):
                break
                
            # Extract parameter values
            param_values = []
            scores = []
            
            for result in results_data:
                if result.get('config', {}).get(param) is not None:
                    param_values.append(result['config'][param])
                    scores.append(result.get('overall_score', 0))
            
            if param_values:
                # Create scatter plot with color-coded scores
                scatter = axes[i].scatter(param_values, scores, alpha=0.7, s=50, 
                                        c=scores, cmap='viridis', edgecolors='black', linewidth=0.3)
                
                axes[i].set_xlabel(param.replace('_', ' ').title())
                axes[i].set_ylabel('Overall Score')
                axes[i].set_title(f'{param.replace("_", " ").title()}')
                axes[i].grid(True, alpha=0.3)
        
        # Remove empty subplots
        for i in range(len(key_params), len(axes)):
            fig.delaxes(axes[i])
        
        plt.suptitle(f'{player_type.title()} Optimization: Parameter Distributions', fontsize=16)
        
        # Save plot
        filename = f"{self.output_dir}/{player_type}_parameter_distributions.svg"
        plt.tight_layout()
        plt.savefig(filename, format='svg', dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def create_multiplayer_analysis_plot(self, results_data: List[Dict]) -> str:
        """Create comprehensive multi-player analysis visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Extract data
        whale_scores = [r.get('whale_score', 0) for r in results_data]
        grinder_scores = [r.get('grinder_score', 0) for r in results_data]
        casual_scores = [r.get('casual_score', 0) for r in results_data]
        overall_scores = [r.get('overall_score', 0) for r in results_data]
        revenues = [r.get('revenue', 0) for r in results_data]
        userbases = [r.get('userbase', 0) for r in results_data]
        
        # Plot 1: Score comparison
        x_pos = range(len(results_data))
        width = 0.2
        
        axes[0, 0].bar([x - width for x in x_pos], whale_scores, width, label='Whale Score', alpha=0.8)
        axes[0, 0].bar(x_pos, grinder_scores, width, label='Grinder Score', alpha=0.8)
        axes[0, 0].bar([x + width for x in x_pos], casual_scores, width, label='Casual Score', alpha=0.8)
        axes[0, 0].set_xlabel('Configuration Index')
        axes[0, 0].set_ylabel('Score')
        axes[0, 0].set_title('Multi-Player Score Comparison')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Revenue vs Userbase
        scatter = axes[0, 1].scatter(userbases, revenues, c=overall_scores, cmap='viridis', 
                                   s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
        axes[0, 1].set_xlabel('Userbase')
        axes[0, 1].set_ylabel('Revenue ($)')
        axes[0, 1].set_title('Revenue vs Userbase (colored by Overall Score)')
        cbar = plt.colorbar(scatter, ax=axes[0, 1])
        cbar.set_label('Overall Score')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Overall score distribution
        axes[1, 0].hist(overall_scores, bins=20, alpha=0.7, edgecolor='black')
        axes[1, 0].set_xlabel('Overall Score')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Overall Score Distribution')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Score correlations
        score_data = pd.DataFrame({
            'Whale': whale_scores,
            'Grinder': grinder_scores,
            'Casual': casual_scores,
            'Overall': overall_scores
        })
        
        correlation_matrix = score_data.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='RdBu_r', center=0,
                   square=True, ax=axes[1, 1], cbar_kws={"shrink": 0.8})
        axes[1, 1].set_title('Score Correlation Matrix')
        
        plt.suptitle('Multi-Player Optimization Analysis', fontsize=16)
        
        # Save plot
        filename = f"{self.output_dir}/multiplayer_analysis.svg"
        plt.tight_layout()
        plt.savefig(filename, format='svg', dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def create_optimization_progress_plot(self, iteration_results: List[Dict]) -> str:
        """Create plot showing optimization progress across iterations"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # Extract iteration data
        iterations = list(range(1, len(iteration_results) + 1))
        whale_scores = [r.get('whale_score', 0) for r in iteration_results]
        grinder_scores = [r.get('grinder_score', 0) for r in iteration_results]
        casual_scores = [r.get('casual_score', 0) for r in iteration_results]
        overall_scores = [r.get('overall_score', 0) for r in iteration_results]
        
        # Plot 1: Score progression
        axes[0, 0].plot(iterations, whale_scores, 'o-', label='Whale Score', linewidth=2, markersize=6)
        axes[0, 0].plot(iterations, grinder_scores, 's-', label='Grinder Score', linewidth=2, markersize=6)
        axes[0, 0].plot(iterations, casual_scores, '^-', label='Casual Score', linewidth=2, markersize=6)
        axes[0, 0].plot(iterations, overall_scores, 'd-', label='Overall Score', linewidth=3, markersize=8)
        axes[0, 0].set_xlabel('Iteration')
        axes[0, 0].set_ylabel('Score')
        axes[0, 0].set_title('Score Progression Across Iterations')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Improvement rates
        if len(iterations) > 1:
            whale_improvements = [whale_scores[i] - whale_scores[i-1] for i in range(1, len(whale_scores))]
            grinder_improvements = [grinder_scores[i] - grinder_scores[i-1] for i in range(1, len(grinder_scores))]
            casual_improvements = [casual_scores[i] - casual_scores[i-1] for i in range(1, len(casual_scores))]
            overall_improvements = [overall_scores[i] - overall_scores[i-1] for i in range(1, len(overall_scores))]
            
            improvement_iterations = iterations[1:]
            
            axes[0, 1].plot(improvement_iterations, whale_improvements, 'o-', label='Whale Improvement', linewidth=2)
            axes[0, 1].plot(improvement_iterations, grinder_improvements, 's-', label='Grinder Improvement', linewidth=2)
            axes[0, 1].plot(improvement_iterations, casual_improvements, '^-', label='Casual Improvement', linewidth=2)
            axes[0, 1].plot(improvement_iterations, overall_improvements, 'd-', label='Overall Improvement', linewidth=3)
            axes[0, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
            axes[0, 1].set_xlabel('Iteration')
            axes[0, 1].set_ylabel('Score Improvement')
            axes[0, 1].set_title('Score Improvement Per Iteration')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Score distribution
        all_scores = whale_scores + grinder_scores + casual_scores + overall_scores
        score_types = ['Whale'] * len(whale_scores) + ['Grinder'] * len(grinder_scores) + \
                     ['Casual'] * len(casual_scores) + ['Overall'] * len(overall_scores)
        
        score_df = pd.DataFrame({'Score': all_scores, 'Type': score_types})
        sns.boxplot(data=score_df, x='Type', y='Score', ax=axes[1, 0])
        axes[1, 0].set_title('Score Distribution by Type')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Convergence analysis
        if len(overall_scores) > 2:
            # Calculate moving average
            window_size = min(3, len(overall_scores))
            moving_avg = pd.Series(overall_scores).rolling(window=window_size).mean()
            
            axes[1, 1].plot(iterations, overall_scores, 'o-', alpha=0.5, label='Raw Scores')
            axes[1, 1].plot(iterations, moving_avg, 'r-', linewidth=3, label=f'Moving Average (window={window_size})')
            axes[1, 1].set_xlabel('Iteration')
            axes[1, 1].set_ylabel('Overall Score')
            axes[1, 1].set_title('Convergence Analysis')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.suptitle('Optimization Progress Analysis', fontsize=16)
        
        # Save plot
        filename = f"{self.output_dir}/optimization_progress.svg"
        plt.tight_layout()
        plt.savefig(filename, format='svg', dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def create_parameter_progression_plot(self, results_data: List[Dict], player_type: str) -> str:
        """Create parameter progression plot showing how parameters change across test variations"""
        if not results_data:
            return None
            
        # Extract all parameter values across tests
        param_names = []
        param_values = []
        
        # Get all unique parameter names from the first result
        if results_data:
            first_config = results_data[0].get('config', {})
            param_names = [key for key, value in first_config.items() 
                          if isinstance(value, (int, float)) and not isinstance(value, bool)]
        
        # Extract values for each parameter across all tests
        for param_name in param_names:
            values = []
            for result in results_data:
                config = result.get('config', {})
                values.append(config.get(param_name, 0))
            param_values.append(values)
        
        # Create subplots for each parameter
        n_params = len(param_names)
        n_cols = 4
        n_rows = (n_params + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))
        if n_rows == 1:
            axes = [axes] if n_cols == 1 else axes
        else:
            axes = axes.flatten()
        
        test_indices = list(range(1, len(results_data) + 1))
        
        for i, (param_name, values) in enumerate(zip(param_names, param_values)):
            if i >= len(axes):
                break
                
            ax = axes[i]
            
            # Plot parameter values
            ax.plot(test_indices, values, 'o-', linewidth=2, markersize=6, alpha=0.8)
            ax.set_xlabel('Test Configuration')
            ax.set_ylabel(param_name.replace('_', ' ').title())
            ax.set_title(f'{param_name.replace("_", " ").title()}')
            ax.grid(True, alpha=0.3)
            
            # Add value labels on points
            for j, value in enumerate(values):
                ax.annotate(f'{value:.2f}', (test_indices[j], value), 
                           textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
        
        # Remove empty subplots
        for i in range(n_params, len(axes)):
            fig.delaxes(axes[i])
        
        player_type_title = player_type.title() if player_type else "Unknown"
        plt.suptitle(f'{player_type_title} Optimization: Parameter Progression Across Test Configurations', 
                    fontsize=16, y=0.98)
        
        # Save plot
        safe_player_type = player_type if player_type else "unknown"
        filename = f"{self.output_dir}/{safe_player_type}_parameter_progression.svg"
        plt.tight_layout()
        plt.savefig(filename, format='svg', dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def create_score_progression_plot(self, results_data: List[Dict], player_type: str) -> str:
        """Create score progression plot showing how scores change across test variations"""
        if not results_data:
            return None
            
        test_indices = list(range(1, len(results_data) + 1))
        
        # Extract scores
        whale_scores = [r.get('whale_score', 0) for r in results_data]
        grinder_scores = [r.get('grinder_score', 0) for r in results_data]
        casual_scores = [r.get('casual_score', 0) for r in results_data]
        overall_scores = [r.get('overall_score', 0) for r in results_data]
        revenues = [r.get('revenue', 0) for r in results_data]
        userbases = [r.get('userbase', 0) for r in results_data]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # Plot 1: All scores
        axes[0].plot(test_indices, whale_scores, 'o-', label='Whale Score', linewidth=2, markersize=6)
        axes[0].plot(test_indices, grinder_scores, 's-', label='Grinder Score', linewidth=2, markersize=6)
        axes[0].plot(test_indices, casual_scores, '^-', label='Casual Score', linewidth=2, markersize=6)
        axes[0].plot(test_indices, overall_scores, 'd-', label='Overall Score', linewidth=3, markersize=8)
        axes[0].set_xlabel('Test Configuration')
        axes[0].set_ylabel('Score')
        axes[0].set_title('All Scores Progression')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Revenue progression
        axes[1].plot(test_indices, revenues, 'o-', color='green', linewidth=2, markersize=6)
        axes[1].set_xlabel('Test Configuration')
        axes[1].set_ylabel('Revenue ($)')
        axes[1].set_title('Revenue Progression')
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Userbase progression
        axes[2].plot(test_indices, userbases, 'o-', color='blue', linewidth=2, markersize=6)
        axes[2].set_xlabel('Test Configuration')
        axes[2].set_ylabel('Userbase')
        axes[2].set_title('Userbase Progression')
        axes[2].grid(True, alpha=0.3)
        
        # Plot 4: Score vs Revenue scatter
        scatter = axes[3].scatter(overall_scores, revenues, c=test_indices, cmap='viridis', 
                                s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
        axes[3].set_xlabel('Overall Score')
        axes[3].set_ylabel('Revenue ($)')
        axes[3].set_title('Score vs Revenue (colored by test order)')
        cbar = plt.colorbar(scatter, ax=axes[3])
        cbar.set_label('Test Configuration')
        axes[3].grid(True, alpha=0.3)
        
        # Plot 5: Score vs Userbase scatter
        scatter2 = axes[4].scatter(overall_scores, userbases, c=test_indices, cmap='plasma', 
                                 s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
        axes[4].set_xlabel('Overall Score')
        axes[4].set_ylabel('Userbase')
        axes[4].set_title('Score vs Userbase (colored by test order)')
        cbar2 = plt.colorbar(scatter2, ax=axes[4])
        cbar2.set_label('Test Configuration')
        axes[4].grid(True, alpha=0.3)
        
        # Plot 6: Best performing configuration
        best_idx = overall_scores.index(max(overall_scores))
        best_config = results_data[best_idx].get('config', {})
        
        # Show key parameters of best configuration
        key_params = ['owner_base_points', 'pack_price_dollars', 'geo_diversity_bonus', 
                     'social_sneeze_bonus', 'churn_probability_whale']
        param_values = [best_config.get(param, 0) for param in key_params]
        param_labels = [param.replace('_', ' ').title() for param in key_params]
        
        bars = axes[5].bar(range(len(param_values)), param_values, alpha=0.7)
        axes[5].set_xticks(range(len(param_labels)))
        axes[5].set_xticklabels(param_labels, rotation=45, ha='right')
        axes[5].set_title(f'Best Configuration (Test #{best_idx + 1})')
        axes[5].grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, param_values):
            height = bar.get_height()
            axes[5].text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:.2f}', ha='center', va='bottom', fontsize=8)
        
        player_type_title = player_type.title() if player_type else "Unknown"
        plt.suptitle(f'{player_type_title} Optimization: Score and Performance Progression', 
                    fontsize=16, y=0.98)
        
        # Save plot
        safe_player_type = player_type if player_type else "unknown"
        filename = f"{self.output_dir}/{safe_player_type}_score_progression.svg"
        plt.tight_layout()
        plt.savefig(filename, format='svg', dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename

    def create_comprehensive_dashboard(self, all_results: Dict[str, Any]) -> str:
        """Create a comprehensive dashboard with all key visualizations"""
        fig = plt.figure(figsize=(24, 16))
        
        # Create a grid layout
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # Extract data for each player type
        player_types = ['whale', 'grinder', 'casual']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        for i, player_type in enumerate(player_types):
            if f'{player_type}_result' in all_results:
                result = all_results[f'{player_type}_result']
                config = result.get('config', {})
                summary = result.get('summary', {})
                
                # Plot 1: Key metrics bar chart
                ax1 = fig.add_subplot(gs[i, 0])
                metrics = ['Revenue', 'Userbase', 'Stickers Placed']
                values = [
                    result.get('revenue', 0),
                    result.get('userbase', 0),
                    summary.get(f'{player_type}_purchases', 0)
                ]
                bars = ax1.bar(metrics, values, color=colors[i], alpha=0.7)
                ax1.set_title(f'{player_type.title()} Key Metrics')
                ax1.tick_params(axis='x', rotation=45)
                
                # Add value labels on bars
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{value:.0f}', ha='center', va='bottom')
                
                # Plot 2: Parameter radar chart (simplified as bar chart)
                ax2 = fig.add_subplot(gs[i, 1])
                key_params = ['owner_base_points', 'pack_price_dollars', 'geo_diversity_bonus', 
                             'social_sneeze_bonus', 'churn_probability_whale']
                param_values = [config.get(param, 0) for param in key_params]
                param_labels = [param.replace('_', ' ').title() for param in key_params]
                
                bars = ax2.bar(range(len(param_values)), param_values, color=colors[i], alpha=0.7)
                ax2.set_xticks(range(len(param_labels)))
                ax2.set_xticklabels(param_labels, rotation=45, ha='right')
                ax2.set_title(f'{player_type.title()} Key Parameters')
                
                # Plot 3: Score breakdown
                ax3 = fig.add_subplot(gs[i, 2])
                scores = [result.get('target_score', 0), result.get('overall_score', 0)]
                score_labels = ['Target Score', 'Overall Score']
                bars = ax3.bar(score_labels, scores, color=colors[i], alpha=0.7)
                ax3.set_title(f'{player_type.title()} Scores')
                
                # Add value labels
                for bar, value in zip(bars, scores):
                    height = bar.get_height()
                    ax3.text(bar.get_x() + bar.get_width()/2., height,
                            f'{value:.1f}', ha='center', va='bottom')
        
        # Multi-player summary
        if 'multiplayer_result' in all_results:
            mp_result = all_results['multiplayer_result']
            
            # Plot 4: Multi-player comparison
            ax4 = fig.add_subplot(gs[3, :2])
            player_scores = [
                mp_result.get('whale_score', 0),
                mp_result.get('grinder_score', 0),
                mp_result.get('casual_score', 0)
            ]
            player_labels = ['Whale', 'Grinder', 'Casual']
            
            bars = ax4.bar(player_labels, player_scores, color=colors, alpha=0.7)
            ax4.set_title('Multi-Player Score Comparison')
            ax4.set_ylabel('Score')
            
            # Add value labels
            for bar, value in zip(bars, player_scores):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:.1f}', ha='center', va='bottom')
            
            # Plot 5: Multi-player metrics
            ax5 = fig.add_subplot(gs[3, 2:])
            mp_metrics = ['Revenue', 'Userbase', 'Overall Score']
            mp_values = [
                mp_result.get('revenue', 0),
                mp_result.get('userbase', 0),
                mp_result.get('overall_score', 0)
            ]
            
            bars = ax5.bar(mp_metrics, mp_values, color='#9B59B6', alpha=0.7)
            ax5.set_title('Multi-Player Final Metrics')
            
            # Add value labels
            for bar, value in zip(bars, mp_values):
                height = bar.get_height()
                ax5.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:.1f}', ha='center', va='bottom')
        
        plt.suptitle('FYNDR Economy Optimization - Comprehensive Dashboard', fontsize=20, y=0.98)
        
        # Save plot
        filename = f"{self.output_dir}/comprehensive_dashboard.svg"
        plt.tight_layout()
        plt.savefig(filename, format='svg', dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def generate_all_visualizations(self, results_data: Dict[str, Any], 
                                  iteration_data: List[Dict] = None) -> Dict[str, str]:
        """Generate all visualizations and return file paths"""
        generated_files = {}
        
        print("Generating visualizations...")
        
        # Create comprehensive dashboard
        dashboard_file = self.create_comprehensive_dashboard(results_data)
        generated_files['dashboard'] = dashboard_file
        print(f"✓ Created comprehensive dashboard: {dashboard_file}")
        
        # Create player-specific progression visualizations
        all_simulation_results = results_data.get('all_simulation_results', [])
        
        if all_simulation_results:
            # Group results by player type focus
            player_results = {}
            for result in all_simulation_results:
                player_focus = result.get('player_type_focus', 'unknown')
                if player_focus not in player_results:
                    player_results[player_focus] = []
                player_results[player_focus].append(result)
            
            # Create progression plots for each player type
            for player_type, results in player_results.items():
                if len(results) > 1:  # Need multiple results to show progression
                    # Parameter progression plot
                    param_prog_file = self.create_parameter_progression_plot(results, player_type)
                    if param_prog_file:
                        generated_files[f'{player_type}_parameter_progression'] = param_prog_file
                        print(f"✓ Created {player_type} parameter progression: {param_prog_file}")
                    
                    # Score progression plot
                    score_prog_file = self.create_score_progression_plot(results, player_type)
                    if score_prog_file:
                        generated_files[f'{player_type}_score_progression'] = score_prog_file
                        print(f"✓ Created {player_type} score progression: {score_prog_file}")
        
        # Create multi-player analysis
        if 'multiplayer_result' in results_data:
            print("✓ Generated multi-player analysis")
        
        # Create optimization progress plot if iteration data is available
        if iteration_data:
            progress_file = self.create_optimization_progress_plot(iteration_data)
            generated_files['progress'] = progress_file
            print(f"✓ Created optimization progress plot: {progress_file}")
        
        return generated_files
