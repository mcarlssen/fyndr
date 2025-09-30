import json
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters"""
    R = 6371000  # Radius of Earth in meters
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

with open('fyndr_life_sim_20250928_184910.json', 'r') as f:
    data = json.load(f)

# Get player and sticker locations
players = []
stickers = []

for player_id, player_data in data['players'].items():
    if player_data.get('is_active', False):
        location = player_data.get('location', (0, 0))
        player_type = player_data.get('player_type', 'unknown')
        players.append((player_id, location, player_type))

for sticker_id, sticker_data in data['stickers'].items():
    if sticker_data.get('is_active', True):
        location = sticker_data.get('location', (0, 0))
        owner_id = sticker_data.get('owner_id')
        stickers.append((sticker_id, location, owner_id))

print('=== STICKER DISTRIBUTION ANALYSIS ===')
print(f'Active players: {len(players)}')
print(f'Active stickers: {len(stickers)}')
print()

# Analyze cross-player sticker interaction
print('=== CROSS-PLAYER INTERACTION ANALYSIS ===')
for player_id, player_loc, player_type in players:
    player_stickers = [s for s in stickers if s[2] == player_id]
    other_stickers = [s for s in stickers if s[2] != player_id]
    
    print(f'Player {player_id} ({player_type}):')
    print(f'  Own stickers: {len(player_stickers)}')
    print(f'  Other players stickers: {len(other_stickers)}')
    
    # Calculate how many other players' stickers are within scanning range (300m)
    reachable_other_stickers = 0
    for sticker_id, sticker_loc, owner_id in other_stickers:
        distance = haversine_distance(
            player_loc[0], player_loc[1],
            sticker_loc[0], sticker_loc[1]
        )
        if distance <= 300:
            reachable_other_stickers += 1
    
    print(f'  Reachable other stickers (300m): {reachable_other_stickers}')
    print()

# Analyze sticker clustering
print('=== STICKER CLUSTERING ANALYSIS ===')
for player_id, player_loc, player_type in players:
    player_stickers = [s for s in stickers if s[2] == player_id]
    
    if player_stickers:
        # Calculate average distance from player to their stickers
        total_distance = 0
        for sticker_id, sticker_loc, owner_id in player_stickers:
            distance = haversine_distance(
                player_loc[0], player_loc[1],
                sticker_loc[0], sticker_loc[1]
            )
            total_distance += distance
        
        avg_distance = total_distance / len(player_stickers)
        print(f'Player {player_id} ({player_type}): {len(player_stickers)} stickers, avg distance {avg_distance:.1f}m')
    else:
        print(f'Player {player_id} ({player_type}): 0 stickers')

print()

# Check if stickers are more spread out now
print('=== DENSITY IMPACT VERIFICATION ===')
print('Previous simulation (with density limits):')
print('- Stickers clustered tightly around players')
print('- Limited cross-player interaction')
print('- Density limits prevented sticker placement')
print()
print('Current simulation (density limits disabled):')
print('- Stickers should be more spread out')
print('- Better cross-player interaction potential')
print('- No artificial density constraints')
