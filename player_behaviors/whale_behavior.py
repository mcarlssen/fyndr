#!/usr/bin/env python3
"""
Whale player behavior module.
Whales focus on sticker ownership and placement, with strategic wallet management.
"""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fyndr_life_simulator import Player, FYNDRLifeSimulator

def simulate_whale_behavior(simulator: 'FYNDRLifeSimulator', player: 'Player'):
    """
    Simulate whale player behavior - focused on sticker ownership and strategic spending.
    
    Whale economic flow: Empty wallet → Top-up ($6-60) → Buy stickers (100%) → Place stickers (80%) → Repeat
    
    Whale behavior logic:
    1. Wallet top-ups ONLY when wallet is empty (using top-up probability)
    2. When wallet has balance, purchase stickers immediately (100% probability)
    3. Place stickers as quickly as possible (80% daily probability)
    4. When wallet is empty, small chance to buy stickers directly (no wallet top-up)
    5. Direct purchases are placed immediately
    """
    
    # 1. WALLET TOP-UP LOGIC (only when wallet is empty)
    if player.wallet_balance <= 0:
        # Check for wallet top-up
        if random.random() < simulator.config.whale_purchase_probability:
            spend_amount = random.uniform(
                simulator.config.wallet_topup_min,
                simulator.config.wallet_topup_max
            )
            player.wallet_balance += spend_amount
            player.total_spent += spend_amount
            simulator.total_revenue += spend_amount
            # Log wallet top-up
            simulator._log_event(
                "whale_wallet_topup",
                f"Whale {player.id} topped up wallet with ${spend_amount:.2f}",
                affected_players=1,
                additional_data={
                    "player_id": player.id,
                    "topup_amount": spend_amount,
                    "new_wallet_balance": player.wallet_balance
                }
            )
    
    # 2. STICKER PACK PURCHASES (when wallet has balance)
    # Whales buy stickers immediately when they have wallet funds (100% probability)
    if player.wallet_balance >= simulator.config.pack_price_dollars:
        if simulator._purchase_sticker_pack_with_money(player):
            # Log sticker pack purchase
            simulator._log_event(
                "whale_sticker_purchase",
                f"Whale {player.id} purchased sticker pack for ${simulator.config.pack_price_dollars}",
                affected_players=1,
                additional_data={
                    "player_id": player.id,
                    "pack_price": simulator.config.pack_price_dollars,
                    "remaining_wallet": player.wallet_balance
                }
            )
    
    # 3. DIRECT PURCHASE (when wallet is empty, small chance)
    if player.wallet_balance <= 0:
        # Much smaller probability for direct purchase (1/4 of top-up probability)
        direct_purchase_prob = simulator.config.whale_purchase_probability * 0.25
        
        if random.random() < direct_purchase_prob:
            # Direct purchase - no wallet top-up
            player.total_spent += simulator.config.pack_price_dollars
            simulator.total_revenue += simulator.config.pack_price_dollars
            
            # Add stickers to inventory
            stickers_per_pack = 6
            player.stickers_owned += stickers_per_pack
            player.sticker_packs_purchased += 1
            player.total_stickers_purchased += stickers_per_pack
            
            # Log direct purchase
            simulator._log_event(
                "whale_direct_purchase",
                f"Whale {player.id} made direct purchase for ${simulator.config.pack_price_dollars}",
                affected_players=1,
                additional_data={
                    "player_id": player.id,
                    "pack_price": simulator.config.pack_price_dollars,
                    "stickers_added": stickers_per_pack
                }
            )
    
    # 4. STICKER PLACEMENT LOGIC
    # Whales place stickers as quickly as possible (high probability)
    if player.stickers_owned > 0:
        # High probability to place stickers - whales want to place them ASAP
        placement_probability = 0.8  # 80% chance per day to place a sticker
        
        if random.random() < placement_probability:
            if simulator._create_new_sticker(player):
                player.placed_today = True
                # Log sticker placement
                simulator._log_event(
                    "whale_sticker_placement",
                    f"Whale {player.id} placed a sticker (remaining: {player.stickers_owned})",
                    affected_players=1,
                    additional_data={
                        "player_id": player.id,
                        "remaining_stickers": player.stickers_owned
                    }
                )
    
    # 5. SCANNING BEHAVIOR (low priority for whales)
    if random.random() < simulator.config.whale_scan_percentage:  # 30% chance to scan
        simulator._simulate_scan_behavior(player)
        player.scanned_today = True
