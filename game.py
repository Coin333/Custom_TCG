import main_menu
import random
import json
import pygame
import os
import card_list
from copy import deepcopy

# Status effect tracking
class StatusEffect:
    def __init__(self, effect_type, turns, value, stat=None):
        self.type = effect_type  # "poison", "defense", "miss_chance", "stat_buff", "skip_turn"
        self.turns = turns  # -1 for infinite
        self.value = value
        self.stat = stat  # For stat_buff: "damage", "hp", "dodge", etc.
    
    def tick(self):
        """Reduce turns by 1, return True if still active"""
        if self.turns > 0:
            self.turns -= 1
        return self.turns != 0 or self.turns == -1

def activate_ability(attacker, defender, ability, game_state=None):
    """
    Activate a card's ability.
    
    Ability format (dict):
    {
        "type": "critical" | "turn_skip" | "poison" | "defense" | "miss_chance" | 
                "stat_buff" | "self_hit" | "convert" | "heal",
        "name": "Ability Name",
        "chance": 0.25,  # activation chance (0.0 to 1.0)
        "multiplier": 2.0,  # for critical damage
        "turns": 3,  # for poison/turn_skip (use -1 for infinite)
        "amount": 100,  # for heal/poison damage
        "stat": "damage",  # for stat_buff: "damage", "hp", "dodge", "damage_reduction", "doublehit"
        "value": 0.1,  # for stat_buff/defense (percentage or flat)
        "target": "self" | "opponent" | "bench"  # for stat_buff
    }
    
    Legacy format (list) is also supported for backwards compatibility:
    [name, "ability", chance, multiplier]
    """
    # Handle legacy format
    if isinstance(ability, list):
        if len(ability) < 4:
            return None
        ability = {
            "type": "critical",
            "name": ability[0],
            "chance": ability[2],
            "multiplier": ability[3]
        }
    
    if not isinstance(ability, dict) or "type" not in ability:
        return None
    
    # Check activation chance
    chance = ability.get("chance", 1.0)
    if random.random() > chance:
        return None
    
    ability_name = ability.get("name", "Unknown Ability")
    ability_type = ability.get("type")
    
    result = {"type": ability_type, "name": ability_name}
    
    if ability_type == "critical":
        # Critical hit: damage multiplier
        multiplier = ability.get("multiplier", 2.0)
        base_damage = attacker.damage
        if isinstance(base_damage, list):
            base_damage = random.randint(base_damage[0], base_damage[1])
        elif base_damage == 0:
            base_damage = defender.hp * 0.1
        damage = base_damage * multiplier
        actual_dmg = card_list.DealDamage(attacker, defender, damage)
        result["damage"] = actual_dmg
        print(f"  {ability_name} activated! Critical hit for {actual_dmg:.1f} damage!")
        
    elif ability_type == "turn_skip":
        # Skip opponent's next turn
        turns = ability.get("turns", 1)
        if not hasattr(defender, "status_effects"):
            defender.status_effects = []
        defender.status_effects.append(StatusEffect("skip_turn", turns, 0))
        result["turns"] = turns
        print(f"  {ability_name} activated! {defender.name} will skip {turns} turn(s)!")
        
    elif ability_type == "poison":
        # Poison: damage each turn
        turns = ability.get("turns", 3)
        amount = ability.get("amount", 50)
        # If amount is 0, calculate as percentage of HP
        if amount == 0:
            percentage = ability.get("percentage", 0.10)
            amount = defender.hp * percentage
        if not hasattr(defender, "status_effects"):
            defender.status_effects = []
        defender.status_effects.append(StatusEffect("poison", turns, amount))
        result["turns"] = turns
        result["amount"] = amount
        print(f"  {ability_name} activated! {defender.name} is poisoned for {turns} turns ({amount:.1f} damage/turn)!")
        
    elif ability_type == "defense":
        # Increase damage reduction
        value = ability.get("value", 0.1)
        target = ability.get("target", "self")
        target_card = attacker if target == "self" else defender
        if not hasattr(target_card, "status_effects"):
            target_card.status_effects = []
        turns = ability.get("turns", -1)  # Default infinite
        target_card.status_effects.append(StatusEffect("defense", turns, value))
        target_card.damage_reduction = min(1.0, target_card.damage_reduction + value)
        result["value"] = value
        result["target"] = target
        print(f"  {ability_name} activated! {target_card.name} gains {value*100:.0f}% damage reduction!")
        
    elif ability_type == "miss_chance":
        # Increase opponent's miss chance
        value = ability.get("value", 0.1)
        turns = ability.get("turns", 1)
        if not hasattr(defender, "status_effects"):
            defender.status_effects = []
        defender.status_effects.append(StatusEffect("miss_chance", turns, value))
        defender.dodge = min(1.0, defender.dodge + value)
        result["value"] = value
        result["turns"] = turns
        print(f"  {ability_name} activated! {defender.name} has {value*100:.0f}% increased miss chance for {turns} turn(s)!")
        
    elif ability_type == "stat_buff":
        # Buff stats
        stat = ability.get("stat", "damage")
        value = ability.get("value", 0.1)
        target = ability.get("target", "self")
        turns = ability.get("turns", -1)
        target_card = attacker if target == "self" else defender
        
        if not hasattr(target_card, "status_effects"):
            target_card.status_effects = []
        target_card.status_effects.append(StatusEffect("stat_buff", turns, value, stat))
        
        # Apply buff
        if stat == "damage":
            target_card.damage = int(target_card.damage * (1 + value)) if isinstance(target_card.damage, (int, float)) else target_card.damage
        elif stat == "hp":
            target_card.hp += target_card.hp * value
        elif stat == "dodge":
            target_card.dodge = min(1.0, target_card.dodge + value)
        elif stat == "damage_reduction":
            target_card.damage_reduction = min(1.0, target_card.damage_reduction + value)
        elif stat == "doublehit":
            target_card.doublehit = min(1.0, target_card.doublehit + value)
        
        result["stat"] = stat
        result["value"] = value
        result["target"] = target
        print(f"  {ability_name} activated! {target_card.name} gains {value*100:.0f}% {stat} buff!")
        
    elif ability_type == "self_hit":
        # Chance for opponent's next attack to hit themselves
        chance = ability.get("value", 0.5)
        turns = ability.get("turns", 1)
        if not hasattr(defender, "status_effects"):
            defender.status_effects = []
        defender.status_effects.append(StatusEffect("self_hit", turns, chance))
        result["chance"] = chance
        result["turns"] = turns
        print(f"  {ability_name} activated! {defender.name} has {chance*100:.0f}% chance to hit themselves for {turns} turn(s)!")
        
    elif ability_type == "convert":
        # Convert opponent's card to your side
        chance = ability.get("chance", 0.33)
        if random.random() < chance:
            result["converted"] = True
            print(f"  {ability_name} activated! {defender.name} has been converted!")
            return result  # Special case - card conversion
        else:
            print(f"  {ability_name} failed to convert {defender.name}.")
            
    elif ability_type == "heal":
        # Heal
        amount = ability.get("amount", 100)
        target = ability.get("target", "self")
        target_card = attacker if target == "self" else defender
        heal_amount = min(amount, target_card.hp * 0.5) if isinstance(amount, str) and "%" in amount else amount
        if isinstance(heal_amount, str) and "%" in heal_amount:
            heal_amount = target_card.hp * (float(heal_amount.replace("%", "")) / 100)
        target_card.hp += heal_amount
        result["amount"] = heal_amount
        result["target"] = target
        print(f"  {ability_name} activated! {target_card.name} healed {heal_amount:.1f} HP!")
    
    elif ability_type == "block":
        # Block/negate next attack
        attacks = ability.get("attacks", 1)
        if not hasattr(attacker, "status_effects"):
            attacker.status_effects = []
        attacker.status_effects.append(StatusEffect("block", attacks, 0))
        result["attacks"] = attacks
        print(f"  {ability_name} activated! {attacker.name} will block the next {attacks} attack(s)!")
        
    elif ability_type == "mutual_destruction":
        # Both cards die
        attacker.hp = 0
        defender.hp = 0
        result["mutual"] = True
        print(f"  {ability_name} activated! Both cards are destroyed!")
        
    elif ability_type == "dodge_buff":
        # Auto-dodge next X attacks
        attacks = ability.get("attacks", 1)
        if not hasattr(attacker, "status_effects"):
            attacker.status_effects = []
        attacker.status_effects.append(StatusEffect("dodge_buff", attacks, 0))
        result["attacks"] = attacks
        print(f"  {ability_name} activated! {attacker.name} will auto-dodge the next {attacks} attack(s)!")
        
    elif ability_type == "conditional_critical":
        # Critical with conditions
        multiplier = ability.get("multiplier", 2.0)
        condition = ability.get("condition", {})  # {"trait": "short", "value": True}
        
        # Check condition
        condition_met = True
        if condition:
            trait = condition.get("trait")
            value = condition.get("value")
            if trait == "short" and defender.short != value:
                condition_met = False
            elif trait == "tall" and defender.tall != value:
                condition_met = False
            elif trait == "male" and defender.male != value:
                condition_met = False
            elif trait == "female" and defender.female != value:
                condition_met = False
        
        if condition_met:
            base_damage = attacker.damage
            if isinstance(base_damage, list):
                base_damage = random.randint(base_damage[0], base_damage[1])
            elif base_damage == 0:
                base_damage = defender.hp * 0.1
            damage = base_damage * multiplier
            actual_dmg = card_list.DealDamage(attacker, defender, damage)
            result["damage"] = actual_dmg
            print(f"  {ability_name} activated! Conditional critical hit for {actual_dmg:.1f} damage!")
        else:
            # Fallback multiplier if condition not met
            fallback = ability.get("fallback_multiplier", 1.25)
            base_damage = attacker.damage
            if isinstance(base_damage, list):
                base_damage = random.randint(base_damage[0], base_damage[1])
            damage = base_damage * fallback
            actual_dmg = card_list.DealDamage(attacker, defender, damage)
            result["damage"] = actual_dmg
            print(f"  {ability_name} activated! (Condition not met) Dealt {actual_dmg:.1f} damage!")
            
    elif ability_type == "damage_boost":
        # Flat damage boost
        boost = ability.get("boost", 0)
        turns = ability.get("turns", -1)
        if not hasattr(attacker, "status_effects"):
            attacker.status_effects = []
        attacker.status_effects.append(StatusEffect("damage_boost", turns, boost))
        if isinstance(attacker.damage, (int, float)):
            attacker.damage += boost
        result["boost"] = boost
        print(f"  {ability_name} activated! {attacker.name} gains +{boost} damage!")
        
    elif ability_type == "percentage_damage":
        # Deal % of HP as damage
        percentage = ability.get("percentage", 0.1)
        damage = defender.hp * percentage
        actual_dmg = card_list.DealDamage(attacker, defender, damage)
        result["damage"] = actual_dmg
        print(f"  {ability_name} activated! Dealt {percentage*100:.0f}% of {defender.name}'s HP ({actual_dmg:.1f} damage)!")
        
    elif ability_type == "flat_damage":
        # Deal flat damage amount
        damage = ability.get("damage", 100)
        actual_dmg = card_list.DealDamage(attacker, defender, damage)
        result["damage"] = actual_dmg
        print(f"  {ability_name} activated! Dealt {actual_dmg:.1f} damage!")
        
    elif ability_type == "full_heal":
        # Heal to full HP (and optionally add defense)
        max_hp = ability.get("max_hp", attacker.hp)
        target = ability.get("target", "self")
        target_card = attacker if target == "self" else defender
        target_card.hp = max_hp
        
        # Optional defense boost
        defense_boost = ability.get("defense_boost", 0)
        if defense_boost > 0:
            defense_turns = ability.get("defense_turns", 1)
            if not hasattr(target_card, "status_effects"):
                target_card.status_effects = []
            target_card.status_effects.append(StatusEffect("defense", defense_turns, defense_boost))
            target_card.damage_reduction = min(1.0, target_card.damage_reduction + defense_boost)
            print(f"  {ability_name} activated! {target_card.name} healed to full HP ({max_hp:.1f}) and gains {defense_boost*100:.0f}% damage reduction!")
        else:
            print(f"  {ability_name} activated! {target_card.name} healed to full HP ({max_hp:.1f})!")
        
        result["target"] = target
        
    elif ability_type == "stat_debuff":
        # Debuff opponent stats
        stat = ability.get("stat", "damage")
        value = ability.get("value", 0.1)
        turns = ability.get("turns", 2)
        if not hasattr(defender, "status_effects"):
            defender.status_effects = []
        defender.status_effects.append(StatusEffect("stat_debuff", turns, value, stat))
        
        # Apply debuff
        if stat == "damage":
            defender.damage = max(0, int(defender.damage * (1 - value))) if isinstance(defender.damage, (int, float)) else defender.damage
        elif stat == "dodge":
            defender.dodge = max(0, defender.dodge - value)
        elif stat == "damage_reduction":
            defender.damage_reduction = max(0, defender.damage_reduction - value)
        
        result["stat"] = stat
        result["value"] = value
        result["turns"] = turns
        print(f"  {ability_name} activated! {defender.name} loses {value*100:.0f}% {stat} for {turns} turn(s)!")
    
    return result

