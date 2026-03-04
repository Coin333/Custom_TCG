"""
Status Effect System for Terminal Chaos TCG
Handles all status effects, their application, resolution, and stacking
"""
from dataclasses import dataclass, field
from typing import Optional
from utils import apply_cap, roll


# ============================================
# STATUS EFFECT TYPES
# ============================================
class EffectType:
    """Enumeration of effect types"""
    SKIP_TURN = "skip_turn"           # Skip turn effects (highest priority)
    SELF_DAMAGE = "self_damage"       # Damage over time
    STAT_MODIFIER = "stat_modifier"   # ATK/DEF modifiers
    DODGE = "dodge"                   # Dodge chance
    CRITICAL = "critical"             # Critical hit modifiers
    DAMAGE_REDUCTION = "damage_reduction"  # Damage reduction
    HEAL = "heal"                     # Healing over time
    NEXT_ATTACK = "next_attack"       # Buff for next attack only
    MISS_CHANCE = "miss_chance"       # Chance to miss attacks
    CANT_ATTACK = "cant_attack"       # Cannot attack
    AUTO_DODGE = "auto_dodge"         # Auto dodge attacks
    REFLECTION = "reflection"         # Attacks may hit self
    LOCKED = "locked"                 # Bench card is locked
    GLUTTON = "glutton"               # Skip every other turn
    
    # Priority order (lower = resolves first)
    PRIORITY = {
        "skip_turn": 1,
        "self_damage": 2,
        "stat_modifier": 3,
        "dodge": 4,
        "critical": 5,
        "damage_reduction": 6,
        "heal": 7,
        "next_attack": 8,
        "miss_chance": 9,
        "cant_attack": 10,
        "auto_dodge": 11,
        "reflection": 12,
        "locked": 13,
        "glutton": 14,
    }


@dataclass
class Status:
    """
    Represents a status effect applied to a card.
    
    Attributes:
        name: Display name of the status
        duration: Remaining turns (0 = permanent/until triggered, -1 = permanent)
        effect_type: Type of effect (from EffectType)
        magnitude: Effect strength (percentage or flat value)
        stat_target: Which stat is affected (atk, def, hp, etc.)
        chance: Chance of effect triggering (0-100, default 100)
        stackable: Whether multiple instances can exist
        source: Name of card/ability that applied this status
        stacks: Number of stacks (for auto-dodge counting, etc.)
    """
    name: str
    duration: int
    effect_type: str
    magnitude: float
    stat_target: str = ""
    chance: float = 100.0
    stackable: bool = True
    source: str = ""
    stacks: int = 1
    
    def tick(self) -> bool:
        """
        Reduce duration by 1.
        
        Returns:
            True if status is still active, False if expired
        """
        if self.duration > 0:
            self.duration -= 1
        return self.duration != 0 or self.duration == -1  # -1 = permanent
    
    def is_active(self) -> bool:
        """Check if status is still active."""
        return self.duration != 0
    
    def should_trigger(self) -> bool:
        """Roll to see if effect triggers based on chance."""
        return roll(self.chance)
    
    def copy(self) -> 'Status':
        """Create a copy of this status."""
        return Status(
            name=self.name,
            duration=self.duration,
            effect_type=self.effect_type,
            magnitude=self.magnitude,
            stat_target=self.stat_target,
            chance=self.chance,
            stackable=self.stackable,
            source=self.source,
            stacks=self.stacks
        )


