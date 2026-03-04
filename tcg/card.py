"""
Card System for Terminal Chaos TCG
Defines the Card class and card loading from JSON
"""
import json
from dataclasses import dataclass, field
from typing import Optional, Any
from status import StatusManager, Status
from utils import colorize, RARITY_POINTS, RARITY_COLORS, Colors


@dataclass
class AttackData:
    """
    Represents a card's attack properties.
    
    Attributes:
        base_damage: Flat damage amount
        percent_damage: Percentage of opponent's MAX HP
        crit_chance: Base critical hit chance (0-100)
        crit_multiplier: Damage multiplier on crit (e.g., 200 = 2x)
    """
    base_damage: int = 50
    percent_damage: float = 0.0
    crit_chance: float = 10.0
    crit_multiplier: float = 200.0
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AttackData':
        """Create AttackData from dictionary."""
        return cls(
            base_damage=data.get("base_damage", 50),
            percent_damage=data.get("percent_damage", 0.0),
            crit_chance=data.get("crit_chance", 10.0),
            crit_multiplier=data.get("crit_multiplier", 200.0)
        )


@dataclass
class AbilityData:
    """
    Represents a card's ability.
    
    Attributes:
        name: Display name of the ability
        description: Description of what the ability does
        effect_id: Identifier for ability engine to execute
        is_passive: If True, ability is always active
        parameters: Additional parameters for the ability
    """
    name: str = "None"
    description: str = ""
    effect_id: str = "none"
    is_passive: bool = False
    parameters: dict = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AbilityData':
        """Create AbilityData from dictionary."""
        return cls(
            name=data.get("name", "None"),
            description=data.get("description", ""),
            effect_id=data.get("effect_id", "none"),
            is_passive=data.get("is_passive", False),
            parameters=data.get("parameters", {})
        )


