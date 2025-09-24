#!/usr/bin/env python3
"""
FYNDR Simulator Interactive Interface

Easy-to-use interface for running simulations and analyzing results.
"""

import sys
import os
from fyndr_simulator import FYNDRSimulator, GameConfig
from config_manager import ConfigManager

def print_banner():
    print("=" * 60)
    print("           FYNDR GAME ECONOMY SIMULATOR")
    print("=" * 60)
    print("A comprehensive tool for testing and refining game economy")
    print("Models player behavior, economic mechanics, and scenarios")
    print("=" * 60)
    print()

def print_menu():
    print("MAIN MENU")
    print("1. Run Default Simulation")
    print("2. Run Scenario Comparison")
    print("3. Create Custom Scenario")
    print("4. Analyze Results")
    print("5. View Available Scenarios")
    print("6. Exit")
    print()

def run_default_simulation():
    print("Running default 30-day simulation...")
    config = GameConfig()
    simulator = FYNDRSimulator(config)
    simulator.run_simulation(30)
    
    summary = simulator.get_economy_summary()
    print("\nSIMULATION RESULTS:")
    print(f"Total Revenue: ${summary['total_revenue']:.2f}")
    print(f"Total Points: {summary['total_points']:,}")
    print(f"Total Scans: {summary['total_scans']:,}")
    print(f"Total Players: {summary['total_players']}")
    print(f"Total Stickers: {summary['total_stickers']}")
    
    print("\nPlayer Distribution:")
    for player_type, count in summary['player_types'].items():
        print(f"  {player_type.title()}: {count}")
    
    print("\nRevenue by Player Type:")
    for player_type, revenue in summary['revenue_by_type'].items():
        print(f"  {player_type.title()}: ${revenue:.2f}")
    
    # Export data
    simulator.export_data("default_simulation")
    print("\nData exported to CSV files.")
    return simulator

def run_scenario_comparison():
    manager = ConfigManager()
    print("Available scenarios:")
    scenarios = manager.list_scenarios()
    for i, scenario_name in enumerate(scenarios, 1):
        scenario = manager.get_scenario(scenario_name)
        print(f"{i}. {scenario.name}")
    
    print("\nEnter scenario numbers to compare (e.g., 1,2,3):")
    try:
        choices = input().split(',')
        scenario_names = [scenarios[int(choice.strip()) - 1] for choice in choices]
        
        print(f"\nComparing scenarios: {', '.join(scenario_names)}")
        results = manager.compare_scenarios(scenario_names)
        
        print("\nCOMPARISON RESULTS:")
        print("-" * 50)
        for scenario_name, data in results.items():
            summary = data['summary']
            print(f"\n{scenario_name.upper()}:")
            print(f"  Revenue: ${summary['total_revenue']:.2f}")
            print(f"  Points: {summary['total_points']:,}")
            print(f"  Avg Revenue/Player: ${summary['avg_revenue_per_player']:.2f}")
            print(f"  Points/Scan: {summary['points_per_scan']:.2f}")
        
    except (ValueError, IndexError):
        print("Invalid selection. Please try again.")

def create_custom_scenario():
    manager = ConfigManager()
    print("Create Custom Scenario")
    print("-" * 25)
    
    name = input("Scenario name: ")
    description = input("Description: ")
    
    print("\nGame Configuration (press Enter for defaults):")
    config_dict = {}
    
    # Get key parameters
    pack_price = input("Pack price in dollars (default 3.0): ")
    if pack_price:
        config_dict['pack_price_dollars'] = float(pack_price)
    
    owner_points = input("Owner base points (default 2.0): ")
    if owner_points:
        config_dict['owner_base_points'] = float(owner_points)
    
    scanner_points = input("Scanner base points (default 1.0): ")
    if scanner_points:
        config_dict['scanner_base_points'] = float(scanner_points)
    
    print("\nInitial Player Distribution:")
    whales = int(input("Number of whales (default 10): ") or "10")
    grinders = int(input("Number of grinders (default 50): ") or "50")
    casuals = int(input("Number of casuals (default 100): ") or "100")
    
    initial_players = {'whale': whales, 'grinder': grinders, 'casual': casuals}
    
    days = int(input("Simulation days (default 30): ") or "30")
    
    scenario_id = manager.create_custom_scenario(
        name, description, config_dict, initial_players, days
    )
    
    print(f"\nCustom scenario '{scenario_id}' created successfully!")
    
    # Ask if they want to run it
    run_now = input("Run this scenario now? (y/n): ").lower() == 'y'
    if run_now:
        simulator = manager.run_scenario(scenario_id)
        summary = simulator.get_economy_summary()
        print(f"\nResults: ${summary['total_revenue']:.2f} revenue, {summary['total_points']:,} points")

def analyze_results():
    print("Analyze Results")
    print("-" * 15)
    print("This feature requires CSV files from a previous simulation.")
    print("Make sure you have run a simulation first.")
    
    # Check for CSV files
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found. Please run a simulation first.")
        return
    
    print(f"Found CSV files: {', '.join(csv_files)}")
    print("Analysis feature coming soon...")

def view_scenarios():
    manager = ConfigManager()
    print("Available Scenarios:")
    print("-" * 20)
    
    for scenario_name in manager.list_scenarios():
        scenario = manager.get_scenario(scenario_name)
        print(f"\n{scenario.name}")
        print(f"  ID: {scenario_name}")
        print(f"  Description: {scenario.description}")
        print(f"  Days: {scenario.simulation_days}")
        print(f"  Players: {scenario.initial_players}")
        print(f"  Tags: {', '.join(scenario.tags)}")

def main():
    print_banner()
    
    while True:
        print_menu()
        choice = input("Select an option (1-6): ").strip()
        
        if choice == '1':
            run_default_simulation()
        elif choice == '2':
            run_scenario_comparison()
        elif choice == '3':
            create_custom_scenario()
        elif choice == '4':
            analyze_results()
        elif choice == '5':
            view_scenarios()
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")
        print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main()
