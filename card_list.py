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
    Card(
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
    Card(
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
    Card(
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
    Card(
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
    Card(
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
    Card(
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
    Card(
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
    Card(
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