# Terminal Chaos TCG

A chaotic, fast-paced terminal-based trading card game for 2 players.

## Quick Start

```bash
cd tcg
python3 main.py
```

## Game Overview

- **Players:** 2 (shared console)
- **Deck Size:** 10 cards per player
- **Win Condition:** First to 25 points wins
- **Game Style:** Fast, random, chaotic!

## How to Play

### Setup
1. Each player builds a 10-card deck from the card pool
2. Select 1 Active card and 2 Bench cards
3. Coin flip determines who goes first

### Turn Structure
1. **Start Turn** - Status effects resolve (DoT, healing, skip checks)
2. **Action Phase** - Choose to Attack OR use Ability
3. **Combat Resolution** - Damage is calculated and applied
4. **KO Check** - Replace fallen cards, score points

### Scoring
When you KO an opponent's card, you score points based on its rarity:
- Basic: 1 point
- Common: 2 points
- Rare: 3 points
- Epic: 5 points
- Mythical: 7 points
- Legendary: 10 points
- Ultra Legendary: 15 points

### Deck Building Limits
| Rarity | Max Allowed |
|--------|-------------|
| Ultra Legendary | 1 |
| Legendary | 2 |
| Mythical | 2 |
| Epic | 2 |
| Rare | 2 |
| Common | Unlimited |
| Basic | Unlimited |

### Abilities
- Each card has one unique ability
- Active abilities can be used **ONCE per card lifetime**
- Passive abilities are always active
- Choose wisely when to use your ability!

## Files

- `main.py` - Entry point, run this to play
- `engine.py` - Core game engine
- `card.py` - Card class and loading
- `status.py` - Status effect system
- `ability_engine.py` - Ability execution
- `deck_builder.py` - Deck building interface
- `cards.json` - Card database (53 cards)
- `utils.py` - Utilities (RNG, colors, helpers)
- `test_game.py` - Test suite

## Testing

Run the test suite to verify everything works:

```bash
cd tcg
python3 test_game.py
```

## Requirements

- Python 3.10+
- No external libraries required
- Terminal with ANSI color support

## Game Modes

1. **Standard Game** - Build decks manually
2. **Quick Game** - Random decks for both players

## Tips

- Balance your deck with different rarities
- Save powerful abilities for critical moments
- Status effects stack - use this to your advantage
- Higher rarity cards give more points but are limited
- Don't underestimate Basic/Common cards - they're unlimited!

Enjoy the chaos!
