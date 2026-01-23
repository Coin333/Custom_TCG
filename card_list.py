import random
import json
import pygame
import os
import game

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
    "Charlie Kirk": Card(
    "Charlie Kirk",
    150,               # Attack value
    500,               # HP value
    0,                 # Damage reduction not mentioned
    [False, False, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                 # Dodge not mentioned
    0,                 # Doublehit always 0
    0,                 # Truedmg not mentioned
    ["Debate!", "ability", 0.25, 5.0]  # Ability: 25% chance to inflict critical damage (500% multiplier)
        ),
    "Donald Trump": Card(
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
    "Kanye West": Card(
    "Kanye West",
    0,                  # Attack is % of opponent’s HP, so raw attack set to 0
    500,                # HP value
    0,                  # Damage reduction not mentioned
    [False, True, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                  # Dodge not mentioned
    0,                  # Doublehit always 0
    0.20,               # True damage = 20% of opponent’s HP
    ["Album Drop", "ability", 0.10, 0]  # 10% chance to transform (no damage multiplier specified)
    # Note: If Album Drop unsuccessful, boosts next attack damage to 33% of opponent’s HP
    # Combo Ability activates only if Drake is in play (not implemented here)
        ),
    "Kobe Bryant": Card(
    "Kobe Bryant",
    500,               # Attack value
    350,               # HP value
    0,                 # Damage reduction not mentioned
    [False, True, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                 # Dodge not mentioned
    0,                 # Doublehit always 0
    0,                 # Truedmg not mentioned
    ["Kobe Fadeaway", "ability", 0.447, 1.5]  # Ability: 44.7% chance to deal 150% damage
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
    ["Backboard Shatter", "ability", 1.0, 0]  # Ability: grants 50% damage reduction for 3 turns (effect not modeled here)
        ),
    "Burger King Guy": Card(
    "Burger King Guy",
    500,               # Attack value
    500,               # HP value
    0,                 # Damage reduction not mentioned
    [False, False, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                 # Dodge not mentioned
    0,                 # Doublehit always 0
    0,                 # Truedmg not mentioned
    ["Slur", "ability", 1.0, 0]  # Ability: always activates, deals ragebait damage, saps 5% enemy health for 5 turns (effect not fully modeled)
        ),
    "Coughing Baby": Card(
    "Coughing Baby",
    50,                # Attack value
    10,                # HP value
    0,                 # Damage reduction not mentioned
    [False, False, False, False, False, False, False],  # Traits: none
    0,                 # Dodge not mentioned
    0,                 # Doublehit always 0
    0,                 # Truedmg not mentioned
    ["Cough", "ability", 0.125, 0]  # Ability: flip 3 coins, 1/8 chance all same face (0.125), no damage multiplier
        ),
    "George Floyd": Card(
    "George Floyd",
    200,               # Base attack value
    300,               # HP value
    0,                 # Damage reduction not mentioned
    [False, True, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
    0,                 # Dodge not mentioned
    0,                 # Doublehit always 0
    0,                 # Truedmg not mentioned
    ["Floyd’s Revenge", "ability", 1.0, 0]  # Ability: applies “Asphyxiation” (enables +800 attack condition)
    # Note: Attack increases by +800 if "Asphyxiation" is applied (not modeled here)
        )
}
rare_cards = {
    "Steph Curry": Card(
	"Steph Curry",
	600,               # Attack value
	300,               # HP value
	0.33,              # 33% damage reduction
	[False, True, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	["3 Point Blick", "ability", 0.42, 2.5]  # Ability: 42% chance to shoot critical (250% damage)
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
	["Bark", "ability", 1.0, 0]  # Ability: always activates, details: 25% chance to backflip heal 300 HP (not modeled here)
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
	["Lebron Scream", "ability", 0.25, 10.0]  # Ability: flip 2 coins (1/4 chance), critical 1000% damage next turn
		),
    "Goonicide guy": Card(
	"Goonicide guy",
	400,               # Attack value
	800,               # HP value
	0,                 # Damage reduction not mentioned
	[False, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	["Goon-akaze", "ability", 1.0, 0]  # Ability: deals 1,000 damage to one card; slows all bench cards and 25% permanent miss chance (effects not modeled)
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
	["Mask Removal", "ability", 1.0, 0]  # Ability: doubles all stats permanently, incapacitates for 1 turn (effects not modeled)
		),
    "Elon Musk": Card(
	"Elon Musk",
	300,               # Attack value
	750,               # HP value
	0.25,              # 25% damage reduction when in Cybertruck (conditional)
	[False, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	["Cybertruck Defense", "ability", 1.0, 0]  # Ability: reduces incoming damage by 75% unless “Sledgehammer” in play (effect not modeled)
		),
}
epic_cards = {
    "Badland Chugs": Card(
	"Badland Chugs",
	500,               # Attack value
	1600,              # HP value
	0,                 # Damage reduction not mentioned (temporary 95% reduction from ability)
	[False, False, False, True, False, True, True],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	["Chug Fest", "ability", 1.0, 0]  # Ability: heals to full HP and grants 95% damage reduction for 1 turn (effect not modeled)
		),
   "John Pork": Card(
	"John Pork",
	50,                # Attack value
	1000,              # HP value
	0,                 # Damage reduction not mentioned
	[False, False, False, True, False, False, True],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	["John Pork is calling", "ability", 1.0, 0]  # Ability: disables a bench card from being played for 3 turns (effect not modeled)
		),
    "Xi Jinping": Card(
	"Xi Jinping",
	400,               # Attack value
	650,               # HP value
	0,                 # Damage reduction not mentioned
	[False, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	["Dictatorship", "ability", 1.0, 0]  # Ability: details not specified
		),
    "El Primo": Card(
	"El Primo",
	800,               # Attack value
	800,               # HP value
	0,                 # Damage reduction not mentioned
	[False, False, True, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	["El Primoooo", "ability", 1.0, 0]  # Ability: deals 200 burn damage per turn for 4 turns (effect not modeled)
		),
    "Lil Uzi Vert": Card(
	"Lil Uzi Vert",
	250,               # Attack value
	600,               # HP value
	0,                 # Damage reduction not mentioned
	[True, True, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	["Luv is Rage", "ability", 1.0, 0]  # Ability: buffs stats of all bench cards by 25% permanently (effect not modeled)
		),
    "Erica Kirk": Card(
	"Erica Kirk",
	350,               # Attack value
	1400,              # HP value
	0,                 # Damage reduction not mentioned
	[False, False, False, False, True, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	["We Are Charlie Kirk", "ability", 0.5, 0]  # Ability: 50% chance opponent’s next attack hits themselves
		),
    "Bruce Lee": Card(
	"Bruce Lee",
	1000,              # Attack value
	800,               # HP value
	0,                 # Damage reduction not mentioned
	[False, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	["1 Inch Punch", "ability", 1.0, 1.5]  # Ability: 1.5x damage if opponent short, else 1.25x (1.25x not modeled here)
		),
    "Andrew Tate": Card(
	"Andrew Tate",
	0,                 # No direct damage; attack is a Bugatti color roll mechanic
	1000,              # HP value
	0.25,              # 25% damage reduction (Alpha Male)
	[False, False, False, True, False, False, False],  # Traits: short, african american, tall, male, female, chuzz, fat
	0,                 # Dodge not mentioned
	0,                 # Doublehit always 0
	0,                 # Truedmg not mentioned
	["What color’s your Bugatti?", "ability", 0.333, 0]  # 1/3 chance colors match → opponent card joins your team
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
	["Bipolar Disorder", "ability", 0.05, 2.0]  # 5% revert to Kanye; coin flip double damage (2x)
		),
    "OJ Simpson": Card(
	"OJ Simpson",
	0,                 # Attack not specified
	0,                 # HP not specified
	0,
	[False, True, False, True, False, False, False],
	0,
	0,
	0,
	["Glove don’t fit", "ability", 1.0, 0]  # Nullifies next attack
		),
    "Ezra Roberts": Card(
	"Ezra Roberts",
	0,                 # Attack not specified
	0,                 # HP not specified
	0,
	[False, False, True, True, False, False, False],
	0,
	0,
	0,
	["Recycle", "ability", 1.0, 0]  # Effect not specified
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
	["Freedom Speech", "ability", 1.0, 0]  # Heals 200 HP if another African American card is in play
		),
    "Pablo Escobar": Card(
	"Pablo Escobar",
	500,               # Base attack
	400,               # HP value
	0,
	[True, False, False, True, False, False, False],
	0,
	0,
	0,
	["Cartel Smuggle", "ability", 0.5, 3.0]  # Coin flip: 3x damage if heads
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
	["Diddle", "ability", 1.0, 0]  # Ability details not specified
		),
    "Kim Jong-Un": Card(
	"Kim Jong-Un",
	0,                 # No flat damage
	3000,
	0,
	[False, False, False, True, False, False, True],
	0,
	0,
	0.9,               # 90% HP true damage
	["Missile Launch", "ability", 0.05, 0]  # 5% chance to hit, otherwise false alarm
		),
    "Saddam Hussein": Card(
	"Saddam Hussein",
	350,
	500,
	0.5,               # 50% damage reduction
	[False, False, False, True, False, False, False],
	0.5,               # 50% less chance to get hit
	0,
	0,
	["Hiding Spot", "ability", 1.0, 0]
		),
    "Theodore Roosevelt": Card(
	"Theodore Roosevelt",
	600,
	1500,
	0,
	[False, False, False, True, False, False, False],
	0,
	0,
	0,
	["Rough Rider Charge", "ability", 1.0, 2.0]  # Double damage next turn; also 2x vs tall opponents
		),
    "Gorlock the Destroyer": Card(
	"Gorlock the Destroyer",
	200,
	5000,
	0,
	[False, False, False, False, True, True, True],
	0,
	0,
	0,
	["Dominion Expansion", "ability", 1.0, 0]  # Absorbs all damage even from bench, heals 50%
		)
}
legendary_cards = {
    "Lebron James": Card(
	"Lebron James",
	500,
	2500,
	0,
	[False, True, True, True, False, False, False],  # tall, african american, male
	0,
	0,
	0,
	["Chase Down Block", "ability", 1.0, 0]  # Ability details not specified
		),
    "Jeffrey Epstein": Card(
	"Jeffrey Epstein",
	800,
	1300,
	0,
	[False, False, False, True, False, False, False],
	0,
	0,
	0,
	["Kidnap", "ability", 0.5, 0]  # 50% chance to skip opponent’s next turn
		),
    "Barack Obama": Card(
	"Barack Obama",
	900,
	1000,
	0,
	[False, True, False, True, False, False, False],
	0,
	0,
	0.10,              # 10% HP true damage from drones
	["Drone Strike", "ability", 0.10, 0]  # 10% chance to summon drones hitting all opponent cards
		),
    "Mr. Michaelsen": Card(
	"Mr. Michaelsen",
	650,               # Average of 600–700
	2000,
	0,
	[False, False, True, True, False, False, False],
	0,
	0,
	0,
	["AP Euro Flashcards", "ability", 1.0, 0]  # If opponent answers wrong, gains 80% DR for 3 turns
		),
    "Walter White": Card(
	"Walter White",
	1500,
	250,
	0,
	[False, False, False, True, False, False, False],
	0,
	0,
	0.10,              # Ricin drains 10% HP per turn
	["Ricin", "ability", 1.0, 0]  # Chosen card loses 10% HP for 4 turns
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
	["Sit on u", "ability", 1.0, 2.0]  # Opponent cannot attack for 2 turns; 2x damage if opponent not tall
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
	["Banana Slimer", "ability", 1.0, 0]  # If opponent male, inflicts anguish (-90% attack for 2 turns)
		)
}
ult_legendary_cards = {
    "Hydrogen Bomb": Card(
	"Hydrogen Bomb",
	0,                 # No flat damage
	1,                 # HP value
	0,
	[False, False, False, False, False, False, False],  # No traits
	0,
	0,
	1.0,               # 100% HP true damage
	["Nuclear Strike", "ability", 1.0, 0]  # On attack both cards die; always goes first
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
	["Take that wood", "ability", 1.0, 1.0]  # Flip 5 coins, 1000 damage per heads; feeds 33% gauge to opponent
		),
    "Noah Tsui": Card(
	"Noah Tsui",
	[67,6700],              # Midpoint of 67–6700
	1500,
	0,
	[True, False, False, True, False, False, False],
	0.50,              # 50% chance to jump over attacks
	0,
	0,
	["Busty Calves", "ability", 1.0, 0]  # Auto-dodges next 2 attacks
		),
# Passive: Asian Blindness — 25% chance to miss attacks,
    "Colin Sweeney": Card(
	"Colin Sweeney",
	0,                 # Coin-flip based attack
	1600,
	0,
	[False, False, False, True, False, False, False],
	0,
	0,
	0.67,              # Heads: deals 67% opponent HP; tails heals 25%
	["Caffeine Gum", "ability", 1.0, 0]  # Next turn doubles number of coin flips
		),
# Passive: Procrastination — 25% chance to skip next turn,
    "Aldo Ortiz": Card(
	"Aldo Ortiz",
	67,                # Base attack
	1750,
	0,
	[False, False, False, True, False, False, False],
	0.75,              # 75% dodge when above 1000 HP
	0,
	0,
	["", "ability", 1.0, 100.0]  # Critical 10000% (100x) when above 1000 HP
		)
# Passive: Deportation — 25% chance to be detained for 1 turn; dodge reduced to 25% and crit disabled
}