def process_status_effects(card, card_name):
    """Process status effects on a card at the start of turn."""
    if not hasattr(card, "status_effects") or not card.status_effects:
        return False
    
    skip_turn = False
    effects_to_remove = []
    
    for effect in card.status_effects:
        if effect.type == "poison":
            # Apply poison damage
            damage = effect.value
            card.hp = max(0, card.hp - damage)
            print(f"  {card_name} takes {damage:.1f} poison damage!")
            if not effect.tick():
                effects_to_remove.append(effect)
        elif effect.type == "skip_turn":
            # Skip this turn
            skip_turn = True
            if not effect.tick():
                effects_to_remove.append(effect)
    
    # Remove expired effects
    for effect in effects_to_remove:
        card.status_effects.remove(effect)
        if effect.type == "defense":
            card.damage_reduction = max(0, card.damage_reduction - effect.value)
        elif effect.type == "miss_chance":
            card.dodge = max(0, card.dodge - effect.value)
        elif effect.type == "stat_buff":
            # Revert stat buff
            if effect.stat == "damage":
                card.damage = int(card.damage / (1 + effect.value)) if isinstance(card.damage, (int, float)) else card.damage
            elif effect.stat == "hp":
                card.hp = card.hp / (1 + effect.value)
            elif effect.stat == "dodge":
                card.dodge = max(0, card.dodge - effect.value)
            elif effect.stat == "damage_reduction":
                card.damage_reduction = max(0, card.damage_reduction - effect.value)
            elif effect.stat == "doublehit":
                card.doublehit = max(0, card.doublehit - effect.value)
        elif effect.type == "stat_debuff":
            # Revert stat debuff
            if effect.stat == "damage":
                card.damage = int(card.damage / (1 - effect.value)) if isinstance(card.damage, (int, float)) else card.damage
            elif effect.stat == "dodge":
                card.dodge = min(1.0, card.dodge + effect.value)
            elif effect.stat == "damage_reduction":
                card.damage_reduction = min(1.0, card.damage_reduction + effect.value)
        elif effect.type == "damage_boost":
            # Revert damage boost
            if isinstance(card.damage, (int, float)):
                card.damage = max(0, card.damage - effect.value)
    
    return skip_turn

