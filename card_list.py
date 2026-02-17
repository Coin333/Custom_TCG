import random
import json
import pygame
import os

class Card:
    def __init__(self, name, damage, hp, damage_reduction,traits,dodge,doublehit,truedmg,abilities):
        self.name = name
        self.damage = damage
        self.hp = hp
        self.damage_reduction = damage_reduction
        self.trait_list = traits
        self.dodge = dodge
        self.doublehit = doublehit
        self.truedmg = truedmg
        self.abilities = abilities
        self.set_traits(self.trait_list)
    def set_traits(self,trait_key):
        #use format [short,afam,tall,male,female,chuzz,fat] (t/f)
        self.short = False
        self.tall = False
        self.afam = False
        self.male = False
        self.female = False
        self.chuzz = False
        self.fat = False
        if trait_key[0] == True:
            self.short = True
            self.tall = False
        elif trait_key[2] == True:
            self.tall = True
        if trait_key[1] == True:
            self.afam = True
            self.dodge += .05
        if trait_key[3] == True:
            self.male = True
            self.female = False
        elif trait_key[4] == True:
            self.female = True
            self.male = False
        else:
            self.female = False
            self.male = False
        if trait_key[5] == True:
            self.chuzz = True
            self.doublehit += .10
        if trait_key[6] == True:
            self.fat = True
            self.dodge -= .05

