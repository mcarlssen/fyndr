#!/usr/bin/env python3
"""
Grinder player behavior module.
Grinders focus on economy wins via streaks, bonuses, and strategic point reinvestment.
"""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fyndr_life_simulator import Player, FYNDRLifeSimulator

def simulate_grinder_behavior(simulator: 'FYNDRLifeSimulator', player: 'Player'):
    """
    Simulate grinder player behavior - focused on economy wins via streaks and bonuses.
    
    Grinder behavior logic:
    1. Occasional wallet top-ups (1/4 whale rate)
    2. Strategic sticker pack purchases (money and points)
    3. Focus on SCANNING for streaks and bonuses (high priority)
    4. Reinvest points on level up (100% reinvestment)
    5. Lower sticker placement priority
    """
    
    # 1. WALLET TOP-UP LOGIC (occasional, 1/4 whale rate)
    if random.random() < simulator.config.grinder_purchase_probability:
        spend_amount = random.uniform(
            simulator.config.grinder_purchase_min,
            simulator.config.grinder_purchase_max
        )
        player.wallet_balance += spend_amount
        player.total_spent += spend_amount
        simulator.total_revenue += spend_amount
        
        # Log wallet top-up
        simulator._log_event(
            "grinder_wallet_topup",
            f"Grinder {player.id} topped up wallet with ${spend_amount:.2f}",
            affected_players=1,
            additional_data={
                "player_id": player.id,
                "topup_amount": spend_amount,
                "new_wallet_balance": player.wallet_balance
            }
        )
    
    # 2. STICKER PACK PURCHASES (money-based)
    if player.wallet_balance >= simulator.config.pack_price_dollars:
        grinder_purchase_prob = simulator._calculate_price_adjusted_probability(
            simulator.config.grinder_purchase_probability, "grinder"
        )
        
        if random.random() < grinder_purchase_prob:
            if simulator._purchase_sticker_pack_with_money(player):
                # Log sticker pack purchase
                simulator._log_event(
                    "grinder_sticker_purchase",
                    f"Grinder {player.id} purchased sticker pack for ${simulator.config.pack_price_dollars}",
                    affected_players=1,
                    additional_data={
                        "player_id": player.id,
                        "pack_price": simulator.config.pack_price_dollars,
                        "remaining_wallet": player.wallet_balance
                    }
                )
    
    # 3. POINT-BASED PURCHASES (grinder reinvestment logic)
    if simulator.config.grinder_reinvest_on_levelup and player.total_points >= simulator.config.pack_price_points:
        # Check if player leveled up recently (within last 3 days)
        if (hasattr(player, 'last_level_up_day') and 
            player.last_level_up_day is not None and 
            (simulator.current_day - player.last_level_up_day) <= 3):
            
            # Reinvest all points into sticker packs
            packs_to_buy = int(player.total_points // simulator.config.pack_price_points)
            if packs_to_buy > 0:
                for _ in range(packs_to_buy):
                    if simulator._purchase_sticker_pack_with_points(player):
                        # Log reinvestment purchase
                        simulator._log_event(
                            "grinder_reinvestment",
                            f"Grinder {player.id} reinvested points into sticker pack",
                            affected_players=1,
                            additional_data={
                                "player_id": player.id,
                                "points_spent": simulator.config.pack_price_points,
                                "remaining_points": player.total_points
                            }
                        )
        else:
            # Regular point-based purchasing (less frequent)
            grinder_point_prob = simulator._calculate_price_adjusted_probability(
                simulator.config.grinder_purchase_probability, "grinder"
            )
            if random.random() < grinder_point_prob:
                if simulator._purchase_sticker_pack_with_points(player):
                    # Log point purchase
                    simulator._log_event(
                        "grinder_point_purchase",
                        f"Grinder {player.id} purchased sticker pack with points",
                        affected_players=1,
                        additional_data={
                            "player_id": player.id,
                            "points_spent": simulator.config.pack_price_points,
                            "remaining_points": player.total_points
                        }
                    )
    
    # 4. SCANNING BEHAVIOR (high priority for streaks and bonuses)
    # Grinders attempt to scan each available sticker with grinder_scan_percentage probability
    simulator._simulate_scan_behavior_per_sticker(player, simulator.config.grinder_scan_percentage)
    player.scanned_today = True
    
    # 5. STICKER PLACEMENT (low priority)
    if player.stickers_owned > 0 and random.random() < 0.2:  # 20% chance to place sticker
        if simulator._create_new_sticker(player):
            player.placed_today = True
            # Log sticker placement
            simulator._log_event(
                "grinder_sticker_placement",
                f"Grinder {player.id} placed a sticker (remaining: {player.stickers_owned})",
                affected_players=1,
                additional_data={
                    "player_id": player.id,
                    "remaining_stickers": player.stickers_owned
                }
            )