def turn(c1, p1, c2, p2):
    """
    Execute a single turn of combat between two cards.
    c1: Player 1's card
    p1: Player 1's name
    c2: Player 2's card  
    p2: Player 2's name
    Returns: (c1_alive, c2_alive, converted) tuple
    """
    print(f"\n--- {p1}'s {c1.name} vs {p2}'s {c2.name} ---")
    print(f"{c1.name}: {c1.hp:.1f} HP | {c2.name}: {c2.hp:.1f} HP")
    
    # Initialize status effects if needed
    if not hasattr(c1, "status_effects"):
        c1.status_effects = []
    if not hasattr(c2, "status_effects"):
        c2.status_effects = []
    
    # Process status effects at start of turn
    c1_skip = process_status_effects(c1, c1.name)
    c2_skip = process_status_effects(c2, c2.name)
    
    converted = False
    
    # Player 1 attacks Player 2
    if c1.hp > 0 and not c1_skip:
        # Check for self_hit status
        self_hit = False
        for effect in c1.status_effects:
            if effect.type == "self_hit" and random.random() < effect.value:
                self_hit = True
                break
        
        # Check for block status on defender
        blocked = False
        for effect in c2.status_effects:
            if effect.type == "block":
                blocked = True
                effect.tick()
                if effect.turns == 0:
                    c2.status_effects.remove(effect)
                break
        
        # Check for dodge_buff on defender (c2)
        auto_dodge = False
        for effect in c2.status_effects:
            if effect.type == "dodge_buff":
                auto_dodge = True
                effect.tick()
                if effect.turns == 0:
                    c2.status_effects.remove(effect)
                break
        
        if self_hit:
            dmg1 = card_list.DealDamage(c1, c1, c1.damage)
            print(f"{p1}'s {c1.name} attacks themselves for {dmg1:.1f} damage!")
        elif blocked:
            print(f"{p1}'s {c1.name} attacks but {c2.name} blocks it!")
            dmg1 = 0
        else:
            # Check if defender has dodge_buff
            if auto_dodge:
                print(f"{p1}'s {c1.name} attacks but {c2.name} auto-dodges!")
                dmg1 = 0
            else:
                dmg1 = card_list.DealDamage(c1, c2)
                if dmg1 > 0:
                    print(f"{p1}'s {c1.name} attacks for {dmg1:.1f} damage!")
                else:
                    print(f"{p1}'s {c1.name} attacks but {c2.name} dodges!")
        
        # Activate ability
        if c1.hp > 0 and c2.hp > 0:
            ability_result = activate_ability(c1, c2, c1.abilities)
            if ability_result and ability_result.get("converted"):
                converted = True
                return (True, False, True)  # Card converted
    elif c1_skip:
        print(f"{p1}'s {c1.name} is unable to act this turn!")
    
    # Player 2 attacks Player 1
    if c2.hp > 0 and not c2_skip:
        # Check for self_hit status
        self_hit = False
        for effect in c2.status_effects:
            if effect.type == "self_hit" and random.random() < effect.value:
                self_hit = True
                break
        
        # Check for block status on defender
        blocked = False
        for effect in c1.status_effects:
            if effect.type == "block":
                blocked = True
                effect.tick()
                if effect.turns == 0:
                    c1.status_effects.remove(effect)
                break
        
        # Check for dodge_buff on attacker
        auto_dodge = False
        for effect in c2.status_effects:
            if effect.type == "dodge_buff":
                auto_dodge = True
                effect.tick()
                if effect.turns == 0:
                    c2.status_effects.remove(effect)
                break
        
        if self_hit:
            dmg2 = card_list.DealDamage(c2, c2, c2.damage)
            print(f"{p2}'s {c2.name} attacks themselves for {dmg2:.1f} damage!")
        elif blocked:
            print(f"{p2}'s {c2.name} attacks but {c1.name} blocks it!")
            dmg2 = 0
        else:
            # Check if defender has dodge_buff
            auto_dodge = False
            for effect in c1.status_effects:
                if effect.type == "dodge_buff":
                    auto_dodge = True
                    effect.tick()
                    if effect.turns == 0:
                        c1.status_effects.remove(effect)
                    break
            
            if auto_dodge:
                print(f"{p2}'s {c2.name} attacks but {c1.name} auto-dodges!")
                dmg2 = 0
            else:
                dmg2 = card_list.DealDamage(c2, c1)
                if dmg2 > 0:
                    print(f"{p2}'s {c2.name} attacks for {dmg2:.1f} damage!")
                else:
                    print(f"{p2}'s {c2.name} attacks but {c1.name} dodges!")
        
        # Activate ability
        if c1.hp > 0 and c2.hp > 0:
            ability_result = activate_ability(c2, c1, c2.abilities)
            if ability_result and ability_result.get("converted"):
                converted = True
                return (False, True, True)  # Card converted
    elif c2_skip:
        print(f"{p2}'s {c2.name} is unable to act this turn!")
    
    # Check if cards are alive
    c1_alive = c1.hp > 0
    c2_alive = c2.hp > 0
    
    if not c1_alive:
        print(f"\n{p1}'s {c1.name} has been defeated!")
    if not c2_alive:
        print(f"\n{p2}'s {c2.name} has been defeated!")
    
    if c1_alive and c2_alive:
        print(f"Status: {c1.name} ({c1.hp:.1f} HP) vs {c2.name} ({c2.hp:.1f} HP)")
    
    return (c1_alive, c2_alive, converted)

