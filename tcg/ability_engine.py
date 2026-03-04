"""
Ability Engine for Terminal Chaos TCG
Handles execution of all card abilities for custom cards
"""
from typing import TYPE_CHECKING, Callable, Any, Optional
from status import create_status, Status, EffectType
from utils import roll, coin, random_choice, print_success, print_warning, Colors
import random

if TYPE_CHECKING:
    from card import Card


class AbilityResult:
    """Result of an ability execution."""
    
    def __init__(self, success: bool = True, message: str = "", damage_dealt: int = 0,
                 healing_done: int = 0, statuses_applied: list = None, 
                 transform_to: str = None, kill_self: bool = False, kill_target: bool = False):
        self.success = success
        self.message = message
        self.damage_dealt = damage_dealt
        self.healing_done = healing_done
        self.statuses_applied = statuses_applied or []
        self.transform_to = transform_to
        self.kill_self = kill_self
        self.kill_target = kill_target


class AbilityEngine:
    """
    Centralized ability execution engine.
    All ability logic is contained here for modularity.
    """
    
    def __init__(self):
        # Registry of ability handlers
        self._abilities: dict[str, Callable] = {
            "none": self._ability_none,
            
            # Generic test abilities
            "direct_damage": self._ability_direct_damage,
            "heal_self": self._ability_heal_self,
            "apply_status": self._ability_apply_status,
            
            # Basic
            "hockey_stick": self._ability_hockey_stick,
            
            # Common
            "debate": self._ability_debate,
            "firm_handshake": self._ability_firm_handshake,
            "album_drop": self._ability_album_drop,
            "kobe_fadeaway": self._ability_kobe_fadeaway,
            "backboard_shatter": self._ability_backboard_shatter,
            "aggressive_language": self._ability_aggressive_language,
            "cough": self._ability_cough,
            
            # Rare
            "three_point_blick": self._ability_three_point_blick,
            "bark": self._ability_bark,
            "lebron_scream": self._ability_lebron_scream,
            "goon_akaze": self._ability_goon_akaze,
            "mask_removal": self._ability_mask_removal,
            "cybertruck": self._ability_cybertruck,
            
            # Epic
            "john_pork_calling": self._ability_john_pork_calling,
            "luv_is_rage": self._ability_luv_is_rage,
            "we_are_charlie_kirk": self._ability_we_are_charlie_kirk,
            "one_inch_punch": self._ability_one_inch_punch,
            "what_color_bugatti": self._ability_what_color_bugatti,
            
            # Mythical
            "bipolar_disorder": self._ability_bipolar_disorder,
            "freedom_speech": self._ability_freedom_speech,
            "diddle": self._ability_diddle,
            "missile_launch": self._ability_missile_launch,
            "hiding_spot": self._ability_hiding_spot,
            "rough_rider_charge": self._ability_rough_rider_charge,
            "dominion_expansion": self._ability_dominion_expansion,
            
            # Legendary
            "chase_down_block": self._ability_chase_down_block,
            "kidnap": self._ability_kidnap,
            "drone_strike": self._ability_drone_strike,
            "ap_euro_flashcards": self._ability_ap_euro_flashcards,
            "ricin": self._ability_ricin,
            "sit_on_u": self._ability_sit_on_u,
            "banana_slimer": self._ability_banana_slimer,
            
            # Ultra Legendary
            "nuclear_strike": self._ability_nuclear_strike,
            "take_that_wood": self._ability_take_that_wood,
            "thicc_calves": self._ability_thicc_calves,
            "caffeine_gum": self._ability_caffeine_gum,
            "bean_rice_cheese": self._ability_bean_rice_cheese,
        }
        
        # Passive handlers
        self._passives: dict[str, Callable] = {
            "none": lambda **kwargs: None,
            "secret_service": self._passive_secret_service,
            "backflip": self._passive_backflip,
            "steph_defense": self._passive_steph_defense,
            "mlk_peace": self._passive_mlk_peace,
            "saddam_shield": self._passive_saddam_shield,
            "monkey_agility": self._passive_monkey_agility,
            "asian_blindness": self._passive_asian_blindness,
            "procrastination": self._passive_procrastination,
            "alpha": self._passive_alpha,
            "aldo_slip": self._passive_aldo_slip,
            "jump": self._passive_jump,
            "high_dodge": self._passive_high_dodge,
            "beaver_timer": self._passive_beaver_timer,
        }
        
        # Death ability handlers
        self._death_abilities: dict[str, Callable] = {
            "none": lambda **kwargs: None,
            "auto_turret": self._death_auto_turret,
        }
    
    def execute_ability(
        self,
        user: 'Card',
        target: 'Card',
        ability_id: str,
        params: dict = None,
        game_state: dict = None
    ) -> AbilityResult:
        """
        Execute an ability.
        
        Args:
            user: Card using the ability
            target: Target card
            ability_id: Ability identifier
            params: Additional parameters
            game_state: Current game state (includes bench cards, etc.)
        
        Returns:
            AbilityResult with execution details
        """
        params = params or {}
        game_state = game_state or {}
        
        handler = self._abilities.get(ability_id, self._ability_none)
        
        try:
            return handler(user=user, target=target, params=params, game_state=game_state)
        except Exception as e:
            return AbilityResult(
                success=False,
                message=f"Ability failed: {str(e)}"
            )
    
    def trigger_passive(
        self,
        card: 'Card',
        passive_id: str,
        trigger_type: str,
        context: dict = None
    ) -> Optional[AbilityResult]:
        """
        Trigger a passive ability.
        
        Args:
            card: Card with the passive
            passive_id: Passive identifier
            trigger_type: What triggered it (turn_start, on_hit, etc.)
            context: Additional context
        
        Returns:
            AbilityResult if triggered, None otherwise
        """
        context = context or {}
        handler = self._passives.get(passive_id)
        
        if handler:
            return handler(card=card, trigger_type=trigger_type, context=context)
        return None
    
    def apply_passive(
        self,
        card: 'Card',
        target: 'Card',
        effect_id: str,
        parameters: dict = None,
        trigger: str = "turn_start"
    ) -> AbilityResult:
        """
        Apply a passive ability with target context.
        
        Args:
            card: Card with the passive
            target: Target card (opponent)
            effect_id: Passive effect identifier
            parameters: Additional parameters
            trigger: What triggered it
        
        Returns:
            AbilityResult from passive execution
        """
        context = {
            "target": target,
            "parameters": parameters or {}
        }
        result = self.trigger_passive(card, effect_id, trigger, context)
        if result:
            return result
        return AbilityResult(success=True, message="")
    
    def trigger_death_ability(
        self,
        card: 'Card',
        death_ability_id: str,
        game_state: dict = None
    ) -> Optional[AbilityResult]:
        """
        Trigger a death ability.
        """
        game_state = game_state or {}
        handler = self._death_abilities.get(death_ability_id)
        
        if handler:
            return handler(card=card, game_state=game_state)
        return None
    
    # ============================================
    # BASIC ABILITIES
    # ============================================
    
    def _ability_none(self, **kwargs) -> AbilityResult:
        """No ability."""
        return AbilityResult(success=True, message="No ability used.")
    
    def _ability_direct_damage(self, user: 'Card', target: 'Card', params: dict = None, **kwargs) -> AbilityResult:
        """Deal direct damage to target."""
        params = params or {}
        damage = params.get("damage", 50)
        target.take_damage(damage)
        return AbilityResult(
            success=True,
            message=f"{user.name} deals {damage} direct damage!",
            damage_dealt=damage
        )
    
    def _ability_heal_self(self, user: 'Card', params: dict = None, **kwargs) -> AbilityResult:
        """Heal self."""
        params = params or {}
        amount = params.get("amount", 50)
        healed = user.heal(amount)
        return AbilityResult(
            success=True,
            message=f"{user.name} heals {healed} HP!",
            healing_done=healed
        )
    
    def _ability_apply_status(self, user: 'Card', target: 'Card', params: dict = None, **kwargs) -> AbilityResult:
        """Apply a status effect to target."""
        params = params or {}
        status_name = params.get("status", "Burn")
        duration = params.get("duration", 2)
        status = create_status(status_name, duration=duration, source=user.name)
        target.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} applies {status_name} to {target.name}!",
            statuses_applied=[status_name]
        )
    
    def _ability_hockey_stick(self, user: 'Card', **kwargs) -> AbilityResult:
        """Jack Orense: Next attack does +250 damage."""
        status = create_status("Hockey Stick", source=user.name)
        user.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} readies hockey stick! Next attack: +250 damage!",
            statuses_applied=["Hockey Stick"]
        )
    
    # ============================================
    # COMMON ABILITIES
    # ============================================
    
    def _ability_debate(self, user: 'Card', **kwargs) -> AbilityResult:
        """Charlie Kirk: Next attack has 25% chance to inflict CRITICAL(500%) damage."""
        status = create_status("Debate Crit", source=user.name)
        user.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} initiates a debate! 25% chance for 500% CRITICAL next attack!",
            statuses_applied=["Debate Crit"]
        )
    
    def _ability_firm_handshake(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """Donald Trump: Heal 10% HP, drain 10% from opponent."""
        heal_amount = int(user.max_hp * 0.10)
        drain_amount = int(target.max_hp * 0.10)
        
        user.heal(heal_amount)
        target.take_damage(drain_amount)
        
        return AbilityResult(
            success=True,
            message=f"{user.name} firmly shakes hands! Healed {heal_amount}, drained {drain_amount}!",
            damage_dealt=drain_amount,
            healing_done=heal_amount
        )
    
    def _ability_album_drop(self, user: 'Card', **kwargs) -> AbilityResult:
        """Kanye West: 10% chance to transform into Ye, else boost next attack."""
        if roll(10):
            return AbilityResult(
                success=True,
                message=f"{user.name} drops a legendary album! Transforming into YE!",
                transform_to="Ye"
            )
        else:
            status = create_status("Album Drop Buff", source=user.name)
            user.status_manager.add_status(status)
            return AbilityResult(
                success=True,
                message=f"{user.name} drops an album! Next attack deals 33% opponent's HP!",
                statuses_applied=["Album Drop Buff"]
            )
    
    def _ability_kobe_fadeaway(self, user: 'Card', **kwargs) -> AbilityResult:
        """Kobe Bryant: Next attack has 44.7% chance to SWISH dealing 150% damage."""
        status = create_status("Kobe Crit", source=user.name)
        user.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} sets up the fadeaway! 44.7% chance for 150% CRITICAL!",
            statuses_applied=["Kobe Crit"]
        )
    
    def _ability_backboard_shatter(self, user: 'Card', **kwargs) -> AbilityResult:
        """Shaq: 50% Damage reduction for 3 turns."""
        status = create_status("Backboard Shatter", duration=3, source=user.name)
        user.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} SHATTERS THE BACKBOARD! 50% damage reduction for 3 turns!",
            statuses_applied=["Backboard Shatter"]
        )
    
    def _ability_aggressive_language(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """Burger King Guy: Apply ragebait DoT (5% HP for 5 turns)."""
        status = create_status("Ragebait", duration=5, source=user.name)
        target.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} unleashes aggressive language! {target.name} takes ragebait damage!",
            statuses_applied=["Ragebait"]
        )
    
    def _ability_cough(self, user: 'Card', **kwargs) -> AbilityResult:
        """Coughing Baby: Flip 3 coins, if all same face, transform to Hydrogen Bomb."""
        flips = [coin() for _ in range(3)]
        flip_str = ", ".join(["Heads" if f else "Tails" for f in flips])
        
        if all(flips) or not any(flips):
            return AbilityResult(
                success=True,
                message=f"{user.name} coughs... [{flip_str}] ALL SAME! TRANSFORMING TO HYDROGEN BOMB!",
                transform_to="Hydrogen Bomb"
            )
        else:
            return AbilityResult(
                success=True,
                message=f"{user.name} coughs... [{flip_str}] Nothing happens..."
            )
    
    # ============================================
    # RARE ABILITIES
    # ============================================
    
    def _ability_three_point_blick(self, user: 'Card', **kwargs) -> AbilityResult:
        """Steph Curry: 42% chance to shoot a CRITICAL (250%) shot."""
        status = create_status("Steph Crit", source=user.name)
        user.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} lines up the 3-pointer! 42% chance for 250% CRITICAL!",
            statuses_applied=["Steph Crit"]
        )
    
    def _ability_bark(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """IShowSpeed: Enrage opponent, 33% chance to miss next attack."""
        status = create_status("Barked At", source=user.name)
        target.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} BARKS at {target.name}! 33% chance to miss next attack!",
            statuses_applied=["Barked At"]
        )
    
    def _ability_lebron_scream(self, user: 'Card', **kwargs) -> AbilityResult:
        """Hungryhungryhanny: Flip 2 coins, both heads = 1000% CRITICAL next turn."""
        flips = [coin(), coin()]
        flip_str = ", ".join(["Heads" if f else "Tails" for f in flips])
        
        if all(flips):
            status = create_status("Lebron Crit", source=user.name)
            user.status_manager.add_status(status)
            return AbilityResult(
                success=True,
                message=f"{user.name} screams... [{flip_str}] ELEVATOR LEBRON SCREAM! 1000% CRIT next turn!",
                statuses_applied=["Lebron Crit"]
            )
        else:
            return AbilityResult(
                success=True,
                message=f"{user.name} screams... [{flip_str}] Not enough power..."
            )
    
    def _ability_goon_akaze(self, user: 'Card', target: 'Card', game_state: dict = None, **kwargs) -> AbilityResult:
        """Goonicide guy: 800 damage, bench cards get 10% permanent miss chance."""
        damage = 800
        target.take_damage(damage)
        
        messages = [f"{user.name} GOON-AKAZES! {target.name} takes {damage} damage!"]
        
        # Apply gooned to all bench cards
        if game_state and "opponent_bench" in game_state:
            for bench_card in game_state["opponent_bench"]:
                status = create_status("Gooned", source=user.name)
                bench_card.status_manager.add_status(status)
                messages.append(f"{bench_card.name} is GOONED!")
        
        return AbilityResult(
            success=True,
            message=" ".join(messages),
            damage_dealt=damage,
            statuses_applied=["Gooned"]
        )
    
    def _ability_mask_removal(self, user: 'Card', **kwargs) -> AbilityResult:
        """NPC: Double all stats permanently, incapacitate for 1 turn."""
        status_double = create_status("Double Stats", source=user.name)
        status_incap = create_status("Incapacitated", source=user.name)
        
        user.status_manager.add_status(status_double)
        user.status_manager.add_status(status_incap)
        
        # Actually double base stats
        user.attack.base_damage *= 2
        user.max_hp *= 2
        user.current_hp = min(user.current_hp * 2, user.max_hp)
        
        return AbilityResult(
            success=True,
            message=f"{user.name} removes mask and equips [stick]! STATS DOUBLED! Incapacitated for 1 turn.",
            statuses_applied=["Double Stats", "Incapacitated"]
        )
    
    def _ability_cybertruck(self, user: 'Card', **kwargs) -> AbilityResult:
        """Elon Musk: Get 500 HP shield, 25% bleed through, 2x attack while in truck."""
        status = create_status("Cybertruck", source=user.name, stacks_override=500)
        user.status_manager.add_status(status)
        
        # Also double attack while in cybertruck via stat modifier
        enraged = create_status("Empowered", duration=-1, source="Cybertruck", magnitude_override=100)
        user.status_manager.add_status(enraged)
        
        return AbilityResult(
            success=True,
            message=f"{user.name} hops in the CYBERTRUCK! 500 HP shield, 2x attack!",
            statuses_applied=["Cybertruck", "Empowered"]
        )
    
    # ============================================
    # EPIC ABILITIES
    # ============================================
    
    def _ability_john_pork_calling(self, user: 'Card', game_state: dict = None, **kwargs) -> AbilityResult:
        """John Pork: 33% chance to insta-kill a random bench card."""
        if game_state and "opponent_bench" in game_state and game_state["opponent_bench"]:
            bench = game_state["opponent_bench"]
            if bench and roll(33):
                target_card = random.choice(bench)
                target_card.current_hp = 0
                return AbilityResult(
                    success=True,
                    message=f"{user.name} is calling... {target_card.name} ANSWERED AND DIED!",
                    kill_target=True
                )
            else:
                return AbilityResult(
                    success=True,
                    message=f"{user.name} is calling... but nobody answered. (33% failed)"
                )
        
        return AbilityResult(
            success=True,
            message=f"{user.name} is calling... but the bench is empty."
        )
    
    def _ability_luv_is_rage(self, user: 'Card', game_state: dict = None, **kwargs) -> AbilityResult:
        """Lil Uzi Vert: Buff bench card stats by 25%."""
        if game_state and "user_bench" in game_state and game_state["user_bench"]:
            messages = []
            for bench_card in game_state["user_bench"]:
                status = create_status("Luv Buff", source=user.name)
                bench_card.status_manager.add_status(status)
                messages.append(f"{bench_card.name} buffed!")
            
            return AbilityResult(
                success=True,
                message=f"{user.name}: LUV IS RAGE! " + " ".join(messages),
                statuses_applied=["Luv Buff"]
            )
        
        return AbilityResult(
            success=True,
            message=f"{user.name}: LUV IS RAGE! But no bench cards to buff."
        )
    
    def _ability_we_are_charlie_kirk(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """Erica Kirk: 50% chance for opponent's next attack to hit themselves."""
        status = create_status("Reflection", source=user.name)
        target.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name}: WE ARE CHARLIE KIRK! 50% chance {target.name}'s next attack hits themselves!",
            statuses_applied=["Reflection"]
        )
    
    def _ability_one_inch_punch(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """Bruce Lee: Deal 1.5x damage (ignoring height as per user request)."""
        # Apply 1.5x damage as a crit-like effect
        damage = int(user.attack.base_damage * 1.5)
        target.take_damage(damage)
        
        return AbilityResult(
            success=True,
            message=f"{user.name} delivers ONE INCH PUNCH! {damage} damage!",
            damage_dealt=damage
        )
    
    def _ability_what_color_bugatti(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """Andrew Tate: Roll colors, if match opponent joins your team (implemented as stun)."""
        colors = ["Red", "Black", "Blue"]
        user_color = random.choice(colors)
        opponent_color = random.choice(colors)
        
        if user_color == opponent_color:
            # Can't literally switch teams, so massive debuff instead
            status = create_status("Anguish", duration=3, source=user.name)
            target.status_manager.add_status(status)
            return AbilityResult(
                success=True,
                message=f"WHAT COLOR'S YOUR BUGATTI? [{user_color} vs {opponent_color}] MATCH! {target.name} is brainwashed!",
                statuses_applied=["Anguish"]
            )
        else:
            return AbilityResult(
                success=True,
                message=f"WHAT COLOR'S YOUR BUGATTI? [{user_color} vs {opponent_color}] No match."
            )
    
    # ============================================
    # MYTHICAL ABILITIES
    # ============================================
    
    def _ability_bipolar_disorder(self, user: 'Card', **kwargs) -> AbilityResult:
        """Ye: 5% chance to revert to Kanye West."""
        if roll(5):
            return AbilityResult(
                success=True,
                message=f"{user.name} has a bipolar episode! Reverting to Kanye West...",
                transform_to="Kanye West"
            )
        return AbilityResult(
            success=True,
            message=f"{user.name} stays focused."
        )
    
    def _ability_freedom_speech(self, user: 'Card', **kwargs) -> AbilityResult:
        """MLK: Heal 200 HP."""
        heal_amount = 200
        user.heal(heal_amount)
        return AbilityResult(
            success=True,
            message=f"{user.name}: I HAVE A DREAM! Healed {heal_amount} HP!",
            healing_done=heal_amount
        )
    
    def _ability_diddle(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """Diddy: Kidnap effect - like Epstein."""
        if roll(50):
            status = create_status("Kidnapped", source=user.name)
            target.status_manager.add_status(status)
            return AbilityResult(
                success=True,
                message=f"{user.name} kidnaps {target.name}! Skip next turn!",
                statuses_applied=["Kidnapped"]
            )
        return AbilityResult(
            success=True,
            message=f"{user.name} attempts to kidnap... but fails!"
        )
    
    def _ability_missile_launch(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """Kim Jong-Un: 95% false alarm, 5% deals 90% HP."""
        if roll(5):
            damage = int(target.max_hp * 0.90)
            target.take_damage(damage)
            return AbilityResult(
                success=True,
                message=f"{user.name} LAUNCHES MISSILE! DIRECT HIT! {damage} damage (90% HP)!",
                damage_dealt=damage
            )
        else:
            return AbilityResult(
                success=True,
                message=f"{user.name} launches missile... FALSE ALARM!"
            )
    
    def _ability_hiding_spot(self, user: 'Card', **kwargs) -> AbilityResult:
        """Saddam Hussein: 50% extra dodge chance."""
        status = create_status("Hiding Spot", source=user.name)
        user.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} hides in his hiding spot! 50% dodge chance!",
            statuses_applied=["Hiding Spot"]
        )
    
    def _ability_rough_rider_charge(self, user: 'Card', **kwargs) -> AbilityResult:
        """Theodore Roosevelt: 2x damage next turn."""
        status = create_status("Rough Rider", source=user.name)
        user.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} CHARGES! ROUGH RIDER! 2x damage next attack!",
            statuses_applied=["Rough Rider"]
        )
    
    def _ability_dominion_expansion(self, user: 'Card', **kwargs) -> AbilityResult:
        """Gorlock: Heal 25% and tank for bench."""
        heal_amount = int(user.max_hp * 0.25)
        user.heal(heal_amount)
        return AbilityResult(
            success=True,
            message=f"{user.name}: DOMINION EXPANSION! Healed {heal_amount}! Takes all damage for bench!",
            healing_done=heal_amount
        )
    
    # ============================================
    # LEGENDARY ABILITIES
    # ============================================
    
    def _ability_chase_down_block(self, user: 'Card', **kwargs) -> AbilityResult:
        """Lebron James: Block incoming attack (high dodge this turn)."""
        status = create_status("High Dodge", duration=1, source=user.name, magnitude_override=75)
        user.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name}: CHASE DOWN BLOCK! 75% dodge this turn!",
            statuses_applied=["High Dodge"]
        )
    
    def _ability_kidnap(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """Jeffrey Epstein: 50% chance to skip opponent's next turn."""
        if roll(50):
            status = create_status("Kidnapped", source=user.name)
            target.status_manager.add_status(status)
            return AbilityResult(
                success=True,
                message=f"{user.name} kidnaps {target.name}! Skip next turn!",
                statuses_applied=["Kidnapped"]
            )
        return AbilityResult(
            success=True,
            message=f"{user.name} attempts to kidnap... failed!"
        )
    
    def _ability_drone_strike(self, user: 'Card', target: 'Card', game_state: dict = None, **kwargs) -> AbilityResult:
        """Barack Obama: 10% chance to deal 10% HP to all opponent cards."""
        messages = []
        total_damage = 0
        
        if roll(10):
            # Deal damage to active card
            damage = int(target.max_hp * 0.10)
            target.take_damage(damage)
            total_damage += damage
            messages.append(f"{target.name}: -{damage}")
            
            # Deal damage to bench
            if game_state and "opponent_bench" in game_state:
                for bench_card in game_state["opponent_bench"]:
                    dmg = int(bench_card.max_hp * 0.10)
                    bench_card.take_damage(dmg)
                    total_damage += dmg
                    messages.append(f"{bench_card.name}: -{dmg}")
            
            return AbilityResult(
                success=True,
                message=f"{user.name}: DRONE STRIKE! Extra drones deployed! {' | '.join(messages)}",
                damage_dealt=total_damage
            )
        else:
            return AbilityResult(
                success=True,
                message=f"{user.name}: Drone strike... no extra drones this time."
            )
    
    def _ability_ap_euro_flashcards(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """Mr. Michaelsen: Random quiz, if wrong get 80% DR for 3 turns."""
        # Always "wrong" for simplicity (or could implement actual quiz)
        if roll(30):  # 30% chance to "answer correctly"
            return AbilityResult(
                success=True,
                message=f"{user.name} pulls out AP Euro flashcards... {target.name} answered correctly!"
            )
        else:
            status = create_status("Napoleon", duration=3, source=user.name)
            user.status_manager.add_status(status)
            return AbilityResult(
                success=True,
                message=f"{user.name}: AP EURO FLASHCARDS! Wrong answer! Equips Napoleon outfit! 80% DR for 3 turns!",
                statuses_applied=["Napoleon"]
            )
    
    def _ability_ricin(self, user: 'Card', target: 'Card', game_state: dict = None, **kwargs) -> AbilityResult:
        """Walter White: Apply Ricin DoT to a card (10% HP for 4 turns)."""
        # Apply to target by default, but could target bench
        status = create_status("Ricin", duration=4, source=user.name)
        target.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} poisons {target.name} with RICIN! 10% HP damage for 4 turns!",
            statuses_applied=["Ricin"]
        )
    
    def _ability_sit_on_u(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """CaseOh: Opponent can't attack for 2 turns."""
        status = create_status("Sat On", duration=2, source=user.name)
        target.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} SITS ON {target.name}! Can't attack for 2 turns!",
            statuses_applied=["Sat On"]
        )
    
    def _ability_banana_slimer(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """Monkey: Inflict anguish (-90% attack for 2 turns)."""
        status = create_status("Anguish", duration=2, source=user.name)
        target.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} throws BANANA SLIME! {target.name} has -90% ATK for 2 turns!",
            statuses_applied=["Anguish"]
        )
    
    # ============================================
    # ULTRA LEGENDARY ABILITIES
    # ============================================
    
    def _ability_nuclear_strike(self, user: 'Card', target: 'Card', **kwargs) -> AbilityResult:
        """Hydrogen Bomb: Both cards are killed."""
        return AbilityResult(
            success=True,
            message=f"{user.name}: NUCLEAR STRIKE! BOTH CARDS DESTROYED!",
            kill_self=True,
            kill_target=True
        )
    
    def _ability_take_that_wood(self, user: 'Card', target: 'Card', game_state: dict = None, **kwargs) -> AbilityResult:
        """Chinese Beaver: Flip 5 coins. Deal 1000 damage per heads."""
        flips = [coin() for _ in range(5)]
        heads = sum(1 for f in flips if f == "heads")
        flip_str = " ".join(["H" if f == "heads" else "T" for f in flips])
        
        damage = heads * 1000
        
        # Deal damage to active opponent
        if damage > 0 and target:
            target.take_damage(damage)
        
        return AbilityResult(
            success=True,
            message=f"{user.name}: TAKE THAT WOOD! [{flip_str}] {heads} heads = {damage} damage!",
            damage_dealt=damage
        )
    
    def _ability_thicc_calves(self, user: 'Card', **kwargs) -> AbilityResult:
        """Noah Tsui: Auto dodge next 2 attacks."""
        status = create_status("Thicc Calves", source=user.name, stacks_override=2)
        user.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name}: THICC CALVES! Auto-dodges next 2 attacks!",
            statuses_applied=["Thicc Calves"]
        )
    
    def _ability_caffeine_gum(self, user: 'Card', **kwargs) -> AbilityResult:
        """Colin Sweeney: Double coin flips next turn."""
        status = create_status("Caffeine", source=user.name)
        user.status_manager.add_status(status)
        return AbilityResult(
            success=True,
            message=f"{user.name} chews CAFFEINE GUM! Coin flips doubled next turn!",
            statuses_applied=["Caffeine"]
        )
    
    def _ability_bean_rice_cheese(self, user: 'Card', target: 'Card', game_state: dict = None, **kwargs) -> AbilityResult:
        """Aldo Ortiz: 33% each for Bean, Rice, or Cheese effect."""
        roll_val = random.randint(1, 100)
        
        if roll_val <= 33:
            # BEAN: 200 piercing damage to all
            messages = [f"BEAN! Explosive beans deal 200 piercing damage!"]
            target.take_damage(200)
            messages.append(f"{target.name}: -200")
            
            if game_state and "opponent_bench" in game_state:
                for bench_card in game_state["opponent_bench"]:
                    bench_card.take_damage(200)
                    messages.append(f"{bench_card.name}: -200")
            
            return AbilityResult(
                success=True,
                message=f"{user.name}: BEAN RICE AND CHEESE BURRITO! " + " ".join(messages),
                damage_dealt=200
            )
        
        elif roll_val <= 66:
            # RICE: Glutton debuff
            status = create_status("Glutton", duration=6, source=user.name)
            target.status_manager.add_status(status)
            return AbilityResult(
                success=True,
                message=f"{user.name}: BEAN RICE AND CHEESE BURRITO! RICE! {target.name} has GLUTTON! Skips every other turn for 3 turns!",
                statuses_applied=["Glutton"]
            )
        
        else:
            # CHEESE: Heal to 1001 HP, 3x damage next turn
            user.current_hp = 1001
            if user.max_hp < 1001:
                user.max_hp = 1001
            
            status = create_status("Cheese Buff", source=user.name)
            user.status_manager.add_status(status)
            
            return AbilityResult(
                success=True,
                message=f"{user.name}: BEAN RICE AND CHEESE BURRITO! CHEESE! HP set to 1001! 3x damage next attack!",
                statuses_applied=["Cheese Buff"],
                healing_done=1001 - user.current_hp if user.current_hp < 1001 else 0
            )
    
    # ============================================
    # PASSIVE HANDLERS
    # ============================================
    
    def _passive_secret_service(self, card: 'Card', trigger_type: str, context: dict = None, **kwargs) -> Optional[AbilityResult]:
        """Donald Trump: 25% DR, 10% chance to heal to full each turn."""
        if trigger_type == "turn_start":
            # Add DR if not present
            if not card.status_manager.has_status("Secret Service"):
                status = create_status("Secret Service", source=card.name)
                card.status_manager.add_status(status)
            
            # 10% chance to heal to full
            if roll(10):
                heal_amount = card.max_hp - card.current_hp
                card.heal(heal_amount)
                return AbilityResult(
                    success=True,
                    message=f"{card.name}'s Secret Service heals to full! +{heal_amount} HP!",
                    healing_done=heal_amount
                )
        return None
    
    def _passive_backflip(self, card: 'Card', trigger_type: str, context: dict = None, **kwargs) -> Optional[AbilityResult]:
        """IShowSpeed: 25% chance to backflip, healing 300 HP (can overflow)."""
        if trigger_type == "turn_start":
            if roll(25):
                old_hp = card.current_hp
                card.current_hp = min(card.current_hp + 300, card.max_hp + 150)  # Allow some overflow
                if card.current_hp > card.max_hp:
                    card.max_hp = card.current_hp
                heal = card.current_hp - old_hp
                return AbilityResult(
                    success=True,
                    message=f"{card.name} does a BACKFLIP! +{heal} HP! (can overflow)",
                    healing_done=heal
                )
        return None
    
    def _passive_steph_defense(self, card: 'Card', trigger_type: str, **kwargs) -> Optional[AbilityResult]:
        """Steph Curry: 33% damage reduction."""
        if trigger_type in ["battle_start", "turn_start"]:
            if not card.status_manager.has_status("Steph Defense"):
                status = create_status("Steph Defense", source=card.name)
                card.status_manager.add_status(status)
                return AbilityResult(
                    success=True,
                    message=f"{card.name}'s Steph Defense active! 33% DR!"
                )
        return None
    
    def _passive_mlk_peace(self, card: 'Card', trigger_type: str, **kwargs) -> Optional[AbilityResult]:
        """MLK: 80% damage reduction."""
        if trigger_type in ["battle_start", "turn_start"]:
            if not card.status_manager.has_status("MLK Peace"):
                status = create_status("MLK Peace", source=card.name)
                card.status_manager.add_status(status)
                return AbilityResult(
                    success=True,
                    message=f"{card.name}'s MLK Peace active! 80% DR!"
                )
        return None
    
    def _passive_saddam_shield(self, card: 'Card', trigger_type: str, **kwargs) -> Optional[AbilityResult]:
        """Saddam Hussein: 50% damage reduction."""
        if trigger_type in ["battle_start", "turn_start"]:
            if not card.status_manager.has_status("Saddam Shield"):
                status = create_status("Saddam Shield", source=card.name)
                card.status_manager.add_status(status)
                return AbilityResult(
                    success=True,
                    message=f"{card.name}'s Saddam Shield active! 50% DR!"
                )
        return None
    
    def _passive_monkey_agility(self, card: 'Card', trigger_type: str, **kwargs) -> Optional[AbilityResult]:
        """Monkey: 20% dodge chance."""
        if trigger_type in ["battle_start", "turn_start"]:
            if not card.status_manager.has_status("Monkey Agility"):
                status = create_status("Monkey Agility", source=card.name)
                card.status_manager.add_status(status)
                return AbilityResult(
                    success=True,
                    message=f"{card.name}'s Monkey Agility active! 20% dodge!"
                )
        return None
    
    def _passive_asian_blindness(self, card: 'Card', trigger_type: str, **kwargs) -> Optional[AbilityResult]:
        """Noah Tsui: 25% chance to miss attacks."""
        if trigger_type in ["battle_start", "turn_start"]:
            if not card.status_manager.has_status("Asian Blindness"):
                status = create_status("Asian Blindness", source=card.name)
                card.status_manager.add_status(status)
                return AbilityResult(
                    success=True,
                    message=f"{card.name}'s Asian Blindness active! 25% miss chance!"
                )
        return None
    
    def _passive_procrastination(self, card: 'Card', trigger_type: str, **kwargs) -> Optional[AbilityResult]:
        """Colin Sweeney: 25% chance to skip turn."""
        if trigger_type in ["battle_start", "turn_start"]:
            if not card.status_manager.has_status("Procrastination"):
                status = create_status("Procrastination", source=card.name)
                card.status_manager.add_status(status)
                return AbilityResult(
                    success=True,
                    message=f"{card.name}'s Procrastination active! 25% skip turn chance!"
                )
        return None
    
    def _passive_alpha(self, card: 'Card', trigger_type: str, **kwargs) -> Optional[AbilityResult]:
        """Andrew Tate: 25% damage reduction."""
        if trigger_type in ["battle_start", "turn_start"]:
            if not card.status_manager.has_status("Alpha"):
                status = create_status("Alpha", source=card.name)
                card.status_manager.add_status(status)
                return AbilityResult(
                    success=True,
                    message=f"{card.name}'s Alpha passive active! 25% DR!"
                )
        return None
    
    def _passive_aldo_slip(self, card: 'Card', trigger_type: str, **kwargs) -> Optional[AbilityResult]:
        """Aldo Ortiz: 25% chance to slip and immobilize for 1 turn."""
        if trigger_type == "turn_start":
            # Only slip when above 1000 HP (has high dodge otherwise)
            if card.current_hp > 1000 and roll(25):
                status_slip = create_status("Slipped", source=card.name)
                status_dodge = create_status("Slipped Dodge", source=card.name)
                status_nocrit = create_status("No Crit", source=card.name)
                
                card.status_manager.add_status(status_slip)
                card.status_manager.add_status(status_dodge)
                card.status_manager.add_status(status_nocrit)
                
                return AbilityResult(
                    success=True,
                    message=f"{card.name} SLIPPED ON THE ICE! Immobilized for 1 turn!",
                    statuses_applied=["Slipped", "Slipped Dodge", "No Crit"]
                )
        return None
    
    def _passive_jump(self, card: 'Card', trigger_type: str, **kwargs) -> Optional[AbilityResult]:
        """Noah Tsui: 50% chance to jump over attacks."""
        if trigger_type in ["battle_start", "turn_start"]:
            if not card.status_manager.has_status("Jump"):
                status = create_status("Jump", source=card.name)
                card.status_manager.add_status(status)
                return AbilityResult(
                    success=True,
                    message=f"{card.name}'s Jump passive active! 50% dodge!"
                )
        return None
    
    def _passive_high_dodge(self, card: 'Card', trigger_type: str, **kwargs) -> Optional[AbilityResult]:
        """Aldo Ortiz: 75% dodge when above 1000 HP."""
        if trigger_type in ["turn_start", "battle_start"]:
            if card.current_hp > 1000:
                if not card.status_manager.has_status("High Dodge"):
                    status = create_status("High Dodge", duration=-1, source=card.name, magnitude_override=75)
                    card.status_manager.add_status(status)
                    return AbilityResult(
                        success=True,
                        message=f"{card.name}'s High Dodge active! 75% dodge (HP > 1000)"
                    )
            else:
                if card.status_manager.has_status("High Dodge"):
                    card.status_manager.remove_status("High Dodge")
                    return AbilityResult(
                        success=True,
                        message=f"{card.name}'s High Dodge deactivated (HP <= 1000)"
                    )
        return None
    
    def _passive_beaver_timer(self, card: 'Card', trigger_type: str, **kwargs) -> Optional[AbilityResult]:
        """Chinese Beaver: Dies after 2 turns."""
        if trigger_type == "battle_start":
            # Initialize 2-turn timer
            status = create_status("Beaver Timer", source=card.name)
            card.status_manager.add_status(status)
            return AbilityResult(
                success=True,
                message=f"{card.name}'s timer started! 2 turns remaining!"
            )
        elif trigger_type == "turn_start":
            # Check if timer expired (ticked by status manager)
            if card.status_manager.has_status("Beaver Timer"):
                timer_status = card.status_manager.get_status("Beaver Timer")
                if timer_status and timer_status.duration == 1:
                    return AbilityResult(
                        success=True,
                        message=f"{card.name}'s timer: LAST TURN!"
                    )
            else:
                # Timer expired - beaver dies
                card.take_damage(card.current_hp)
                return AbilityResult(
                    success=True,
                    message=f"{card.name}'s timer expired! The beaver disappears!",
                    kill_self=True
                )
        return None
    
    # ============================================
    # DEATH ABILITY HANDLERS
    # ============================================
    
    def _death_auto_turret(self, card: 'Card', game_state: dict = None, **kwargs) -> Optional[AbilityResult]:
        """Walter White: Upon death, 25% HP to active, 15% to bench."""
        messages = []
        total_damage = 0
        
        if game_state:
            # Damage active opponent
            if "opponent_active" in game_state and game_state["opponent_active"]:
                active = game_state["opponent_active"]
                dmg = int(active.max_hp * 0.25)
                active.take_damage(dmg)
                total_damage += dmg
                messages.append(f"{active.name}: -{dmg}")
            
            # Damage bench
            if "opponent_bench" in game_state:
                for bench_card in game_state["opponent_bench"]:
                    dmg = int(bench_card.max_hp * 0.15)
                    bench_card.take_damage(dmg)
                    total_damage += dmg
                    messages.append(f"{bench_card.name}: -{dmg}")
        
        return AbilityResult(
            success=True,
            message=f"{card.name}'s AUTOMATIC TURRET activates! {' | '.join(messages)}",
            damage_dealt=total_damage
        )


# Singleton instance
ability_engine = AbilityEngine()