# ============================================
# PREDEFINED STATUS EFFECTS
# ============================================
def create_status(name: str, duration: int = None, source: str = "", magnitude_override: float = None, stacks_override: int = None) -> Status:
    """
    Factory function to create common status effects.
    If duration is not specified, uses the predefined duration for that status.
    """
    statuses = {
        # ============================================
        # SKIP TURN EFFECTS
        # ============================================
        "Sleep": Status(
            name="Sleep",
            duration=1,
            effect_type=EffectType.SKIP_TURN,
            magnitude=100,
            stackable=False
        ),
        "Procrastination": Status(
            name="Procrastination",
            duration=-1,
            effect_type=EffectType.SKIP_TURN,
            magnitude=25,
            chance=25,
            stackable=False
        ),
        "Stunned": Status(
            name="Stunned",
            duration=1,
            effect_type=EffectType.SKIP_TURN,
            magnitude=100,
            stackable=False
        ),
        "Incapacitated": Status(
            name="Incapacitated",
            duration=1,
            effect_type=EffectType.SKIP_TURN,
            magnitude=100,
            stackable=False
        ),
        "Kidnapped": Status(
            name="Kidnapped",
            duration=1,
            effect_type=EffectType.SKIP_TURN,
            magnitude=100,
            stackable=False
        ),
        "Slipped": Status(
            name="Slipped",
            duration=1,
            effect_type=EffectType.SKIP_TURN,
            magnitude=100,
            stackable=False
        ),
        
        # ============================================
        # SELF-DAMAGE EFFECTS (DoT)
        # ============================================
        "Burn": Status(
            name="Burn",
            duration=3,
            effect_type=EffectType.SELF_DAMAGE,
            magnitude=10,
            stackable=True
        ),
        "Poison": Status(
            name="Poison",
            duration=3,
            effect_type=EffectType.SELF_DAMAGE,
            magnitude=5,
            stackable=True
        ),
        "Ragebait": Status(
            name="Ragebait",
            duration=5,
            effect_type=EffectType.SELF_DAMAGE,
            magnitude=5,
            stackable=True
        ),
        "Ricin": Status(
            name="Ricin",
            duration=4,
            effect_type=EffectType.SELF_DAMAGE,
            magnitude=10,
            stackable=True
        ),
        "Bleed": Status(
            name="Bleed",
            duration=2,
            effect_type=EffectType.SELF_DAMAGE,
            magnitude=8,
            stackable=True
        ),
        
        # ============================================
        # STAT MODIFIERS
        # ============================================
        "Enraged": Status(
            name="Enraged",
            duration=3,
            effect_type=EffectType.STAT_MODIFIER,
            magnitude=50,
            stat_target="atk",
            stackable=True
        ),
        "Weakened": Status(
            name="Weakened",
            duration=2,
            effect_type=EffectType.STAT_MODIFIER,
            magnitude=-10,
            stat_target="atk",
            stackable=True
        ),
        "Empowered": Status(
            name="Empowered",
            duration=2,
            effect_type=EffectType.STAT_MODIFIER,
            magnitude=25,
            stat_target="atk",
            stackable=True
        ),
        "Anguish": Status(
            name="Anguish",
            duration=2,
            effect_type=EffectType.STAT_MODIFIER,
            magnitude=-90,
            stat_target="atk",
            stackable=False
        ),
        "Double Stats": Status(
            name="Double Stats",
            duration=-1,
            effect_type=EffectType.STAT_MODIFIER,
            magnitude=100,
            stat_target="all",
            stackable=False
        ),
        "Luv Buff": Status(
            name="Luv Buff",
            duration=-1,
            effect_type=EffectType.STAT_MODIFIER,
            magnitude=25,
            stat_target="all",
            stackable=True
        ),
        
        # ============================================
        # DAMAGE REDUCTION
        # ============================================
        "Shield": Status(
            name="Shield",
            duration=2,
            effect_type=EffectType.DAMAGE_REDUCTION,
            magnitude=25,
            stackable=True
        ),
        "Secret Service": Status(
            name="Secret Service",
            duration=-1,
            effect_type=EffectType.DAMAGE_REDUCTION,
            magnitude=25,
            stackable=False
        ),
        "Alpha": Status(
            name="Alpha",
            duration=-1,
            effect_type=EffectType.DAMAGE_REDUCTION,
            magnitude=25,
            stackable=False
        ),
        "Backboard Shatter": Status(
            name="Backboard Shatter",
            duration=3,
            effect_type=EffectType.DAMAGE_REDUCTION,
            magnitude=50,
            stackable=False
        ),
        "Napoleon": Status(
            name="Napoleon",
            duration=3,
            effect_type=EffectType.DAMAGE_REDUCTION,
            magnitude=80,
            stackable=False
        ),
        "Steph Defense": Status(
            name="Steph Defense",
            duration=-1,
            effect_type=EffectType.DAMAGE_REDUCTION,
            magnitude=33,
            stackable=False
        ),
        "MLK Peace": Status(
            name="MLK Peace",
            duration=-1,
            effect_type=EffectType.DAMAGE_REDUCTION,
            magnitude=80,
            stackable=False
        ),
        "Saddam Shield": Status(
            name="Saddam Shield",
            duration=-1,
            effect_type=EffectType.DAMAGE_REDUCTION,
            magnitude=50,
            stackable=False
        ),
        
        # ============================================
        # DODGE EFFECTS
        # ============================================
        "Evasion": Status(
            name="Evasion",
            duration=2,
            effect_type=EffectType.DODGE,
            magnitude=20,
            stackable=True
        ),
        "Hiding Spot": Status(
            name="Hiding Spot",
            duration=-1,
            effect_type=EffectType.DODGE,
            magnitude=50,
            stackable=False
        ),
        "Jump": Status(
            name="Jump",
            duration=-1,
            effect_type=EffectType.DODGE,
            magnitude=50,
            stackable=False
        ),
        "Monkey Agility": Status(
            name="Monkey Agility",
            duration=-1,
            effect_type=EffectType.DODGE,
            magnitude=20,
            stackable=False
        ),
        "Slipped Dodge": Status(
            name="Slipped Dodge",
            duration=1,
            effect_type=EffectType.DODGE,
            magnitude=25,
            stackable=False
        ),
        "High Dodge": Status(
            name="High Dodge",
            duration=-1,
            effect_type=EffectType.DODGE,
            magnitude=75,
            stackable=False
        ),
        
        # ============================================
        # CRITICAL HIT EFFECTS
        # ============================================
        "Focused": Status(
            name="Focused",
            duration=2,
            effect_type=EffectType.CRITICAL,
            magnitude=25,
            stat_target="crit_chance",
            stackable=True
        ),
        "Debate Crit": Status(
            name="Debate Crit",
            duration=1,
            effect_type=EffectType.CRITICAL,
            magnitude=25,
            stat_target="crit_chance",
            stackable=False
        ),
        "Kobe Crit": Status(
            name="Kobe Crit",
            duration=1,
            effect_type=EffectType.CRITICAL,
            magnitude=44.7,
            stat_target="crit_chance",
            stackable=False
        ),
        "Steph Crit": Status(
            name="Steph Crit",
            duration=1,
            effect_type=EffectType.CRITICAL,
            magnitude=42,
            stat_target="crit_chance",
            stackable=False
        ),
        "Lebron Crit": Status(
            name="Lebron Crit",
            duration=1,
            effect_type=EffectType.CRITICAL,
            magnitude=100,
            stat_target="crit_chance",
            stackable=False
        ),
        
        # ============================================
        # NEXT ATTACK BUFFS
        # ============================================
        "Hockey Stick": Status(
            name="Hockey Stick",
            duration=1,
            effect_type=EffectType.NEXT_ATTACK,
            magnitude=250,
            stat_target="flat_damage",
            stackable=False
        ),
        "Album Drop Buff": Status(
            name="Album Drop Buff",
            duration=1,
            effect_type=EffectType.NEXT_ATTACK,
            magnitude=33,
            stat_target="percent_damage",
            stackable=False
        ),
        "Rough Rider": Status(
            name="Rough Rider",
            duration=1,
            effect_type=EffectType.NEXT_ATTACK,
            magnitude=200,
            stat_target="damage_mult",
            stackable=False
        ),
        "Caffeine": Status(
            name="Caffeine",
            duration=1,
            effect_type=EffectType.NEXT_ATTACK,
            magnitude=2,
            stat_target="coin_mult",
            stackable=False
        ),
        "Cheese Buff": Status(
            name="Cheese Buff",
            duration=1,
            effect_type=EffectType.NEXT_ATTACK,
            magnitude=300,
            stat_target="damage_mult",
            stackable=False
        ),
        
        # ============================================
        # MISS CHANCE EFFECTS
        # ============================================
        "Barked At": Status(
            name="Barked At",
            duration=1,
            effect_type=EffectType.MISS_CHANCE,
            magnitude=33,
            stackable=False
        ),
        "Gooned": Status(
            name="Gooned",
            duration=-1,
            effect_type=EffectType.MISS_CHANCE,
            magnitude=10,
            stackable=True
        ),
        "Asian Blindness": Status(
            name="Asian Blindness",
            duration=-1,
            effect_type=EffectType.MISS_CHANCE,
            magnitude=25,
            stackable=False
        ),
        
        # ============================================
        # CANT ATTACK EFFECTS
        # ============================================
        "Sat On": Status(
            name="Sat On",
            duration=2,
            effect_type=EffectType.CANT_ATTACK,
            magnitude=100,
            stackable=False
        ),
        
        # ============================================
        # AUTO DODGE EFFECTS
        # ============================================
        "Thicc Calves": Status(
            name="Thicc Calves",
            duration=-1,
            effect_type=EffectType.AUTO_DODGE,
            magnitude=100,
            stacks=2,
            stackable=False
        ),
        "Backflip": Status(
            name="Backflip",
            duration=1,
            effect_type=EffectType.HEAL,
            magnitude=300,
            stat_target="overflow",
            stackable=False
        ),
        
        # ============================================
        # REFLECTION EFFECTS
        # ============================================
        "Reflection": Status(
            name="Reflection",
            duration=1,
            effect_type=EffectType.REFLECTION,
            magnitude=50,
            stackable=False
        ),
        
        # ============================================
        # LOCKED EFFECTS (for bench cards)
        # ============================================
        "Called": Status(
            name="Called",
            duration=3,
            effect_type=EffectType.LOCKED,
            magnitude=100,
            stackable=False
        ),
        
        # ============================================
        # GLUTTON EFFECTS
        # ============================================
        "Glutton": Status(
            name="Glutton",
            duration=6,
            effect_type=EffectType.GLUTTON,
            magnitude=100,
            stackable=False
        ),
        
        # ============================================
        # SPECIAL: Cybertruck Shield
        # ============================================
        "Cybertruck": Status(
            name="Cybertruck",
            duration=-1,
            effect_type=EffectType.DAMAGE_REDUCTION,
            magnitude=75,
            stacks=500,
            stackable=False
        ),
        
        # ============================================
        # HEALING
        # ============================================
        "Regeneration": Status(
            name="Regeneration",
            duration=3,
            effect_type=EffectType.HEAL,
            magnitude=5,
            stackable=True
        ),
        
        # ============================================
        # SPECIAL FLAGS
        # ============================================
        "No Crit": Status(
            name="No Crit",
            duration=1,
            effect_type=EffectType.CRITICAL,
            magnitude=-100,
            stat_target="crit_chance",
            stackable=False
        ),
        "Piercing": Status(
            name="Piercing",
            duration=1,
            effect_type=EffectType.STAT_MODIFIER,
            magnitude=0,
            stat_target="pierce",
            stackable=False
        ),
        
        # ============================================
        # TIMER EFFECTS
        # ============================================
        "Beaver Timer": Status(
            name="Beaver Timer",
            duration=2,
            effect_type=EffectType.STAT_MODIFIER,
            magnitude=0,
            stackable=False
        ),
    }
    
    if name in statuses:
        status = statuses[name].copy()
        # Only override duration if explicitly provided
        if duration is not None:
            status.duration = duration
        status.source = source
        if magnitude_override is not None:
            status.magnitude = magnitude_override
        if stacks_override is not None:
            status.stacks = stacks_override
        return status
    
    # Return a generic status if not predefined
    return Status(
        name=name,
        duration=duration if duration is not None else 1,
        effect_type=EffectType.STAT_MODIFIER,
        magnitude=magnitude_override if magnitude_override else 0,
        source=source
    )