def build_deck(available_cards=None, deck_size=5):
    """Build a deck by selecting cards from available cards."""
    print("\n" + "="*50)
    print("DECK BUILDING")
    print("="*50)
    
    # Show available cards by rarity
    all_cards = {}
    all_cards.update(card_list.common_cards)
    all_cards.update(card_list.rare_cards)
    all_cards.update(card_list.epic_cards)
    all_cards.update(card_list.mythic_cards)
    all_cards.update(card_list.legendary_cards)
    all_cards.update(card_list.ult_legendary_cards)
    
    print("\nAvailable Cards:")
    print("-" * 50)
    
    # Group by rarity
    rarities = {
        "Common": card_list.common_cards,
        "Rare": card_list.rare_cards,
        "Epic": card_list.epic_cards,
        "Mythic": card_list.mythic_cards,
        "Legendary": card_list.legendary_cards,
        "Ultimate Legendary": card_list.ult_legendary_cards
    }
    
    card_list_display = []
    idx = 1
    for rarity, cards in rarities.items():
        if cards:
            print(f"\n{rarity}:")
            for name, card in cards.items():
                display_name = name.replace("_", " ")
                print(f"  {idx}. {display_name} - DMG: {card.damage}, HP: {card.hp}, DR: {card.damage_reduction*100:.0f}%")
                card_list_display.append((name, card, rarity))
                idx += 1
    
    deck = []
    print(f"\nSelect {deck_size} cards for your deck:")
    
    while len(deck) < deck_size:
        try:
            choice = input(f"Card {len(deck)+1}/{deck_size} (enter number): ").strip()
            if choice.lower() == 'random':
                # Fill remaining with random cards
                remaining = deck_size - len(deck)
                available = [c for c in card_list_display if c[0] not in [d[0] for d in deck]]
                selected = random.sample(available, min(remaining, len(available)))
                deck.extend([(name, deepcopy(card)) for name, card, _ in selected])
                print(f"Randomly selected {remaining} cards!")
                break
            elif choice.lower() == 'auto':
                # Auto-build deck
                available = [c for c in card_list_display]
                selected = random.sample(available, min(deck_size, len(available)))
                deck = [(name, deepcopy(card)) for name, card, _ in selected]
                print("Auto-built deck!")
                break
            else:
                card_idx = int(choice) - 1
                if 0 <= card_idx < len(card_list_display):
                    name, card, rarity = card_list_display[card_idx]
                    if (name, card) not in deck:
                        deck.append((name, deepcopy(card)))
                        print(f"Added {name.replace('_', ' ')} to deck!")
                    else:
                        print("Card already in deck!")
                else:
                    print("Invalid selection!")
        except (ValueError, IndexError):
            print("Invalid input! Enter a number, 'random', or 'auto'")
    
    print("\nYour deck:")
    for i, (name, card) in enumerate(deck, 1):
        print(f"{i}. {name.replace('_', ' ')} - DMG: {card.damage}, HP: {card.hp}")
    
    return deck

