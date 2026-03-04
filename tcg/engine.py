"""
Game Engine for Terminal Chaos TCG
Core game loop, combat resolution, and game state management
"""
from dataclasses import dataclass, field
from typing import Optional
from card import Card
from status import StatusManager, EffectType
from ability_engine import ability_engine, AbilityResult
from utils import (
    roll, coin, random_choice, apply_cap,
    print_header, print_subheader, print_divider, print_error, print_success, print_warning,
    colorize, Colors, clear_screen, format_hp, get_numeric_input,
    RARITY_POINTS
)


@dataclass
class Player:
    """
    Represents a player in the game.
    
    Attributes:
        name: Player's display name
        deck_pool: Remaining cards not in play
        active: Current active card
        bench: Bench cards (max 2)
        score: Current point score
    """
    name: str
    deck_pool: list[Card] = field(default_factory=list)
    active: Optional[Card] = None
    bench: list[Card] = field(default_factory=list)
    score: int = 0
    
    def has_cards_remaining(self) -> bool:
        """Check if player has any cards left to play."""
        return self.active is not None or len(self.bench) > 0 or len(self.deck_pool) > 0
    
    def can_replace_active(self) -> bool:
        """Check if active can be replaced when KO'd."""
        return len(self.bench) > 0
    
    def replace_active(self, bench_index: int) -> tuple[bool, str]:
        """
        Replace active card with a bench card.
        
        Args:
            bench_index: Index of bench card to promote (0-based)
            
        Returns:
            Tuple of (success, message)
        """
        if bench_index < 0 or bench_index >= len(self.bench):
            return (False, "Invalid bench index")
        
        # Promote bench card to active
        new_active = self.bench.pop(bench_index)
        self.active = new_active
        
        # Fill empty bench slot from deck pool if possible
        if self.deck_pool:
            new_bench = random_choice(self.deck_pool)
            self.deck_pool.remove(new_bench)
            self.bench.append(new_bench)
            new_bench.reset()  # Reset new card's state
            return (True, f"{new_active.name} becomes Active! {new_bench.name} joins bench.")
        
        return (True, f"{new_active.name} becomes Active!")
    
    def get_total_cards(self) -> int:
        """Get total number of cards remaining."""
        total = len(self.deck_pool) + len(self.bench)
        if self.active:
            total += 1
        return total


