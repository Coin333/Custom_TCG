#!/usr/bin/env python3
"""
Automated Game Simulation for Terminal Chaos TCG
Tests a complete run-through of the game without interactive input
"""
import sys
sys.path.insert(0, '.')
import random
from card import load_cards_from_json, Card
from engine import GameEngine, Player
from ability_engine import ability_engine
from status import create_status


def simulate_game():
    """Run a complete automated game simulation."""
    print("=" * 60)
    print("Terminal Chaos TCG - Automated Game Test")
    print("=" * 60)
    
    # Load all cards including transform-only for transformation lookups
    all_cards = load_cards_from_json("cards.json", include_transform_only=True)
    print(f"\nLoaded {len(all_cards)} cards")
    
    # Filter out transform-only cards for deck building
    available_cards = [c for c in all_cards if not c.transform_only]
    
    # Build decks for both players
    print("\nBuilding decks...")
    
    # Player 1 deck: Random selection
    p1_deck = random.sample(available_cards, min(10, len(available_cards)))
    p1_deck = [c.copy() for c in p1_deck]
    
    # Player 2 deck: Random selection from remaining
    remaining = [c for c in available_cards if c.name not in [d.name for d in p1_deck]]
    if len(remaining) < 10:
        remaining = available_cards  # Reuse if needed
    p2_deck = random.sample(remaining, min(10, len(remaining)))
    p2_deck = [c.copy() for c in p2_deck]
    
    print(f"Player 1 deck: {[c.name for c in p1_deck]}")
    print(f"Player 2 deck: {[c.name for c in p2_deck]}")
    
    # Set up players
    # Active = first card, Bench = next 2, Pool = rest
    p1 = Player(
        name="Player 1",
        active=p1_deck[0],
        bench=p1_deck[1:3],
        deck_pool=p1_deck[3:]
    )
    
    p2 = Player(
        name="Player 2",
        active=p2_deck[0],
        bench=p2_deck[1:3],
        deck_pool=p2_deck[3:]
    )
    
    # Initialize game engine
    engine = GameEngine(p1, p2)
    
    print("\n" + "=" * 60)
    print("GAME START!")
    print("=" * 60)
    
    max_turns = 50  # Prevent infinite loops
    turn = 0
    
    # Helper function to trigger passives when a card enters play
    def trigger_card_passives(card, opp_active=None):
        """Trigger battle_start passives for a card."""
        if card.passive:
            result = ability_engine.trigger_passive(
                card, card.passive.effect_id, "battle_start", {}
            )
            if result and result.message:
                print(f"  {result.message}")
        if card.secondary_passive:
            result = ability_engine.trigger_passive(
                card, card.secondary_passive.effect_id, "battle_start", {}
            )
            if result and result.message:
                print(f"  {result.message}")
    
    # Trigger initial passives
    if engine.player1.active:
        trigger_card_passives(engine.player1.active, engine.player2.active)
    if engine.player2.active:
        trigger_card_passives(engine.player2.active, engine.player1.active)
    
    while not engine.game_over and turn < max_turns:
        turn += 1
        current = engine.current_player
        opponent = engine.opponent
        
        print(f"\n--- Turn {turn}: {current.name}'s turn ---")
        
        if not current.active:
            print(f"{current.name} has no active card! Checking bench...")
            if current.bench:
                current.active = current.bench.pop(0)
                print(f"  Promoted {current.active.name} to active")
                trigger_card_passives(current.active, opponent.active)
            else:
                print(f"  {current.name} has no more cards!")
                engine.game_over = True
                engine.winner = opponent
                break
        
        if not opponent.active:
            print(f"{opponent.name} has no active card! Checking bench...")
            if opponent.bench:
                opponent.active = opponent.bench.pop(0)
                print(f"  Promoted {opponent.active.name} to active")
                trigger_card_passives(opponent.active, current.active)
            else:
                print(f"  {opponent.name} has no more cards!")
                engine.game_over = True
                engine.winner = current
                break
        
        attacker = current.active
        defender = opponent.active
        
        print(f"  {attacker.name} (HP: {attacker.current_hp}/{attacker.max_hp}) vs {defender.name} (HP: {defender.current_hp}/{defender.max_hp})")
        
        # Tick status effects BEFORE checking skip (so skip effects expire)
        expired = attacker.status_manager.tick_all()
        for exp in expired:
            print(f"  Status expired: {exp.name}")
        
        # Check for skip turn effects
        should_skip, skip_reason = attacker.status_manager.should_skip_turn()
        if should_skip:
            print(f"  {attacker.name} skips turn due to {skip_reason}!")
        else:
            # Trigger turn_start passives
            if attacker.passive:
                result = ability_engine.trigger_passive(
                    attacker, attacker.passive.effect_id, "turn_start", {}
                )
                if result and result.message:
                    print(f"  {result.message}")
            if attacker.secondary_passive:
                result = ability_engine.trigger_passive(
                    attacker, attacker.secondary_passive.effect_id, "turn_start", {}
                )
                if result and result.message:
                    print(f"  {result.message}")
            
            # Calculate self-damage from DoT
            self_damage = attacker.status_manager.calculate_self_damage(attacker.max_hp)
            if self_damage > 0:
                attacker.take_damage(self_damage)
                print(f"  {attacker.name} takes {self_damage} DoT damage (HP: {attacker.current_hp})")
            
            # Check if died from DoT
            if not attacker.is_alive():
                print(f"  {attacker.name} died from DoT!")
                points = attacker.get_point_value()
                opponent.score += points
                print(f"  {opponent.name} scores {points} points! (Total: {opponent.score})")
                current.active = None
            else:
                # 50% chance to use ability if available
                if attacker.can_use_ability() and random.random() < 0.5:
                    print(f"  {attacker.name} uses {attacker.ability.name}!")
                    
                    game_state = {
                        "user_bench": current.bench,
                        "opponent_bench": opponent.bench,
                        "opponent_active": defender
                    }
                    
                    result = ability_engine.execute_ability(
                        attacker, defender, attacker.ability.effect_id,
                        game_state=game_state
                    )
                    
                    attacker.ability_used = True
                    print(f"    {result.message}")
                    
                    # Check for transformation
                    if result.transform_to:
                        print(f"    TRANSFORMATION to {result.transform_to}!")
                        # Find the transform target card
                        for c in all_cards:
                            if c.name == result.transform_to:
                                new_card = c.copy()
                                new_card.current_hp = min(attacker.current_hp, new_card.max_hp)
                                current.active = new_card
                                attacker = new_card
                                break
                    
                    # Check for kills
                    if result.kill_self:
                        attacker.take_damage(attacker.current_hp)
                        print(f"    {attacker.name} is destroyed!")
                    if result.kill_target:
                        defender.take_damage(defender.current_hp)
                        print(f"    {defender.name} is destroyed!")
                
                # Attack if still alive
                if attacker.is_alive() and defender.is_alive():
                    # Check dodge
                    dodge_chance = defender.status_manager.get_dodge_chance()
                    auto_dodged = defender.status_manager.check_auto_dodge()
                    
                    if auto_dodged:
                        print(f"  {defender.name} auto-dodged!")
                    elif dodge_chance > 0 and random.random() * 100 < dodge_chance:
                        print(f"  {defender.name} dodged! ({dodge_chance:.0f}% chance)")
                    else:
                        # Check miss chance
                        miss_chance = attacker.status_manager.get_miss_chance()
                        if miss_chance > 0 and random.random() * 100 < miss_chance:
                            print(f"  {attacker.name} missed! ({miss_chance:.0f}% chance)")
                        else:
                            # Check reflection
                            if defender.status_manager.check_reflection():
                                print(f"  ATTACK REFLECTED!")
                                defender = attacker
                            
                            # SPECIAL: Chinese Beaver - 5 coin flips x 1000 damage
                            if attacker.name == "Chinese Beaver":
                                flips = [random.choice(["heads", "tails"]) for _ in range(5)]
                                heads = sum(1 for f in flips if f == "heads")
                                flip_str = " ".join(["H" if f == "heads" else "T" for f in flips])
                                damage = heads * 1000
                                print(f"  {attacker.name}: TAKE THAT WOOD! [{flip_str}] {heads} heads = {damage} damage!")
                                if damage > 0:
                                    actual_damage = defender.take_damage(damage)
                                    print(f"    {defender.name} HP: {defender.current_hp}/{defender.max_hp}")
                            else:
                                # Calculate damage
                                base_damage = attacker.get_attack_damage(defender.max_hp)
                            
                                # Get next attack buffs
                                buffs = attacker.status_manager.get_next_attack_buffs()
                                damage = base_damage + buffs["flat_damage"]
                                if buffs["flat_damage"] > 0:
                                    print(f"  +{buffs['flat_damage']} bonus damage from buffs!")
                                if buffs["damage_mult"] > 100:
                                    print(f"  {buffs['damage_mult']/100}x damage multiplier!")
                                damage = int(damage * (buffs["damage_mult"] / 100))
                                
                                # Check critical
                                crit_mods = attacker.status_manager.get_crit_modifiers()
                                crit_chance = attacker.attack.crit_chance + crit_mods[0]
                                
                                # Aldo's guaranteed crit when above 1000 HP
                                if attacker.name == "Aldo Ortiz" and attacker.current_hp > 1000:
                                    crit_chance = 100
                                    print(f"  {attacker.name}'s HP > 1000: GUARANTEED CRITICAL!")
                                
                                is_crit = random.random() * 100 < crit_chance
                                
                                if is_crit:
                                    crit_mult = attacker.attack.crit_multiplier / 100
                                    damage = int(damage * crit_mult)
                                    print(f"  CRITICAL HIT! ({crit_mult:.0f}x damage)")
                                
                                # Apply damage reduction
                                dr = defender.status_manager.get_damage_reduction()
                                if dr > 0:
                                    damage = int(damage * (1 - dr / 100))
                                    print(f"  Damage reduced by {dr:.0f}%")
                                
                                # Deal damage
                                actual_damage = defender.take_damage(damage)
                                print(f"  {attacker.name} deals {actual_damage} damage to {defender.name}!")
                                print(f"    {defender.name} HP: {defender.current_hp}/{defender.max_hp}")
                
                # Check for KOs
                if defender and not defender.is_alive():
                    points = defender.get_point_value()
                    current.score += points
                    print(f"  {defender.name} is KO'd! {current.name} scores {points} points! (Total: {current.score})")
                    opponent.active = None
        
        # Check win condition
        if current.score >= engine.WIN_SCORE:
            engine.game_over = True
            engine.winner = current
            print(f"\n{current.name} reaches {engine.WIN_SCORE} points!")
        elif opponent.score >= engine.WIN_SCORE:
            engine.game_over = True
            engine.winner = opponent
            print(f"\n{opponent.name} reaches {engine.WIN_SCORE} points!")
        
        # Check for no cards remaining
        if not current.has_cards_remaining():
            engine.game_over = True
            engine.winner = opponent
            print(f"\n{current.name} has no more cards!")
        elif not opponent.has_cards_remaining():
            engine.game_over = True
            engine.winner = current
            print(f"\n{opponent.name} has no more cards!")
        
        # Swap turns
        engine.current_player, engine.opponent = engine.opponent, engine.current_player
        engine.turn_number += 1
    
    print("\n" + "=" * 60)
    print("GAME OVER!")
    print("=" * 60)
    
    if engine.winner:
        print(f"\nWINNER: {engine.winner.name}!")
    else:
        print("\nGame ended in a draw or timeout.")
    
    print(f"\nFinal Scores:")
    print(f"  {p1.name}: {p1.score} points")
    print(f"  {p2.name}: {p2.score} points")
    print(f"  Total turns: {turn}")
    
    return True


if __name__ == "__main__":
    try:
        result = simulate_game()
        if result:
            print("\n" + "=" * 60)
            print("AUTOMATED TEST PASSED!")
            print("=" * 60)
            sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