common_cards = {
    "Charlie_Kirk": Card(
    "Charlie Kirk",
    150,               # Attack value
    500,               # HP value
    0,                 # Damage reduction not mentioned
    [False, False, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                 # Dodge not mentioned
    0,                 # Doublehit always 0
    0,                 # Truedmg not mentioned
    {  # New ability format: Critical hit
        "type": "critical",
        "name": "Debate!",
        "chance": 0.25,  # 25% chance to activate
        "multiplier": 5.0  # 5x damage (500% multiplier)
    }
        ),
    "Donald_Trump": Card(
    "Donald Trump",
    125,                # Attack value
    600,                # HP value
    0.25,               # 25% damage reduction from Secret Service Buff
    [False, False, True, True, False, False, True],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                  # Dodge not mentioned
    0,                  # Doublehit always 0
    0,                  # Truedmg not mentioned
    ["Firm Handshake", "ability", 1.0, 0]  # Ability: always activates (100% chance), no damage multiplier since it heals/drains
    # Note: Secret Service Buff also grants a 10% chance every turn to heal back to full health (not included here)
        ),
    "Kanye_West": Card(
    "Kanye West",
    0,                  # Attack is % of opponent’s HP, so raw attack set to 0
    500,                # HP value
    0,                  # Damage reduction not mentioned
    [False, True, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                  # Dodge not mentioned
    0,                  # Doublehit always 0
    0.20,               # True damage = 20% of opponent’s HP
    {  # Transform or boost damage
        "type": "damage_boost",
        "name": "Album Drop",
        "chance": 0.10,
        "boost": 0,  # Will be calculated as % of opponent HP
        "turns": 1
    }
    # Combo Ability activates only if Drake is in play (not implemented here)
        ),
    "Kobe_Bryant": Card(
    "Kobe Bryant",
    500,               # Attack value
    350,               # HP value
    0,                 # Damage reduction not mentioned
    [False, True, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                 # Dodge not mentioned
    0,                 # Doublehit always 0
    0,                 # Truedmg not mentioned
    {  # Critical hit
        "type": "critical",
        "name": "Kobe Fadeaway",
        "chance": 0.447,
        "multiplier": 1.5
    }
        ),
    "Shaq": Card(
    "Shaq",
    300,               # Attack value
    900,               # HP value
    0,                 # Damage reduction (not passive, it’s a temporary buff from ability)
    [False, True, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                 # Dodge not mentioned
    0,                 # Doublehit always 0
    0,                 # Truedmg not mentioned
    {  # Defense boost
        "type": "defense",
        "name": "Backboard Shatter",
        "chance": 1.0,
        "value": 0.50,
        "target": "self",
        "turns": 3
    }
        ),
    "Burger_King_Guy": Card(
    "Burger King Guy",
    500,               # Attack value
    500,               # HP value
    0,                 # Damage reduction not mentioned
    [False, False, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                 # Dodge not mentioned
    0,                 # Doublehit always 0
    0,                 # Truedmg not mentioned
    {  # Poison effect
        "type": "poison",
        "name": "Slur",
        "chance": 1.0,
        "turns": 5,
        "amount": 25  # 5% of 500 HP = 25 per turn
    }
        ),
    "Coughing_Baby": Card(
    "Coughing Baby",
    50,                # Attack value
    10,                # HP value
    0,                 # Damage reduction not mentioned
    [False, False, False, False, False, False, False],  # Traits: none
    0,                 # Dodge not mentioned
    0,                 # Doublehit always 0
    0,                 # Truedmg not mentioned
    {  # Low chance critical (coin flip mechanic)
        "type": "critical",
        "name": "Cough",
        "chance": 0.125,
        "multiplier": 3.0  # Significant damage if it hits
    }
        ),
    "George_Floyd": Card(
    "George Floyd",
    200,               # Base attack value
    300,               # HP value
    0,                 # Damage reduction not mentioned
    [False, True, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                 # Dodge not mentioned
    0,                 # Doublehit always 0
    0,                 # Truedmg not mentioned
    {  # Damage boost
        "type": "damage_boost",
        "name": "Floyd's Revenge",
        "chance": 1.0,
        "boost": 800,
        "turns": -1  # Permanent
    }
        )
}
rare_cards = {
    "Steph_Curry": Card(
	"Steph Curry",
	600,               # Attack value
	300,               # HP value
	0.33,              # 33% damage reduction
	[False, True, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Critical hit
		"type": "critical",
		"name": "3 Point Blick",
		"chance": 0.42,
		"multiplier": 2.5
	}
		),
    "IShowSpeed": Card(
	"IShowSpeed",
	250,               # Attack value
	500,               # HP value
	0,                 # Damage reduction not mentioned
	[False, True, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Heal with chance
		"type": "heal",
		"name": "Bark",
		"chance": 0.25,  # 25% chance to heal
		"amount": 300,
		"target": "self"
	}
		),
    "Hungryhungryhanny": Card(
	"Hungryhungryhanny",
	250,               # Attack value
	400,               # HP value
	0,                 # Damage reduction not mentioned
	[False, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Critical hit
		"type": "critical",
		"name": "Lebron Scream",
		"chance": 0.25,
		"multiplier": 10.0
	}
		),
    "Goonicide_Guy": Card(
	"Goonicide Guy",
	400,               # Attack value
	800,               # HP value
	0,                 # Damage reduction not mentioned
	[False, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Flat damage + miss chance
		"type": "flat_damage",
		"name": "Goon-akaze",
		"chance": 1.0,
		"damage": 1000
	}
		),
    "NPC": Card(
	"NPC",
	250,               # Attack value
	750,               # HP value
	0,                 # Damage reduction not mentioned
	[True, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Stat buff + turn skip self
		"type": "stat_buff",
		"name": "Mask Removal",
		"chance": 1.0,
		"stat": "damage",
		"value": 1.0,  # Double damage
		"target": "self",
		"turns": -1
	}
		),
    "Elon_Musk": Card(
	"Elon Musk",
	300,               # Attack value
	750,               # HP value
	0.25,              # 25% damage reduction when in Cybertruck (conditional)
	[False, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Defense boost
		"type": "defense",
		"name": "Cybertruck Defense",
		"chance": 1.0,
		"value": 0.75,
		"target": "self",
		"turns": -1
	}
		),
}
epic_cards = {
    "Badland_Chugs": Card(
	"Badland Chugs",
	500,               # Attack value
	1600,              # HP value
	0,                 # Damage reduction not mentioned (temporary 95% reduction from ability)
	[False, False, False, True, False, True, True],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Full heal + defense
		"type": "full_heal",
		"name": "Chug Fest",
		"chance": 1.0,
		"max_hp": 1600,
		"target": "self",
		"defense_boost": 0.95,
		"defense_turns": 1
	}
		),
   "John_Pork": Card(
	"John Pork",
	50,                # Attack value
	1000,              # HP value
	0,                 # Damage reduction not mentioned
	[False, False, False, True, False, False, True],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Turn skip (simplified as opponent skip)
		"type": "turn_skip",
		"name": "John Pork is calling",
		"chance": 1.0,
		"turns": 1
	}
		),
    "Xi_Jinping": Card(
	"Xi Jinping",
	400,               # Attack value
	650,               # HP value
	0,                 # Damage reduction not mentioned
	[False, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Stat debuff (simplified)
		"type": "stat_debuff",
		"name": "Dictatorship",
		"chance": 1.0,
		"stat": "damage",
		"value": 0.20,
		"turns": 2
	}
		),
    "El_Primo": Card(
	"El Primo",
	800,               # Attack value
	800,               # HP value
	0,                 # Damage reduction not mentioned
	[False, False, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Poison
		"type": "poison",
		"name": "El Primoooo",
		"chance": 1.0,
		"turns": 4,
		"amount": 200
	}
		),
    "Lil_Uzi_Vert": Card(
	"Lil Uzi Vert",
	250,               # Attack value
	600,               # HP value
	0,                 # Damage reduction not mentioned
	[True, True, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Stat buff (self, since bench not implemented)
		"type": "stat_buff",
		"name": "Luv is Rage",
		"chance": 1.0,
		"stat": "damage",
		"value": 0.25,
		"target": "self",
		"turns": -1
	}
		),
    "Erica_Kirk": Card(
	"Erica Kirk",
	350,               # Attack value
	1400,              # HP value
	0,                 # Damage reduction not mentioned
	[False, False, False, False, True, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Self hit
		"type": "self_hit",
		"name": "We Are Charlie Kirk",
		"chance": 0.5,
		"value": 1.0,  # 100% chance to hit self when active
		"turns": 1
	}
		),
    "Bruce_Lee": Card(
	"Bruce Lee",
	1000,              # Attack value
	800,               # HP value
	0,                 # Damage reduction not mentioned
	[False, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Conditional critical
		"type": "conditional_critical",
		"name": "1 Inch Punch",
		"chance": 1.0,
		"multiplier": 1.5,
		"condition": {"trait": "short", "value": True},
		"fallback_multiplier": 1.25
	}
		),
    "Andrew_Tate": Card(
	"Andrew Tate",
	0,                 # No direct damage; attack is a Bugatti color roll mechanic
	1000,              # HP value
	0.25,              # 25% damage reduction (Alpha Male)
	[False, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	{  # Convert
		"type": "convert",
		"name": "What color's your Bugatti?",
		"chance": 0.333,
		"value": 1.0  # If activates, always converts
	}
		)
}
mythic_cards = {
    "Ye": Card(
	"Ye",
	400,               # Base attack, pierces damage reduction
	800,               # HP value
	0,                 # No damage reduction mentioned
	[False, True, False, True, False, False, False],  # short, african american, tall, male, female, chuzz, fat
	0,
	0,
	0,
	{  # Critical hit
		"type": "critical",
		"name": "Bipolar Disorder",
		"chance": 0.05,
		"multiplier": 2.0
	}
		),
    "OJ_Simpson": Card(
	"OJ Simpson",
	0,                 # Attack not specified
	0,                 # HP not specified
	0,
	[False, True, False, True, False, False, False],
	0,
	0,
	0,
	{  # Block
		"type": "block",
		"name": "Glove don't fit",
		"chance": 1.0,
		"attacks": 1
	}
		),
    "Ezra_Roberts": Card(
	"Ezra Roberts",
	0,                 # Attack not specified
	0,                 # HP not specified
	0,
	[False, False, True, True, False, False, False],
	0,
	0,
	0,
	{  # Heal (simplified)
		"type": "heal",
		"name": "Recycle",
		"chance": 1.0,
		"amount": 200,
		"target": "self"
	}
		),
    "MLK": Card(
	"MLK",
	100,               # Attack heals 40 HP
	400,               # HP value
	0.8,               # 80% damage reduction
	[True, True, False, True, False, False, False],
	0,
	0,
	0,
	{  # Heal
		"type": "heal",
		"name": "Freedom Speech",
		"chance": 1.0,
		"amount": 200,
		"target": "self"
	}
		),
    "Pablo_Escobar": Card(
	"Pablo Escobar",
	500,               # Base attack
	400,               # HP value
	0,
	[True, False, False, True, False, False, False],
	0,
	0,
	0,
	{  # Critical hit
		"type": "critical",
		"name": "Cartel Smuggle",
		"chance": 0.5,
		"multiplier": 3.0
	}
		),
    "Diddy": Card(
	"Diddy",
	900,
	450,
	0,
	[False, True, False, True, False, False, False],
	0,
	0,
	0,
	{  # Stat debuff (simplified)
		"type": "stat_debuff",
		"name": "Diddle",
		"chance": 1.0,
		"stat": "damage",
		"value": 0.15,
		"turns": 2
	}
		),
    "Kim_Jong-Un": Card(
	"Kim Jong-Un",
	0,                 # No flat damage
	3000,
	0,
	[False, False, False, True, False, False, True],
	0,
	0,
	0.9,               # 90% HP true damage
	{  # Percentage damage (very low chance)
		"type": "percentage_damage",
		"name": "Missile Launch",
		"chance": 0.05,
		"percentage": 0.50  # 50% of HP if hits
	}
		),
    "Saddam_Hussein": Card(
	"Saddam Hussein",
	350,
	500,
	0.5,               # 50% damage reduction
	[False, False, False, True, False, False, False],
	0.5,               # 50% less chance to get hit
	0,
	0,
	{  # Dodge buff
		"type": "dodge_buff",
		"name": "Hiding Spot",
		"chance": 1.0,
		"attacks": 2
	}
		),
    "Theodore_Roosevelt": Card(
	"Theodore Roosevelt",
	600,
	1500,
	0,
	[False, False, False, True, False, False, False],
	0,
	0,
	0,
	{  # Conditional critical
		"type": "conditional_critical",
		"name": "Rough Rider Charge",
		"chance": 1.0,
		"multiplier": 2.0,
		"condition": {"trait": "tall", "value": True},
		"fallback_multiplier": 2.0  # Still 2x even if not tall
	}
		),
    "Gorlock_the_Destroyer": Card(
	"Gorlock the Destroyer",
	200,
	5000,
	0,
	[False, False, False, False, True, True, True],
	0,
	0,
	0,
	{  # Full heal + defense
		"type": "full_heal",
		"name": "Dominion Expansion",
		"chance": 1.0,
		"max_hp": 5000,
		"target": "self"
	}
		)
}
legendary_cards = {
    "Lebron_James": Card(
	"Lebron James",
	500,
	2500,
	0,
	[False, True, True, True, False, False, False],  # tall, african american, male
	0,
	0,
	0,
	{  # Block
		"type": "block",
		"name": "Chase Down Block",
		"chance": 1.0,
		"attacks": 1
	}
		),
    "Jeffrey_Epstein": Card(
	"Jeffrey Epstein",
	800,
	1300,
	0,
	[False, False, False, True, False, False, False],
	0,
	0,
	0,
	{  # Turn skip
		"type": "turn_skip",
		"name": "Kidnap",
		"chance": 0.5,
		"turns": 1
	}
		),
    "Barack_Obama": Card(
	"Barack Obama",
	900,
	1000,
	0,
	[False, True, False, True, False, False, False],
	0,
	0,
	0.10,              # 10% HP true damage from drones
	{  # Percentage damage
		"type": "percentage_damage",
		"name": "Drone Strike",
		"chance": 0.10,
		"percentage": 0.20  # 20% of HP
	}
		),
    "Mr._Michaelsen": Card(
	"Mr. Michaelsen",
	650,               # Average of 600–700
	2000,
	0,
	[False, False, True, True, False, False, False],
	0,
	0,
	0,
	{  # Defense boost
		"type": "defense",
		"name": "AP Euro Flashcards",
		"chance": 1.0,
		"value": 0.80,
		"target": "self",
		"turns": 3
	}
		),
    "Walter_White": Card(
	"Walter White",
	1500,
	250,
	0,
	[False, False, False, True, False, False, False],
	0,
	0,
	0.10,              # Ricin drains 10% HP per turn
	{  # Poison (% of HP)
		"type": "poison",
		"name": "Ricin",
		"chance": 1.0,
		"turns": 4,
		"amount": 0,
		"percentage": 0.10  # 10% of HP per turn
	}
		),
    "CaseOh": Card(
	"CaseOh",
	750,
	2500,
	0,
	[False, False, False, True, False, False, True],
	0,
	0,
	0,
	{  # Turn skip + conditional critical
		"type": "turn_skip",
		"name": "Sit on u",
		"chance": 1.0,
		"turns": 2
	}
		),
    "Monkey": Card(
	"Monkey",
	1000,
	500,
	0,
	[False, True, False, True, False, False, False],
	0.20,              # 20% dodge chance
	0,
	0,
	{  # Stat debuff (conditional)
		"type": "stat_debuff",
		"name": "Banana Slimer",
		"chance": 1.0,
		"stat": "damage",
		"value": 0.90,
		"turns": 2
	}
		)
}
ult_legendary_cards = {
    "Hydrogen_Bomb": Card(
	"Hydrogen Bomb",
	0,                 # No flat damage
	1,                 # HP value
	0,
	[False, False, False, False, False, False, False],  # No traits
	0,
	0,
	1.0,               # 100% HP true damage
	{  # Mutual destruction
		"type": "mutual_destruction",
		"name": "Nuclear Strike",
		"chance": 1.0
	}
		),
    "Beaver": Card(
	"Beaver",
	0,                 # Attack determined by coin flips
	0,                 # HP lasts 2 turns then leaves (not numeric)
	0,
	[False, False, False, False, False, False, False],
	0,
	0,
	0,
	{  # Flat damage (coin flip mechanic)
		"type": "flat_damage",
		"name": "Take that wood",
		"chance": 1.0,
		"damage": 1000  # Simplified - would be per coin flip
	}
		),
    "Noah_Tsui": Card(
	"Noah Tsui",
	[67,6700],              # Midpoint of 67–6700
	1500,
	0,
	[True, False, False, True, False, False, False],
	0.50,              # 50% chance to jump over attacks
	0,
	0,
	{  # Dodge buff
		"type": "dodge_buff",
		"name": "Busty Calves",
		"chance": 1.0,
		"attacks": 2
	}
		),
# Passive: Asian Blindness — 25% chance to miss attacks,
    "Colin_Sweeney": Card(
	"Colin Sweeney",
	0,                 # Coin-flip based attack
	1600,
	0,
	[False, False, False, True, False, False, False],
	0,
	0,
	0.67,              # Heads: deals 67% opponent HP; tails heals 25%
	{  # Stat buff (simplified as damage boost)
		"type": "damage_boost",
		"name": "Caffeine Gum",
		"chance": 1.0,
		"boost": 100,
		"turns": 1
	}
		),
# Passive: Procrastination — 25% chance to skip next turn,
    "Aldo_Ortiz": Card(
	"Aldo Ortiz",
	67,                # Base attack
	1750,
	0,
	[False, False, False, True, False, False, False],
	0.75,              # 75% dodge when above 1000 HP
	0,
	0,
	{  # Conditional critical (when above 1000 HP)
		"type": "critical",
		"name": "Massive Critical",
		"chance": 1.0,
		"multiplier": 100.0
	}
		)
# Passive: Deportation — 25% chance to be detained for 1 turn; dodge reduced to 25% and crit disabled
}

def DealDamage(attacker, defender, amount=None):
    """
    Calculate and deal damage from attacker to defender.
    Handles dodge, damage reduction, true damage, and abilities.
    Returns actual damage dealt.
    """
    if amount is None:
        amount = attacker.damage
    
    # Handle special damage types (list-based, etc.)
    if isinstance(amount, list):
        # For cards like Noah_Tsui with range [min, max]
        amount = random.randint(amount[0], amount[1])
    elif amount == 0 and attacker.truedmg == 0:
        # Some cards have 0 base damage but deal %HP (handled by truedmg)
        # If both are 0, deal minimal damage
        amount = 1
    
    # Check for dodge
    if random.random() < defender.dodge:
        return 0  # Dodged!
    
    # Apply true damage (bypasses damage reduction)
    true_dmg = 0
    if attacker.truedmg > 0:
        true_dmg = defender.hp * attacker.truedmg
    
    # Apply regular damage with reduction
    regular_dmg = amount
    if regular_dmg > 0 and defender.damage_reduction > 0:
        regular_dmg = amount * (1 - defender.damage_reduction)
    
    # Check for double hit
    total_dmg = regular_dmg + true_dmg
    if attacker.doublehit > 0 and random.random() < attacker.doublehit:
        total_dmg *= 2
    
    # Apply damage
    actual_dmg = min(total_dmg, defender.hp)
    defender.hp -= actual_dmg
    
    return actual_dmg

def Statmod(card, stat_type, value, duration=0):
    """
    Modify card stats temporarily or permanently.
    stat_type: 'damage', 'hp', 'dodge', 'damage_reduction', 'doublehit'
    duration: 0 = permanent, >0 = number of turns
    """
    if stat_type == 'damage':
        card.damage += value
    elif stat_type == 'hp':
        card.hp += value
    elif stat_type == 'dodge':
        card.dodge = max(0, min(1, card.dodge + value))
    elif stat_type == 'damage_reduction':
        card.damage_reduction = max(0, min(1, card.damage_reduction + value))
    elif stat_type == 'doublehit':
        card.doublehit = max(0, min(1, card.doublehit + value))
    
    return duration  # Return duration for tracking