class GameEngine:
    """
    Main game engine handling turn structure, combat, and win conditions.
    """
    
    WIN_SCORE = 25
    
    def __init__(self, player1: Player, player2: Player, card_pool: list[Card] = None):
        """
        Initialize game engine.
        
        Args:
            player1: First player
            player2: Second player
            card_pool: Full card pool (including transform-only cards) for transformations
        """
        self.player1 = player1
        self.player2 = player2
        self.current_player: Player = player1
        self.opponent: Player = player2
        self.turn_number = 1
        self.game_over = False
        self.winner: Optional[Player] = None
        self.combat_log: list[str] = []
        self.last_turn_log: list[str] = []  # Store last turn's log for victory screen
        self.card_pool = card_pool or []  # For transformations
    
    def log(self, message: str):
        """Add a message to combat log."""
        self.combat_log.append(message)
        print(message)
    
    def clear_log(self):
        """Clear combat log for new turn."""
        self.last_turn_log = self.combat_log.copy()  # Save before clearing
        self.combat_log = []
    
    def coin_flip_starting_player(self) -> Player:
        """
        Flip coin to determine starting player.
        
        Returns:
            Starting player
        """
        clear_screen()
        print_header("Coin Flip for First Turn")
        
        print(f"\n{self.player1.name} calls the flip...")
        input("Press Enter to flip...")
        
        result = coin()
        print(f"\n{Colors.WARNING}The coin shows: {result.upper()}!{Colors.RESET}")
        
        # P1 gets heads
        if result == "heads":
            starting = self.player1
        else:
            starting = self.player2
        
        self.current_player = starting
        self.opponent = self.player2 if starting == self.player1 else self.player1
        
        print_success(f"\n{starting.name} goes first!")
        input("Press Enter to continue...")
        
        return starting
    
    def display_game_state(self):
        """Display current game state."""
        clear_screen()
        print_header(f"Turn {self.turn_number} - {self.current_player.name}'s Turn")
        
        # Scores
        print(f"\n{Colors.INFO}Scores:{Colors.RESET}")
        print(f"  {self.player1.name}: {self.player1.score} / {self.WIN_SCORE}")
        print(f"  {self.player2.name}: {self.player2.score} / {self.WIN_SCORE}")
        
        # Opponent's side
        print_divider("-")
        print(f"{Colors.ERROR}OPPONENT: {self.opponent.name}{Colors.RESET}")
        if self.opponent.active:
            self._display_card(self.opponent.active, is_opponent=True)
        else:
            print("  [No Active Card]")
        
        print(f"\n  Bench: ", end="")
        if self.opponent.bench:
            print(", ".join(f"{c.get_colored_name()} ({c.current_hp} HP)" for c in self.opponent.bench))
        else:
            print("[Empty]")
        print(f"  Deck Pool: {len(self.opponent.deck_pool)} cards")
        
        # Divider
        print_divider("=")
        
        # Your side
        print(f"\n{Colors.SUCCESS}YOU: {self.current_player.name}{Colors.RESET}")
        if self.current_player.active:
            self._display_card(self.current_player.active, is_opponent=False)
        else:
            print("  [No Active Card]")
        
        print(f"\n  Bench:")
        for i, card in enumerate(self.current_player.bench, 1):
            print(f"    {i}. {card.get_colored_name()} | HP: {card.current_hp}/{card.max_hp} | ATK: {card.attack.base_damage}")
        if not self.current_player.bench:
            print("    [Empty]")
        print(f"  Deck Pool: {len(self.current_player.deck_pool)} cards")
        
        print_divider("-")
    
    def _display_card(self, card: Card, is_opponent: bool = False):
        """Display a card's details."""
        prefix = "  "
        
        print(f"{prefix}{card.get_colored_name()} ({card.rarity})")
        print(f"{prefix}HP: {format_hp(card.current_hp, card.max_hp)}")
        
        # Attack info
        atk_str = f"{prefix}ATK: {card.attack.base_damage}"
        if card.attack.percent_damage > 0:
            atk_str += f" + {card.attack.percent_damage}% Max HP"
        print(atk_str)
        
        # Status effects
        statuses = card.status_manager.get_display_list()
        if statuses:
            status_strs = []
            for s in statuses:
                if s.duration > 0:
                    status_strs.append(f"{s.name}({s.duration})")
                else:
                    status_strs.append(s.name)
            print(f"{prefix}Status: {', '.join(status_strs)}")
        else:
            print(f"{prefix}Status: None")
        
        # Ability (only show details for own card)
        if not is_opponent:
            ability_status = ""
            if card.ability.is_passive:
                ability_status = f"{Colors.INFO}[PASSIVE]{Colors.RESET}"
            elif card.ability_used:
                ability_status = f"{Colors.ERROR}[USED]{Colors.RESET}"
            else:
                ability_status = f"{Colors.SUCCESS}[AVAILABLE]{Colors.RESET}"
            print(f"{prefix}Ability: {card.ability.name} {ability_status}")
            print(f"{prefix}  -> {card.ability.description}")
    
    def resolve_start_of_turn(self) -> bool:
        """
        Resolve start of turn effects.
        
        Returns:
            True if turn should continue, False if turn is skipped
        """
        card = self.current_player.active
        if not card:
            return False
        
        print_subheader("Start of Turn")
        
        # Check for turn skip effects
        should_skip, skip_reason = card.status_manager.should_skip_turn()
        if should_skip:
            self.log(f"{Colors.WARNING}{card.name} is affected by {skip_reason}! Turn skipped!{Colors.RESET}")
            return False
        
        # Resolve self-damage (DoT)
        self_damage = card.status_manager.calculate_self_damage(card.max_hp)
        if self_damage > 0:
            card.take_damage(self_damage)
            self.log(f"{Colors.ERROR}{card.name} takes {self_damage} damage from status effects!{Colors.RESET}")
            
            # Check if died to DoT
            if not card.is_alive():
                self.log(f"{Colors.ERROR}{card.name} was KO'd by damage over time!{Colors.RESET}")
                return False
        
        # Resolve healing over time
        healing, can_overflow = card.status_manager.calculate_heal(card.max_hp, card.current_hp)
        if healing > 0:
            if can_overflow:
                old_hp = card.current_hp
                card.current_hp += healing
                if card.current_hp > card.max_hp:
                    card.max_hp = card.current_hp
                actual_heal = card.current_hp - old_hp
            else:
                actual_heal = card.heal(healing)
            if actual_heal > 0:
                self.log(f"{Colors.SUCCESS}{card.name} heals {actual_heal} HP from regeneration!{Colors.RESET}")
        
        # Apply passive effects from ability (if ability is passive)
        if card.ability.is_passive:
            result = ability_engine.apply_passive(
                card, self.opponent.active,
                card.ability.effect_id,
                card.ability.parameters,
                trigger="start_turn"
            )
            if result and result.success and result.message:
                self.log(result.message)
        
        # Apply passive effects from separate passive field
        if card.passive:
            result = ability_engine.trigger_passive(
                card, card.passive.effect_id,
                "turn_start", {}
            )
            if result and result.success and result.message:
                self.log(result.message)
        
        # Apply secondary passive
        if card.secondary_passive:
            result = ability_engine.trigger_passive(
                card, card.secondary_passive.effect_id,
                "turn_start", {}
            )
            if result and result.success and result.message:
                self.log(result.message)
        
        # Tick status durations - NOW HANDLED in end_turn() after full round
        # (Status tick moved to _tick_round_statuses)
        
        return True
    
    def player_action_phase(self) -> tuple[str, Optional[AbilityResult]]:
        """
        Handle player's action selection.
        
        Returns:
            Tuple of (action_type, ability_result)
        """
        card = self.current_player.active
        
        while True:  # Loop to allow viewing stats then returning to action
            print("\n" + "=" * 50)
            print(f"{Colors.WARNING}Choose Your Action:{Colors.RESET}")
            print("  1. Attack")
            
            if card.can_use_ability():
                print(f"  2. Use Ability: {card.ability.name}")
                print(f"     {card.ability.description}")
                print("  3. View Card Stats")
                
                choice = get_numeric_input("Your choice (1-3): ", 1, 3)
            else:
                print(f"  {Colors.ERROR}Ability not available{Colors.RESET}")
                print("  2. View Card Stats")
                
                choice = get_numeric_input("Your choice (1-2): ", 1, 2)
                if choice == 2:
                    choice = 3  # Map to view stats
            
            if choice == 3:
                # View card stats
                self._display_detailed_card_stats()
                continue  # Loop back to action selection
            elif choice == 1:
                return ("attack", None)
            else:
                # Use ability
                card.use_ability()
                result = ability_engine.execute_ability(
                    card,
                    self.opponent.active,
                    card.ability.effect_id,
                    card.ability.parameters
                )
                self.log(f"\n{Colors.INFO}>> {result.message}{Colors.RESET}")
                return ("ability", result)
    
    def _display_detailed_card_stats(self):
        """Display detailed stats for both active cards and bench cards."""
        print_divider("=")
        print(f"{Colors.INFO}=== DETAILED CARD STATS ==={Colors.RESET}")
        print_divider("=")
        
        # Your active card
        print(f"\n{Colors.SUCCESS}YOUR ACTIVE CARD:{Colors.RESET}")
        if self.current_player.active:
            self._display_full_card_stats(self.current_player.active)
        else:
            print("  [No Active Card]")
        
        # Your bench
        print(f"\n{Colors.SUCCESS}YOUR BENCH:{Colors.RESET}")
        if self.current_player.bench:
            for i, c in enumerate(self.current_player.bench, 1):
                print(f"  [{i}] {c.get_colored_name()}")
                print(f"      HP: {c.current_hp}/{c.max_hp} | ATK: {c.attack.base_damage}")
                if c.passive:
                    print(f"      Passive: {c.passive.name}")
        else:
            print("  [Empty]")
        
        # Opponent active card
        print(f"\n{Colors.ERROR}OPPONENT ACTIVE CARD:{Colors.RESET}")
        if self.opponent.active:
            self._display_full_card_stats(self.opponent.active)
        else:
            print("  [No Active Card]")
        
        # Opponent bench
        print(f"\n{Colors.ERROR}OPPONENT BENCH:{Colors.RESET}")
        if self.opponent.bench:
            for i, c in enumerate(self.opponent.bench, 1):
                print(f"  [{i}] {c.get_colored_name()}")
                print(f"      HP: {c.current_hp}/{c.max_hp} | ATK: {c.attack.base_damage}")
        else:
            print("  [Empty]")
        
        print_divider("=")
        input("Press Enter to continue...")
    
    def _display_full_card_stats(self, card: Card):
        """Display comprehensive stats for a single card."""
        print(f"  {card.get_colored_name()} ({card.rarity})")
        print(f"  HP: {format_hp(card.current_hp, card.max_hp)}")
        
        # Attack info
        atk_str = f"  ATK: {card.attack.base_damage}"
        if card.attack.percent_damage > 0:
            atk_str += f" + {card.attack.percent_damage}% Max HP"
        if card.attack.crit_chance > 0:
            atk_str += f" | Crit: {card.attack.crit_chance}% ({card.attack.crit_multiplier}%)"
        print(atk_str)
        
        # Status effects
        statuses = card.status_manager.get_display_list()
        if statuses:
            status_strs = []
            for s in statuses:
                if s.duration > 0:
                    status_strs.append(f"{s.name}({s.duration})")
                else:
                    status_strs.append(s.name)
            print(f"  Status: {', '.join(status_strs)}")
        else:
            print(f"  Status: None")
        
        # Passive abilities
        if card.passive:
            print(f"  Passive: {card.passive.name} - {card.passive.description}")
        if card.secondary_passive:
            print(f"  Secondary: {card.secondary_passive.name} - {card.secondary_passive.description}")
        
        # Active ability
        ability_status = ""
        if card.ability.is_passive:
            ability_status = f"{Colors.INFO}[PASSIVE]{Colors.RESET}"
        elif card.ability_used:
            ability_status = f"{Colors.ERROR}[USED]{Colors.RESET}"
        else:
            ability_status = f"{Colors.SUCCESS}[AVAILABLE]{Colors.RESET}"
        print(f"  Ability: {card.ability.name} {ability_status}")
        print(f"    -> {card.ability.description}")
        
        # Computed values
        dr = card.status_manager.get_damage_reduction()
        dodge = card.status_manager.get_dodge_chance()
        if dr > 0 or dodge > 0:
            print(f"  DR: {dr}% | Dodge: {dodge}%")
    
    def resolve_combat(self, action: str, ability_result: Optional[AbilityResult]):
        """
        Resolve combat based on player's action.
        
        Args:
            action: "attack" or "ability"
            ability_result: Result of ability use (if any)
        """
        attacker = self.current_player.active
        defender = self.opponent.active
        
        if not attacker or not defender:
            return
        
        # Handle ability result effects (transform, kill, etc.)
        if ability_result:
            # Handle transformation
            if ability_result.transform_to:
                self.log(f"{Colors.WARNING}TRANSFORMATION! {attacker.name} becomes {ability_result.transform_to}!{Colors.RESET}")
                for card in self.card_pool:
                    if card.name == ability_result.transform_to:
                        new_card = card.copy()
                        new_card.current_hp = min(attacker.current_hp, new_card.max_hp)
                        self.current_player.active = new_card
                        attacker = new_card
                        break
            
            # Handle kill effects
            if ability_result.kill_self:
                self.log(f"{Colors.ERROR}{attacker.name} is destroyed!{Colors.RESET}")
                attacker.take_damage(attacker.current_hp)
            if ability_result.kill_target:
                self.log(f"{Colors.ERROR}{defender.name} is destroyed!{Colors.RESET}")
                defender.take_damage(defender.current_hp)
        
        # Always attack after ability (abilities don't end turn)
        # Only skip attack if attacker or defender is dead
        if attacker.is_alive() and defender.is_alive():
            self._resolve_attack(attacker, defender)
    
    def _resolve_attack(self, attacker: Card, defender: Card):
        """
        Resolve a standard attack following damage calculation order.
        
        Damage Calculation Order (FINAL):
        1. Base attack value
        2. Apply percentage-based attack calculations (from opponent MAX HP)
        3. Apply buffs (Enraged, etc.)
        4. Apply debuffs
        5. Apply NEXT_ATTACK buffs (consumed after use)
        6. Apply damage reduction
        7. Apply dodge
        8. Apply critical multiplier
        9. Final HP subtraction
        """
        print_subheader("Combat Resolution")
        
        # 0. Check miss chance (attacker may miss)
        miss_chance = attacker.status_manager.get_miss_chance()
        if miss_chance > 0 and roll(miss_chance):
            self.log(f"{Colors.WARNING}{attacker.name} MISSED! ({miss_chance}% miss chance){Colors.RESET}")
            return
        
        # 0.5 Check auto-dodge (defender may auto-dodge)
        if defender.status_manager.check_auto_dodge():
            self.log(f"{Colors.SUCCESS}{defender.name} AUTO-DODGED the attack!{Colors.RESET}")
            return
        
        # SPECIAL: Chinese Beaver - Flip 5 coins, 1000 damage per heads (every attack)
        if attacker.name == "Chinese Beaver":
            flips = [coin() for _ in range(5)]
            heads = sum(1 for f in flips if f == "heads")
            flip_str = " ".join(["H" if f == "heads" else "T" for f in flips])
            damage = heads * 1000
            
            self.log(f"{Colors.WARNING}{attacker.name}: TAKE THAT WOOD! [{flip_str}] {heads} heads!{Colors.RESET}")
            
            if damage > 0:
                actual_damage = defender.take_damage(damage)
                self.log(f"{Colors.ERROR}{defender.name} takes {actual_damage} damage! "
                        f"({defender.current_hp}/{defender.max_hp} HP remaining){Colors.RESET}")
            else:
                self.log(f"{Colors.WARNING}No heads! No damage dealt!{Colors.RESET}")
            return
        
        # 1. Base attack value
        # 2. Percentage-based attack (calculated in get_attack_damage)
        # 3 & 4. Buffs and debuffs (ATK modifiers applied in get_attack_damage)
        base_damage = attacker.get_attack_damage(defender.max_hp)
        
        # 5. Apply NEXT_ATTACK buffs (consume them)
        next_attack_buffs = attacker.status_manager.get_next_attack_buffs()
        if next_attack_buffs["flat_damage"] > 0:
            base_damage += next_attack_buffs["flat_damage"]
            self.log(f"{Colors.SUCCESS}+{next_attack_buffs['flat_damage']} bonus damage from buffs!{Colors.RESET}")
        if next_attack_buffs["damage_mult"] > 100:
            mult = next_attack_buffs["damage_mult"] / 100
            base_damage = int(base_damage * mult)
            self.log(f"{Colors.SUCCESS}{mult}x damage multiplier applied!{Colors.RESET}")
        
        self.log(f"{attacker.name} attacks with {base_damage} base damage!")
        
        # 5. Apply damage reduction
        damage_reduction = defender.status_manager.get_damage_reduction()
        if damage_reduction > 0:
            reduction_amount = int(base_damage * (damage_reduction / 100))
            base_damage -= reduction_amount
            self.log(f"Damage reduced by {damage_reduction}% ({reduction_amount} blocked)")
        
        # Apply defense modifier
        def_mod = defender.get_defense_modifier()
        if def_mod != 0:
            def_multiplier = 1 - (def_mod / 100)  # Negative def_mod = more damage
            base_damage = int(base_damage * def_multiplier)
            if def_mod > 0:
                self.log(f"Defender's fortified defense reduces damage further")
            elif def_mod < 0:
                self.log(f"Defender's vulnerability increases damage!")
        
        # 6. Apply dodge
        dodge_chance = defender.status_manager.get_dodge_chance()
        if dodge_chance > 0:
            if roll(dodge_chance):
                self.log(f"{Colors.SUCCESS}{defender.name} DODGES the attack!{Colors.RESET}")
                return
            else:
                self.log(f"{Colors.WARNING}{defender.name}'s {dodge_chance}% dodge didn't proc!{Colors.RESET}")
        
        # 8. Apply critical multiplier
        crit_chance_bonus, crit_damage_bonus = attacker.status_manager.get_crit_modifiers()
        total_crit_chance = attacker.attack.crit_chance + crit_chance_bonus
        
        # Special: Aldo Ortiz 100% crit when above 1000 HP
        if attacker.name == "Aldo Ortiz" and attacker.current_hp > 1000:
            total_crit_chance = 100
            self.log(f"{Colors.INFO}{attacker.name}'s HP > 1000: GUARANTEED CRITICAL!{Colors.RESET}")
        
        is_crit = roll(total_crit_chance)
        if is_crit:
            crit_multiplier = (attacker.attack.crit_multiplier + crit_damage_bonus) / 100
            base_damage = int(base_damage * crit_multiplier)
            self.log(f"{Colors.ERROR}CRITICAL HIT! ({crit_multiplier:.0f}x damage){Colors.RESET}")
        elif crit_chance_bonus > 0:
            # Show when boosted crit failed
            self.log(f"{Colors.WARNING}Crit chance was {total_crit_chance}% but didn't proc!{Colors.RESET}")
        
        # 8. Final HP subtraction
        final_damage = max(0, base_damage)
        actual_damage = defender.take_damage(final_damage)
        
        self.log(f"{Colors.ERROR}{defender.name} takes {actual_damage} damage! "
                f"({defender.current_hp}/{defender.max_hp} HP remaining){Colors.RESET}")
        
        # Apply passive effects on damage dealt/taken
        if attacker.ability.is_passive:
            result = ability_engine.apply_passive(
                attacker, defender,
                attacker.ability.effect_id,
                {**attacker.ability.parameters, "damage_dealt": actual_damage},
                trigger="on_damage_dealt"
            )
            if result and result.success and result.message:
                self.log(result.message)
        
        # Also check separate passive field for attacker
        if attacker.passive:
            result = ability_engine.trigger_passive(
                attacker, attacker.passive.effect_id,
                "on_damage_dealt", {"damage_dealt": actual_damage, "target": defender}
            )
            if result and result.success and result.message:
                self.log(result.message)
        
        if defender.ability.is_passive:
            result = ability_engine.apply_passive(
                defender, attacker,
                defender.ability.effect_id,
                {**defender.ability.parameters, "damage_taken": actual_damage},
                trigger="on_damage_taken"
            )
            if result and result.success and result.message:
                self.log(result.message)
        
        # Also check separate passive field for defender
        if defender.passive:
            result = ability_engine.trigger_passive(
                defender, defender.passive.effect_id,
                "on_damage_taken", {"damage_taken": actual_damage, "attacker": attacker}
            )
            if result and result.success and result.message:
                self.log(result.message)
    
    def check_ko(self) -> bool:
        """
        Check for KO'd cards and handle replacement.
        
        Returns:
            True if game should continue, False if game over
        """
        # Check opponent's active card
        if self.opponent.active and not self.opponent.active.is_alive():
            ko_card = self.opponent.active
            points = ko_card.get_point_value()
            
            self.log(f"\n{Colors.SUCCESS}{ko_card.name} is KO'd! "
                    f"{self.current_player.name} scores {points} points!{Colors.RESET}")
            
            self.current_player.score += points
            
            # Announce total points
            self._announce_score_update(self.current_player)
            
            # Check win condition
            if self.current_player.score >= self.WIN_SCORE:
                self.game_over = True
                self.winner = self.current_player
                return False
            
            # Check if opponent can replace
            if not self.opponent.can_replace_active():
                if not self.opponent.deck_pool:
                    self.log(f"\n{Colors.ERROR}{self.opponent.name} has no cards left!{Colors.RESET}")
                    self.game_over = True
                    self.winner = self.current_player
                    return False
            
            # Opponent selects replacement
            self._handle_replacement(self.opponent)
        
        # Check current player's active (could die from reflect, thorns, etc.)
        if self.current_player.active and not self.current_player.active.is_alive():
            ko_card = self.current_player.active
            points = ko_card.get_point_value()
            
            self.log(f"\n{Colors.ERROR}{ko_card.name} is KO'd! "
                    f"{self.opponent.name} scores {points} points!{Colors.RESET}")
            
            self.opponent.score += points
            
            # Announce total points
            self._announce_score_update(self.opponent)
            
            # Check win condition
            if self.opponent.score >= self.WIN_SCORE:
                self.game_over = True
                self.winner = self.opponent
                return False
            
            # Check if current player can replace
            if not self.current_player.can_replace_active():
                if not self.current_player.deck_pool:
                    self.log(f"\n{Colors.ERROR}{self.current_player.name} has no cards left!{Colors.RESET}")
                    self.game_over = True
                    self.winner = self.opponent
                    return False
            
            # Current player selects replacement
            self._handle_replacement(self.current_player)
        
        return True
    
    def _handle_replacement(self, player: Player):
        """Handle bench replacement when active is KO'd."""
        if not player.bench:
            return
        
        print_divider("=")
        print(f"\n{Colors.WARNING}{player.name}, select a replacement from bench:{Colors.RESET}")
        
        for i, card in enumerate(player.bench, 1):
            print(f"  {i}. {card.get_colored_name()} | HP: {card.current_hp}/{card.max_hp}")
        
        choice = get_numeric_input(f"Select bench card (1-{len(player.bench)}): ", 1, len(player.bench)) - 1
        
        success, msg = player.replace_active(choice)
        if success:
            print_success(msg)
            
            # Apply passive on combat start for new active
            if player.active:
                opponent = self.player1 if player == self.player2 else self.player2
                
                if player.active.ability.is_passive:
                    result = ability_engine.apply_passive(
                        player.active, opponent.active,
                        player.active.ability.effect_id,
                        player.active.ability.parameters,
                        trigger="battle_start"
                    )
                    if result and result.success and result.message:
                        self.log(result.message)
                
                # Also trigger separate passive field
                if player.active.passive:
                    result = ability_engine.trigger_passive(
                        player.active, player.active.passive.effect_id,
                        "battle_start", {}
                    )
                    if result and result.success and result.message:
                        self.log(result.message)
                
                # Also trigger secondary passive
                if player.active.secondary_passive:
                    result = ability_engine.trigger_passive(
                        player.active, player.active.secondary_passive.effect_id,
                        "battle_start", {}
                    )
                    if result and result.success and result.message:
                        self.log(result.message)
        else:
            print_error(msg)
    
    def _announce_score_update(self, player: Player):
        """Announce total points and points needed to win."""
        points_needed = self.WIN_SCORE - player.score
        opponent = self.player1 if player == self.player2 else self.player2
        
        self.log(f"\n{Colors.INFO}╔══════════════════════════════════════════╗{Colors.RESET}")
        self.log(f"{Colors.INFO}║  SCORE UPDATE                            ║{Colors.RESET}")
        self.log(f"{Colors.INFO}╠══════════════════════════════════════════╣{Colors.RESET}")
        self.log(f"{Colors.INFO}║  {player.name}: {player.score} / {self.WIN_SCORE} points{' ' * (23 - len(player.name) - len(str(player.score)))}║{Colors.RESET}")
        self.log(f"{Colors.INFO}║  {opponent.name}: {opponent.score} / {self.WIN_SCORE} points{' ' * (23 - len(opponent.name) - len(str(opponent.score)))}║{Colors.RESET}")
        
        if points_needed <= 0:
            self.log(f"{Colors.SUCCESS}║  {player.name} WINS!                        ║{Colors.RESET}")
        else:
            self.log(f"{Colors.INFO}║  {player.name} needs {points_needed} more points to win{' ' * (8 - len(str(points_needed)))}║{Colors.RESET}")
        
        self.log(f"{Colors.INFO}╚══════════════════════════════════════════╝{Colors.RESET}")
    
    def end_turn(self):
        """End current turn and switch players."""
        input("\nPress Enter to end turn...")
        
        # Switch players
        self.current_player, self.opponent = self.opponent, self.current_player
        self.turn_number += 1
        
        # Tick status durations after a full ROUND (both players have gone)
        # Player 1 goes on odd turns, Player 2 on even turns
        # After turn 2, 4, 6, etc. (even turns), a full round is complete
        if self.turn_number % 2 == 1 and self.turn_number > 1:
            self._tick_round_statuses()
        
        self.clear_log()
    
    def _tick_round_statuses(self):
        """Tick status durations for both players at end of round."""
        for player in [self.player1, self.player2]:
            if player.active:
                expired = player.active.status_manager.tick_all()
                for status in expired:
                    self.log(f"{player.active.name}'s {status.name} has worn off.")
    
    def run_turn(self) -> bool:
        """
        Run a complete turn.
        
        Returns:
            True if game continues, False if game over
        """
        # Display state
        self.display_game_state()
        
        # Start of turn
        if not self.resolve_start_of_turn():
            # Turn was skipped or card died to DoT
            if self.current_player.active and not self.current_player.active.is_alive():
                if not self.check_ko():
                    return False
            self.end_turn()
            return True
        
        # Player action
        action, ability_result = self.player_action_phase()
        
        # Combat resolution
        self.resolve_combat(action, ability_result)
        
        # KO check
        if not self.check_ko():
            return False
        
        # End turn
        self.end_turn()
        
        return True
    
    def display_victory(self):
        """Display victory screen."""
        clear_screen()
        print_header("GAME OVER")
        
        # Display what happened in the final turn
        print(f"\n{Colors.INFO}=== FINAL TURN EVENTS ==={Colors.RESET}")
        # Use combat_log if game ended mid-turn (before clear), else use last_turn_log
        final_log = self.combat_log if self.combat_log else self.last_turn_log
        if final_log:
            for msg in final_log:
                print(f"  {msg}")
        print()
        
        print(f"{Colors.SUCCESS}{'=' * 50}{Colors.RESET}")
        print(f"{Colors.SUCCESS}{self.winner.name.upper()} WINS!{Colors.RESET}".center(60))
        print(f"{Colors.SUCCESS}{'=' * 50}{Colors.RESET}")
        
        print(f"\n{Colors.INFO}Final Scores:{Colors.RESET}")
        print(f"  {self.player1.name}: {self.player1.score} points")
        print(f"  {self.player2.name}: {self.player2.score} points")
        
        print(f"\nGame lasted {self.turn_number} turns.")
        
        input("\nPress Enter to exit...")
    
    def initialize_passives(self):
        """Initialize passive abilities at game start."""
        for player in [self.player1, self.player2]:
            if player.active:
                opponent = self.player1 if player == self.player2 else self.player2
                card = player.active
                
                # Check if ability itself is passive
                if card.ability.is_passive:
                    result = ability_engine.apply_passive(
                        card, opponent.active,
                        card.ability.effect_id,
                        card.ability.parameters,
                        trigger="battle_start"
                    )
                    if result and result.success and result.message:
                        print(result.message)
                
                # Check for separate passive field
                if card.passive:
                    result = ability_engine.trigger_passive(
                        card, card.passive.effect_id,
                        "battle_start", {}
                    )
                    if result and result.success and result.message:
                        print(result.message)
                
                # Check for secondary passive
                if card.secondary_passive:
                    result = ability_engine.trigger_passive(
                        card, card.secondary_passive.effect_id,
                        "battle_start", {}
                    )
                    if result and result.success and result.message:
                        print(result.message)
    
    def run_game(self):
        """Run the complete game loop."""
        # Initialize passives
        self.initialize_passives()
        
        # Main game loop
        while not self.game_over:
            if not self.run_turn():
                break
        
        # Victory screen
        self.display_victory()