def game():
    """Main game loop."""
    print("\n" + "="*50)
    print("CUSTOM TCG - GAME START")
    print("="*50)
    
    # Get player names
    p1_name = input("\nPlayer 1 name (or press Enter for 'Player 1'): ").strip() or "Player 1"
    p2_name = input("Player 2 name (or press Enter for 'Player 2'): ").strip() or "Player 2"
    
    # Quick play option
    quick_play = input("\nQuick play? (auto-build decks) [y/N]: ").strip().lower()
    
    if quick_play == 'y':
        # Auto-build decks
        print("\nAuto-building decks...")
        all_cards_list = []
        all_cards_list.extend([(k, v) for k, v in card_list.common_cards.items()])
        all_cards_list.extend([(k, v) for k, v in card_list.rare_cards.items()])
        all_cards_list.extend([(k, v) for k, v in card_list.epic_cards.items()])
        all_cards_list.extend([(k, v) for k, v in card_list.mythic_cards.items()])
        all_cards_list.extend([(k, v) for k, v in card_list.legendary_cards.items()])
        all_cards_list.extend([(k, v) for k, v in card_list.ult_legendary_cards.items()])
        
        p1_selected = random.sample(all_cards_list, min(5, len(all_cards_list)))
        p2_selected = random.sample(all_cards_list, min(5, len(all_cards_list)))
        
        p1_deck = [(name, deepcopy(card)) for name, card in p1_selected]
        p2_deck = [(name, deepcopy(card)) for name, card in p2_selected]
        
        print(f"\n{p1_name}'s deck:")
        for name, card in p1_deck:
            print(f"  - {name.replace('_', ' ')} (DMG: {card.damage}, HP: {card.hp})")
        print(f"\n{p2_name}'s deck:")
        for name, card in p2_deck:
            print(f"  - {name.replace('_', ' ')} (DMG: {card.damage}, HP: {card.hp})")
    else:
        # Build decks manually
        print(f"\n{p1_name}, build your deck:")
        p1_deck = build_deck(None)  # None means use all available cards
        
        print(f"\n{p2_name}, build your deck:")
        p2_deck = build_deck(None)  # None means use all available cards
    
    # Shuffle decks
    random.shuffle(p1_deck)
    random.shuffle(p2_deck)
    
    # Game loop
    turn_num = 1
    p1_wins = 0
    p2_wins = 0
    
    print("\n" + "="*50)
    print("BATTLE BEGINS!")
    print("="*50)
    
    while p1_deck and p2_deck:
        print(f"\n{'='*50}")
        print(f"TURN {turn_num}")
        print(f"{'='*50}")
        
        # Draw cards
        c1_name, c1 = p1_deck.pop(0)
        c2_name, c2 = p2_deck.pop(0)
        
        # Create copies for battle (so original stats aren't modified)
        c1_battle = deepcopy(c1)
        c2_battle = deepcopy(c2)
        
        print(f"\n{p1_name} draws: {c1_name.replace('_', ' ')}")
        print(f"{p2_name} draws: {c2_name.replace('_', ' ')}")
        
        # Battle until one card is defeated
        round_num = 1
        while c1_battle.hp > 0 and c2_battle.hp > 0:
            print(f"\n--- Round {round_num} ---")
            c1_alive, c2_alive, converted = turn(c1_battle, p1_name, c2_battle, p2_name)
            
            if converted:
                # Card was converted - special handling
                if not c2_alive:  # c2 was converted to p1
                    print(f"\n{c2_battle.name} has been converted to {p1_name}'s side!")
                    p1_wins += 1
                elif not c1_alive:  # c1 was converted to p2
                    print(f"\n{c1_battle.name} has been converted to {p2_name}'s side!")
                    p2_wins += 1
                break
            
            if not c1_alive or not c2_alive:
                break
            
            round_num += 1
            if round_num > 20:  # Prevent infinite loops
                print("\nBattle reached 20 rounds - it's a draw!")
                break
        
        # Determine winner of this turn
        if c1_battle.hp > 0 and c2_battle.hp <= 0:
            print(f"\n{p1_name} wins this turn!")
            p1_wins += 1
        elif c2_battle.hp > 0 and c1_battle.hp <= 0:
            print(f"\n{p2_name} wins this turn!")
            p2_wins += 1
        else:
            print("\nThis turn is a draw!")
        
        turn_num += 1
        
        # Check if someone ran out of cards
        if not p1_deck or not p2_deck:
            break
        
        input("\nPress Enter to continue to next turn...")
    
    # Final results
    print("\n" + "="*50)
    print("GAME OVER")
    print("="*50)
    print(f"\n{p1_name} wins: {p1_wins}")
    print(f"{p2_name} wins: {p2_wins}")
    
    if p1_wins > p2_wins:
        print(f"\n🎉 {p1_name} WINS THE GAME! 🎉")
    elif p2_wins > p1_wins:
        print(f"\n🎉 {p2_name} WINS THE GAME! 🎉")
    else:
        print("\n🤝 IT'S A TIE! 🤝")
    
    input("\nPress Enter to return to main menu...")
