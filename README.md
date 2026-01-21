# Custom Trading Card Game (CTCG)

A custom-built trading card game written in C++.

## Features

### ✅ Implemented:
- **Card System**: Cards with name, cost, damage, hit points, and abilities
- **Ability System**: Damage, heal, buff, debuff, shield, and special abilities
- **Deck System**: Deck management with shuffling, drawing, and card operations
- **Player System**: Players with health, energy, hand, field, and graveyard
- **Game Engine**: Turn-based game system with turn management and win conditions
- **Combat System**: Card-to-card combat and direct player damage

### Planned:
- Main Menu
- Enhanced Combat System
- More Ability Types
- Card Collection System

## Status
Early development – core game engine and combat system implemented

## Step 1 - Initial Card Development (Week 1)
✅ **Completed:**
- Card class with name, cost, damage, hit points
- Ability system with various effect types
- Deck management (add, remove, shuffle, draw)
- Example card definitions

### Core Components:

#### Card System:
- **Card.h/cpp**: Base card class with combat stats (attack, HP), cost, and abilities
- **Ability.h/cpp**: Ability system with damage, heal, buff, debuff, shield, and special effects
- **Deck.h/cpp**: Deck management with shuffling and card operations
- **card_list.cpp**: Example card definitions (Goblin, Orc Warrior, Dragon, spells)

#### Game System:
- **Player.h/cpp**: Player class managing deck, hand, field, health, and energy
- **GameEngine.h/cpp**: Game engine handling turn management, combat, and win conditions
- **main.cpp**: Example game loop demonstrating gameplay

## Game Mechanics

### Turn Structure:
1. **Start Turn**: Increase energy, draw card, reset attack states
2. **Main Phase**: Play cards, use abilities
3. **Combat Phase**: Attack with creatures
4. **End Turn**: Cleanup and switch players

### Combat:
- Creatures can attack enemy creatures or players directly
- Both creatures deal damage to each other simultaneously
- Dead creatures are moved to graveyard automatically
- Players lose when health reaches 0

### Energy System:
- Players gain +1 max energy each turn (capped at 10)
- Energy resets to max at start of turn
- Cards cost energy to play

## Building

Compile with:
```bash
g++ -std=c++11 -I ctcg/include ctcg/src/*.cpp -o ctcg
```

Run:
```bash
./ctcg
```
