#!/usr/bin/env python3
"""
Casual player behavior module.
Casual players do a little of everything with balanced activity.
"""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fyndr_life_simulator import Player, FYNDRLifeSimulator

def simulate_casual_behavior(simulator: 'FYNDRLifeSimulator', player: 'Player'):
    """
    Simulate casual player behavior - balanced activity across all mechanics.
    
    Casual behavior logic:
    1. Occasional wallet top-ups
    2. Multiple purchase options (wallet, direct, points)
    3. Balanced scanning and sticker placement
    4. Direct purchases more likely for casuals
    """
    
    # 1. WALLET TOP-UP LOGIC (occasional)
    if random.random() < simulator.config.casual_purchase_probability:
        spend_amount = random.uniform(
            simulator.config.casual_purchase_min,
            simulator.config.casual_purchase_max
        )
        player.wallet_balance += spend_amount
        player.total_spent += spend_amount
        simulator.total_revenue += spend_amount
        
        # Log wallet top-up
        simulator._log_event(
            "casual_wallet_topup",
            f"Casual {player.id} topped up wallet with ${spend_amount:.2f}",
            affected_players=1,
            additional_data={
                "player_id": player.id,
                "topup_amount": spend_amount,
                "new_wallet_balance": player.wallet_balance
            }
        )
    
    # 2. STICKER PACK PURCHASES (wallet-based)
    if player.wallet_balance >= simulator.config.pack_price_dollars:
        casual_purchase_prob = simulator._calculate_price_adjusted_probability(
            simulator.config.casual_purchase_probability, "casual"
        )
        
        if random.random() < casual_purchase_prob:
            if simulator._purchase_sticker_pack_with_money(player):
                # Log sticker pack purchase
                simulator._log_event(
                    "casual_sticker_purchase",
                    f"Casual {player.id} purchased sticker pack for ${simulator.config.pack_price_dollars}",
                    affected_players=1,
                    additional_data={
                        "player_id": player.id,
                        "pack_price": simulator.config.pack_price_dollars,
                        "remaining_wallet": player.wallet_balance
                    }
                )
    
    # 3. DIRECT PURCHASES (casuals prefer direct purchases)
    casual_purchase_prob = simulator._calculate_price_adjusted_probability(
        simulator.config.casual_purchase_probability, "casual"
    )
    direct_purchase_prob = casual_purchase_prob * 2  # 2x more likely for direct purchase
    
    if random.random() < direct_purchase_prob:
        # Direct purchase - no wallet required
        player.total_spent += simulator.config.pack_price_dollars
        simulator.total_revenue += simulator.config.pack_price_dollars
        
        # Add stickers to inventory
        stickers_per_pack = 6
        player.stickers_owned += stickers_per_pack
        player.sticker_packs_purchased += 1
        player.total_stickers_purchased += stickers_per_pack
        
        # Log direct purchase
        simulator._log_event(
            "casual_direct_purchase",
            f"Casual {player.id} made direct purchase for ${simulator.config.pack_price_dollars}",
            affected_players=1,
            additional_data={
                "player_id": player.id,
                "pack_price": simulator.config.pack_price_dollars,
                "stickers_added": stickers_per_pack
            }
        )
    
    # 4. POINT-BASED PURCHASES (occasional)
    if player.total_points >= simulator.config.pack_price_points:
        if random.random() < casual_purchase_prob:
            if simulator._purchase_sticker_pack_with_points(player):
                # Log point purchase
                simulator._log_event(
                    "casual_point_purchase",
                    f"Casual {player.id} purchased sticker pack with points",
                    affected_players=1,
                    additional_data={
                        "player_id": player.id,
                        "points_spent": simulator.config.pack_price_points,
                        "remaining_points": player.total_points
                    }
                )
    
    # 5. BALANCED ACTIVITY (scanning and placement)
    # Sticker placement (moderate priority)
    if player.stickers_owned > 0 and random.random() < 0.5:  # 50% chance to place sticker
        if simulator._create_new_sticker(player):
            player.placed_today = True
            # Log sticker placement
            simulator._log_event(
                "casual_sticker_placement",
                f"Casual {player.id} placed a sticker (remaining: {player.stickers_owned})",
                affected_players=1,
                additional_data={
                    "player_id": player.id,
                    "remaining_stickers": player.stickers_owned
                }
            )
    
    # Scanning (moderate priority)
    # Casuals attempt to scan each available sticker with casual_scan_percentage probability
    simulator._simulate_scan_behavior_per_sticker(player, simulator.config.casual_scan_percentage)
    player.scanned_today = True