class StatusManager:
    """
    Manages status effects for a single card.
    Handles application, removal, and resolution of effects.
    """
    
    def __init__(self):
        self.statuses: list[Status] = []
    
    def add_status(self, status: Status) -> bool:
        """Add a status effect."""
        if not status.stackable:
            for existing in self.statuses:
                if existing.name == status.name:
                    if status.duration > existing.duration:
                        existing.duration = status.duration
                    return False
        
        self.statuses.append(status)
        return True
    
    def remove_status(self, name: str, remove_all: bool = False) -> int:
        """Remove status effect(s) by name."""
        count = 0
        new_list = []
        
        for status in self.statuses:
            if status.name == name:
                if not remove_all and count > 0:
                    new_list.append(status)
                else:
                    count += 1
            else:
                new_list.append(status)
        
        self.statuses = new_list
        return count
    
    def clear_all(self):
        """Remove all status effects."""
        self.statuses = []
    
    def get_by_type(self, effect_type: str) -> list[Status]:
        """Get all statuses of a specific type."""
        return [s for s in self.statuses if s.effect_type == effect_type]
    
    def has_status(self, name: str) -> bool:
        """Check if a specific status exists."""
        return any(s.name == name for s in self.statuses)
    
    def get_status(self, name: str) -> Optional[Status]:
        """Get a specific status by name."""
        for s in self.statuses:
            if s.name == name:
                return s
        return None
    
    def tick_all(self) -> list[Status]:
        """Reduce duration of all statuses and remove expired ones."""
        expired = []
        active = []
        
        for status in self.statuses:
            if status.tick():
                active.append(status)
            else:
                expired.append(status)
        
        self.statuses = active
        return expired
    
    def get_sorted_statuses(self) -> list[Status]:
        """Get statuses sorted by priority for resolution."""
        return sorted(
            self.statuses,
            key=lambda s: EffectType.PRIORITY.get(s.effect_type, 99)
        )
    
    def calculate_total_modifier(self, stat: str) -> float:
        """Calculate total percentage modifier for a stat."""
        total = 0.0
        for status in self.statuses:
            if status.effect_type == EffectType.STAT_MODIFIER:
                if status.stat_target == stat or status.stat_target == "all":
                    total += status.magnitude
        return total
    
    def get_dodge_chance(self) -> float:
        """Get total dodge chance from all dodge effects."""
        total = sum(s.magnitude for s in self.get_by_type(EffectType.DODGE))
        return apply_cap(total, "dodge")
    
    def get_damage_reduction(self) -> float:
        """Get total damage reduction from all reduction effects."""
        total = sum(s.magnitude for s in self.get_by_type(EffectType.DAMAGE_REDUCTION))
        return apply_cap(total, "damage_reduction")
    
    def get_miss_chance(self) -> float:
        """Get total miss chance."""
        total = sum(s.magnitude for s in self.get_by_type(EffectType.MISS_CHANCE))
        return min(total, 90)
    
    def get_crit_modifiers(self) -> tuple[float, float]:
        """Get critical hit modifiers."""
        chance = 0.0
        damage = 0.0
        
        for status in self.get_by_type(EffectType.CRITICAL):
            if status.stat_target == "crit_chance":
                chance += status.magnitude
            elif status.stat_target == "crit_damage":
                damage += status.magnitude
        
        return (chance, min(damage, apply_cap(damage + 200, "critical_multiplier") - 200))
    
    def should_skip_turn(self) -> tuple[bool, str]:
        """Check if turn should be skipped."""
        for status in self.get_by_type(EffectType.SKIP_TURN):
            if status.should_trigger():
                return (True, status.name)
        return (False, "")
    
    def can_attack(self) -> tuple[bool, str]:
        """Check if card can attack."""
        for status in self.get_by_type(EffectType.CANT_ATTACK):
            return (False, status.name)
        return (True, "")
    
    def check_auto_dodge(self) -> bool:
        """Check and consume auto-dodge."""
        for status in self.get_by_type(EffectType.AUTO_DODGE):
            if status.stacks > 0:
                status.stacks -= 1
                if status.stacks <= 0:
                    self.remove_status(status.name)
                return True
        return False
    
    def check_reflection(self) -> bool:
        """Check if attack should be reflected."""
        for status in self.get_by_type(EffectType.REFLECTION):
            if status.should_trigger():
                return True
        return False
    
    def get_next_attack_buffs(self) -> dict:
        """Get all next-attack buffs and remove them."""
        buffs = {
            "flat_damage": 0,
            "percent_damage": 0,
            "damage_mult": 100,
            "coin_mult": 1,
            "crit_mult": 0,
        }
        
        to_remove = []
        for status in self.get_by_type(EffectType.NEXT_ATTACK):
            if status.stat_target == "flat_damage":
                buffs["flat_damage"] += status.magnitude
            elif status.stat_target == "percent_damage":
                buffs["percent_damage"] = max(buffs["percent_damage"], status.magnitude)
            elif status.stat_target == "damage_mult":
                buffs["damage_mult"] = max(buffs["damage_mult"], status.magnitude)
            elif status.stat_target == "coin_mult":
                buffs["coin_mult"] = int(status.magnitude)
            to_remove.append(status.name)
        
        for name in set(to_remove):
            self.remove_status(name)
        
        return buffs
    
    def calculate_self_damage(self, max_hp: int) -> int:
        """Calculate total self-damage from DoT effects."""
        total = 0
        for status in self.get_by_type(EffectType.SELF_DAMAGE):
            damage = int(max_hp * (status.magnitude / 100))
            total += damage
        return total
    
    def calculate_heal(self, max_hp: int, current_hp: int) -> tuple[int, bool]:
        """Calculate total healing from heal effects."""
        total = 0
        can_overflow = False
        
        for status in self.get_by_type(EffectType.HEAL):
            if status.stat_target == "overflow":
                total += int(status.magnitude)
                can_overflow = True
            else:
                heal = int(max_hp * (status.magnitude / 100))
                total += heal
        
        return (total, can_overflow)
    
    def is_locked(self) -> bool:
        """Check if card is locked (for bench cards)."""
        return any(s.effect_type == EffectType.LOCKED for s in self.statuses)
    
    def has_piercing(self) -> bool:
        """Check if card has piercing damage."""
        for s in self.statuses:
            if s.stat_target == "pierce":
                return True
        return False
    
    def get_cybertruck(self) -> Optional[Status]:
        """Get cybertruck status if active."""
        return self.get_status("Cybertruck")
    
    def get_display_list(self) -> list[Status]:
        """Get list of statuses for display."""
        return self.statuses.copy()
