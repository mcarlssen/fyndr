#!/usr/bin/env python3
"""
Analyze the impact of disabling realistic density on player activity
"""

import json
import sys
import os

def load_simulation_data(filename):
    """Load simulation data from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def analyze_density_impact(data):
    """Analyze the impact of disabling realistic density"""
    
    print("=== DENSITY IMPACT ANALYSIS ===")
    print()
    
    # Get final day data
    final_day = data['daily_stats'][-1]
    
    print(f"Final day: {final_day['day']}")
    print(f"Active players: {final_day['active_players']}")
    print(f"Total stickers: {final_day['total_stickers_placed']}")
    print(f"Total scans: {final_day['total_scans']}")
    print(f"Total revenue: ${final_day['total_revenue']:.2f}")
    print()
    
    # Analyze sticker distribution
    player_locations = []
    sticker_locations = []
    stickers_by_owner = {}
    
    # Get player locations
    for player_id, player_data in data['players'].items():
        if player_data.get('is_active', False):
            location = player_data.get('location', (0, 0))
            player_type = player_data.get('player_type', 'unknown')
            player_locations.append((location, player_type, player_id))
    
    # Get sticker locations and owners
    for sticker_id, sticker_data in data['stickers'].items():
        if sticker_data.get('is_active', True):
            location = sticker_data.get('location', (0, 0))
            owner_id = sticker_data.get('owner_id')
            sticker_locations.append((location, owner_id))
            
            if owner_id not in stickers_by_owner:
                stickers_by_owner[owner_id] = []
            stickers_by_owner[owner_id].append(sticker_id)
    
    print("=== STICKER DISTRIBUTION ANALYSIS ===")
    print(f"Total active stickers: {len(sticker_locations)}")
    print(f"Active players: {len(player_locations)}")
    print(f"Stickers per player: {len(sticker_locations) / len(player_locations):.1f}")
    print()
    
    # Analyze sticker ownership
    print("=== STICKER OWNERSHIP ===")
    for owner_id, stickers in stickers_by_owner.items():
        print(f"Player {owner_id}: {len(stickers)} stickers")
    print()
    
    # Calculate cross-player interaction potential
    print("=== CROSS-PLAYER INTERACTION ANALYSIS ===")
    total_cross_player_stickers = 0
    for player_id, player_type, _ in player_locations:
        player_stickers = len(stickers_by_owner.get(player_id, []))
        other_stickers = len(sticker_locations) - player_stickers
        total_cross_player_stickers += other_stickers
        print(f"Player {player_id} ({player_type}): {player_stickers} own stickers, {other_stickers} other players' stickers")
    
    avg_cross_player_stickers = total_cross_player_stickers / len(player_locations) if player_locations else 0
    print(f"\nAverage other players' stickers per player: {avg_cross_player_stickers:.1f}")
    print()
    
    # Analyze scanning activity
    print("=== SCANNING ACTIVITY ANALYSIS ===")
    scans_per_player = final_day['total_scans'] / final_day['active_players'] if final_day['active_players'] > 0 else 0
    print(f"Scans per player: {scans_per_player:.1f}")
    print(f"Scans per sticker: {final_day['total_scans'] / len(sticker_locations):.1f}" if sticker_locations else "N/A")
    print()
    
    # Compare to previous simulation (if available)
    print("=== COMPARISON TO PREVIOUS SIMULATION ===")
    print("Previous simulation (with density limits):")
    print("- 8 active players")
    print("- 159 active stickers") 
    print("- 1.8 stickers per player (within 300m)")
    print("- 895 total scans")
    print()
    print("Current simulation (density limits disabled):")
    print(f"- {final_day['active_players']} active players")
    print(f"- {len(sticker_locations)} active stickers")
    print(f"- {len(sticker_locations) / final_day['active_players']:.1f} stickers per player")
    print(f"- {final_day['total_scans']} total scans")
    print()
    
    # Calculate improvement
    if final_day['active_players'] > 0:
        stickers_per_player_current = len(sticker_locations) / final_day['active_players']
        stickers_per_player_previous = 159 / 8  # 19.9
        
        print("=== IMPACT ANALYSIS ===")
        print(f"Stickers per player: {stickers_per_player_current:.1f} (current) vs {stickers_per_player_previous:.1f} (previous)")
        print(f"Change: {((stickers_per_player_current - stickers_per_player_previous) / stickers_per_player_previous * 100):+.1f}%")
        print()
        
        scans_per_player_current = final_day['total_scans'] / final_day['active_players']
        scans_per_player_previous = 895 / 8  # 111.9
        
        print(f"Scans per player: {scans_per_player_current:.1f} (current) vs {scans_per_player_previous:.1f} (previous)")
        print(f"Change: {((scans_per_player_current - scans_per_player_previous) / scans_per_player_previous * 100):+.1f}%")

def main():
    """Main analysis function"""
    
    simulation_file = "../fyndr_life_sim_20250928_184910.json"
    
    if not os.path.exists(simulation_file):
        print(f"Simulation file not found: {simulation_file}")
        return
    
    print("Loading simulation data...")
    data = load_simulation_data(simulation_file)
    
    # Analyze density impact
    analyze_density_impact(data)

if __name__ == "__main__":
    main()
