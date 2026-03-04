# Terminal Chaos TCG

A chaotic, fast-paced terminal-based trading card game for 2 players featuring 38 unique custom cards.

## Installation

1. Make sure you have Python 3.10+ installed
2. Clone this repository:
   ```bash
   git clone https://github.com/Coin333/Custom_TCG_Final.git
   cd Custom_TCG_Final
   ```

## How to Play

### Starting the Game

```bash
cd tcg
python3 main.py
```

### Game Objective

Be the first player to reach **25 points** by KO'ing your opponent's cards!

### Setup

1. Each player builds a **10-card deck** from the available card pool
2. Select **1 Active card** and **2 Bench cards** to start
3. Remaining 7 cards form your deck pool (drawn when bench cards are KO'd)

### Turn Structure

1. **Start of Turn** - Status effects resolve (DoT, skip turn checks, etc.)
2. **Action Phase** - Choose to:
   - Use your card's **Ability** (one-time use per card lifetime)
   - This is followed by your regular **Attack**
3. **Combat Resolution** - Damage is calculated with buffs, crits, and reductions
4. **KO Check** - Replace fallen cards from bench/deck

### Deck Building

During deck building, you can:
- **[1-N]** Add cards by number
- **[R]** Remove a card from your deck
- **[A]** Auto-fill remaining slots randomly
- **[Q]** Quick build (random deck)
- **[L]** Quick list - enter card numbers/names separated by commas
  - Example: `1, 5, Noah Tsui, CaseOh`

### Deck Limits by Rarity

| Rarity | Limit | Points when KO'd |
|--------|-------|------------------|
| Ultra Legendary | 1 | 15 |
| Legendary | 2 | 10 |
| Mythical | 2 | 7 |
| Epic | 2 | 5 |
| Rare | 2 | 3 |
| Common | ∞ | 2 |
| Basic | ∞ | 1 |

## Card Mechanics

### Attack Stats
- **Base Damage**: Flat damage dealt
- **% Damage**: Percentage of opponent's MAX HP
- **Crit Chance**: Chance to land a critical hit
- **Crit Multiplier**: Damage multiplier on critical (e.g., 200% = 2x)

### Abilities
- **Active Abilities**: Can be used ONCE per card's lifetime
- **Passive Abilities**: Always active, trigger automatically

### Status Effects
- **Damage Reduction (DR)**: Reduces incoming damage by percentage
- **Dodge**: Chance to completely avoid an attack
- **Skip Turn**: Forces card to skip their turn
- **DoT (Damage over Time)**: Deals damage at start of each turn
- **Miss Chance**: Chance for attacks to miss
- **Auto-Dodge**: Guaranteed dodge for X attacks

## Ultra Legendary Cards

| Card | HP | Special Mechanics |
|------|-----|-------------------|
| **Chinese Beaver** | 999999 | Flips 5 coins, deals 1000 damage per heads. Dies after 2 turns. |
| **Noah Tsui** | 1500 | 50% dodge (Jump) + 25% miss chance (Asian Blindness) + Auto-dodge ability |
| **Colin Sweeney** | 1600 | 50% of enemy MAX HP damage. 25% chance to skip own turn (Procrastination) |
| **Aldo Ortiz** | 1750 | 100x crit damage when HP > 1000. 75% dodge when HP > 1000. Bean Rice Cheese ability. |
| **Hydrogen Bomb** | 1 | Both cards die. Can only be obtained via Coughing Baby transformation. |

## Running Tests

```bash
cd tcg
python3 test_game.py      # Core system tests
python3 test_abilities.py # All ability tests
python3 test_passives.py  # All passive tests
python3 simulate_game.py  # Automated game simulation
```

## File Structure

```
tcg/
├── main.py           # Game entry point
├── engine.py         # Core game loop and combat
├── card.py           # Card class and loading
├── ability_engine.py # All ability/passive handlers
├── status.py         # Status effect system
├── deck_builder.py   # Deck building interface
├── cards.json        # Card definitions
└── utils.py          # Utilities and constants
```

## Tips

- **High rarity ≠ always better** - Lower rarity cards can counter specific strategies
- **Passives are powerful** - Cards like MLK (80% DR) can be hard to kill
- **Abilities don't end your turn** - Use your ability AND attack in the same turn
- **Watch status durations** - Buffs and debuffs expire, plan accordingly
- **Bench matters** - Some abilities target bench cards (Chinese Beaver, Goonicide Guy)

---

*May chaos be ever in your favor.*