class Card:
    """
    Represents a playable card in the game.
    
    Attributes:
        name: Card name
        max_hp: Maximum health points
        current_hp: Current health points
        attack: AttackData object
        rarity: Rarity level
        ability: AbilityData object
        ability_used: Whether active ability has been used
        status_manager: Manages status effects
    """
    
    def __init__(
        self,
        name: str,
        max_hp: int,
        attack: AttackData,
        rarity: str,
        ability: AbilityData
    ):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.attack = attack
        self.rarity = rarity
        self.ability = ability
        self.ability_used = False
        self.status_manager = StatusManager()
        self.passive = None  # Separate passive ability
        self.secondary_passive = None  # For cards with multiple passives
        self.transform_only = False  # If True, card can only be obtained via transformation
        
        # For tracking
        self._original_max_hp = max_hp
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Card':
        """Create a Card from a dictionary (JSON data)."""
        card = cls(
            name=data["name"],
            max_hp=data["max_hp"],
            attack=AttackData.from_dict(data.get("attack", {})),
            rarity=data["rarity"],
            ability=AbilityData.from_dict(data.get("ability", {}))
        )
        # Load passive if present
        if "passive" in data and data["passive"]:
            card.passive = AbilityData.from_dict(data["passive"])
        # Load secondary passive if present
        if "secondary_passive" in data and data["secondary_passive"]:
            card.secondary_passive = AbilityData.from_dict(data["secondary_passive"])
        # Load transform_only flag
        if data.get("transform_only", False):
            card.transform_only = True
        return card
    
    def copy(self) -> 'Card':
        """Create a deep copy of this card (for deck building)."""
        card = Card(
            name=self.name,
            max_hp=self.max_hp,
            attack=AttackData(
                base_damage=self.attack.base_damage,
                percent_damage=self.attack.percent_damage,
                crit_chance=self.attack.crit_chance,
                crit_multiplier=self.attack.crit_multiplier
            ),
            rarity=self.rarity,
            ability=AbilityData(
                name=self.ability.name,
                description=self.ability.description,
                effect_id=self.ability.effect_id,
                is_passive=self.ability.is_passive,
                parameters=self.ability.parameters.copy()
            )
        )
        # Copy passive if present
        if self.passive:
            card.passive = AbilityData(
                name=self.passive.name,
                description=self.passive.description,
                effect_id=self.passive.effect_id,
                is_passive=True,
                parameters=self.passive.parameters.copy() if self.passive.parameters else {}
            )
        if self.secondary_passive:
            card.secondary_passive = AbilityData(
                name=self.secondary_passive.name,
                description=self.secondary_passive.description,
                effect_id=self.secondary_passive.effect_id,
                is_passive=True,
                parameters=self.secondary_passive.parameters.copy() if self.secondary_passive.parameters else {}
            )
        card.transform_only = self.transform_only
        return card
    
    def reset(self):
        """Reset card to initial state (for new game)."""
        self.current_hp = self.max_hp
        self.ability_used = False
        self.status_manager.clear_all()
    
    def is_alive(self) -> bool:
        """Check if card is still alive."""
        return self.current_hp > 0
    
    def take_damage(self, damage: int) -> int:
        """
        Apply damage to this card.
        
        Args:
            damage: Amount of damage to take
            
        Returns:
            Actual damage taken
        """
        actual_damage = min(damage, self.current_hp)
        self.current_hp = max(0, self.current_hp - damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """
        Heal this card.
        
        Args:
            amount: Amount to heal
            
        Returns:
            Actual amount healed
        """
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
    
    def get_attack_damage(self, opponent_max_hp: int = 0) -> int:
        """
        Calculate base attack damage including stat modifiers.
        
        Args:
            opponent_max_hp: Opponent's max HP (for percent damage)
            
        Returns:
            Modified attack damage
        """
        # Start with base damage
        damage = self.attack.base_damage
        
        # Add percentage damage based on opponent's MAX HP
        if self.attack.percent_damage > 0 and opponent_max_hp > 0:
            percent_dmg = int(opponent_max_hp * (self.attack.percent_damage / 100))
            damage += percent_dmg
        
        # Apply ATK modifiers from status effects
        atk_mod = self.status_manager.calculate_total_modifier("atk")
        if atk_mod != 0:
            damage = int(damage * (1 + atk_mod / 100))
        
        return max(0, damage)
    
    def get_defense_modifier(self) -> float:
        """
        Get defense modifier from status effects.
        
        Returns:
            Defense modifier percentage
        """
        return self.status_manager.calculate_total_modifier("def")
    
    def get_point_value(self) -> int:
        """Get point value when this card is KO'd."""
        return RARITY_POINTS.get(self.rarity, 1)
    
    def add_status(self, status: Status) -> bool:
        """Add a status effect to this card."""
        return self.status_manager.add_status(status)
    
    def has_status(self, name: str) -> bool:
        """Check if card has a specific status."""
        return self.status_manager.has_status(name)
    
    def get_colored_name(self) -> str:
        """Get card name with rarity color."""
        return colorize(self.name, self.rarity)
    
    def can_use_ability(self) -> bool:
        """Check if ability can be used."""
        if self.ability.is_passive:
            return False  # Passives don't need activation
        if self.ability.effect_id == "none":
            return False
        return not self.ability_used
    
    def use_ability(self) -> bool:
        """
        Mark ability as used.
        
        Returns:
            True if ability was successfully used, False if already used
        """
        if self.ability_used or self.ability.is_passive:
            return False
        self.ability_used = True
        return True
    
    def get_display_string(self, show_ability: bool = True) -> str:
        """
        Get a formatted display string for this card.
        
        Args:
            show_ability: Whether to include ability info
            
        Returns:
            Formatted card display string
        """
        lines = []
        
        # Name with rarity color
        lines.append(f"{self.get_colored_name()} ({self.rarity})")
        
        # HP
        hp_pct = self.current_hp / self.max_hp if self.max_hp > 0 else 0
        if hp_pct > 0.6:
            hp_color = Colors.SUCCESS
        elif hp_pct > 0.3:
            hp_color = Colors.WARNING
        else:
            hp_color = Colors.ERROR
        lines.append(f"HP: {hp_color}{self.current_hp} / {self.max_hp}{Colors.RESET}")
        
        # Attack info
        atk_str = f"ATK: {self.attack.base_damage}"
        if self.attack.percent_damage > 0:
            atk_str += f" + {self.attack.percent_damage}% Max HP"
        lines.append(atk_str)
        
        # Status effects
        statuses = self.status_manager.get_display_list()
        if statuses:
            status_strs = [f"{s.name}({s.duration})" for s in statuses]
            lines.append(f"Status: {', '.join(status_strs)}")
        else:
            lines.append("Status: None")
        
        # Ability
        if show_ability:
            ability_status = ""
            if self.ability.is_passive:
                ability_status = " [PASSIVE]"
            elif self.ability_used:
                ability_status = " [USED]"
            else:
                ability_status = " [AVAILABLE]"
            lines.append(f"Ability: {self.ability.name}{ability_status}")
            if self.ability.description:
                lines.append(f"  -> {self.ability.description}")
        
        return "\n".join(lines)
    
    def get_summary_string(self) -> str:
        """Get a short summary for deck building."""
        return (
            f"{self.get_colored_name()} | "
            f"HP: {self.max_hp} | "
            f"ATK: {self.attack.base_damage}"
            f"{'+' + str(self.attack.percent_damage) + '%' if self.attack.percent_damage > 0 else ''} | "
            f"Ability: {self.ability.name}"
        )


def load_cards_from_json(filepath: str, include_transform_only: bool = False) -> list[Card]:
    """
    Load all cards from a JSON file.
    
    Args:
        filepath: Path to cards.json
        include_transform_only: If False, excludes cards that can only be obtained via transformation
        
    Returns:
        List of Card objects
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    cards = []
    for card_data in data["cards"]:
        card = Card.from_dict(card_data)
        # Filter out transform-only cards unless explicitly requested
        if not include_transform_only and card.transform_only:
            continue
        cards.append(card)
    
    return cards


def get_cards_by_rarity(cards: list[Card], rarity: str) -> list[Card]:
    """Filter cards by rarity."""
    return [c for c in cards if c.rarity == rarity]


def validate_deck(deck: list[Card]) -> tuple[bool, str]:
    """
    Validate a deck against building rules.
    
    Args:
        deck: List of cards in the deck
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    from utils import RARITY_LIMITS
    
    if len(deck) != 10:
        return (False, f"Deck must contain exactly 10 cards (has {len(deck)})")
    
    # Count cards by rarity
    rarity_counts = {}
    for card in deck:
        rarity_counts[card.rarity] = rarity_counts.get(card.rarity, 0) + 1
    
    # Check limits
    for rarity, count in rarity_counts.items():
        limit = RARITY_LIMITS.get(rarity, float('inf'))
        if count > limit:
            return (False, f"Too many {rarity} cards ({count}/{int(limit)})")
    
    return (True, "")
