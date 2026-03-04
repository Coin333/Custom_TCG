## **Project Name: Terminal Chaos TCG**

**Platform:** Python 3.x  
 **Environment:** Local terminal (single console, 2 players)  
 **Game Type:** 1v1, turn-based, chaotic, rarity-point based

---

# **1️⃣ CORE GAME SUMMARY**

Terminal Chaos TCG is a locally hosted, text-based collectible card game where:

* Two players share one console

* Each builds a 10-card deck from a global card pool

* Each player selects:

  * 1 Active card

  * 2 Bench cards

* No card drawing mid-game

* When an Active card dies:

  * Player selects 1 bench card to replace it

  * A random unused card from their deck fills the empty bench slot

* Game ends when one player reaches the target score threshold

Game identity:

Fast. Random. Chaotic. Minimal UI. No grind. No progression system.

---

# **2️⃣ MATCH FLOW**

## **2.1 Pre-Match Phase**

### **Deck Building**

* Each player builds a 10-card deck

* All cards unlocked

* Rarity limits enforced (see Section 6\)

### **Starting Setup**

1. Coin flip decides first player

2. Each player selects:

   * 1 Active card

   * 2 Bench cards

3. Remaining 7 cards stay in deck pool

---

# **3️⃣ TURN STRUCTURE**

## **Turn Order**

`START TURN`  
`↓`  
`Check Skip Effects`  
`↓`  
`Player Action Phase`  
`↓`  
`Combat Resolution`  
`↓`  
`KO Check`  
`↓`  
`Score Update`  
`↓`  
`End Turn`

---

## **3.1 Start Turn Phase**

1. Resolve:

   * Skip turn effects (Sleep, etc.)

   * Self-damage effects

2. Reduce durations of status effects

3. If skipped → turn ends immediately

---

## **3.2 Player Action Phase**

Player chooses:

`1. Use Ability (if unused)`  
`2. Attack`

Rules:

* Each card may use its Ability ONCE per lifetime

* If player does not use Ability → Attack automatically triggers

* Only Active cards may attack

---

# **4️⃣ COMBAT RULES**

## **4.1 Attack Rules**

* 1 attack per turn

* Damage applies only to Active card

* No direct player damage

---

## **4.2 Damage Calculation Order**

This order is FINAL and must not change:

1. Base attack value

2. Apply percentage-based attack calculations  
    (calculated from opponent’s MAX HP)

3. Apply buffs (Enraged, etc.)

4. Apply debuffs

5. Apply damage reduction

6. Apply dodge

7. Apply critical multiplier

8. Final HP subtraction

Important:

* Percentage attacks use MAX HP before buffs

* Damage reduction applied AFTER percent conversion

* Status stacking allowed

---

# **5️⃣ STATUS SYSTEM**

Statuses are stackable.

Priority Order:

1. Skip Turn

2. Self-Damage

3. Stat Modifiers

4. Dodge

5. Critical

---

## **Example Status Object**

`class Status:`  
    `name: str`  
    `duration: int`  
    `effect_type: str`  
    `magnitude: float`

---

## **Status Examples**

| Status | Effect | Stackable |
| ----- | ----- | ----- |
| Enraged | \+10% ATK, \-10% DEF | Yes |
| Asphyxiation | \-10% ATK | Yes |
| Procrastination | 25% chance skip | Yes |
| Sleep | Skip next turn | No stacking duration override |

Skip and self-damage effects always resolve first.

---

# **6️⃣ RARITY SYSTEM & POINT STRUCTURE**

## **6.1 Rarities**

| Rarity | Color | Points on KO |
| ----- | ----- | ----- |
| Basic | Grey | 1 |
| Common | Green | 2 |
| Rare | Blue | 3 |
| Epic | Purple | 5 |
| Mythical | Red | 7 |
| Legendary | Yellow | 10 |
| Ultra Legendary | Pink | 15 |

---

## **6.2 Win Condition**

First player to reach **25 points** wins.

Why 25?

* Encourages multiple KOs

* Prevents single Ultra Legendary from auto-winning

* Keeps match length 5–10 KOs

---

# **7️⃣ DECK BUILDING RULES**

Each player builds exactly 10 cards.

Rarity Limits:

| Rarity | Max Allowed |
| ----- | ----- |
| Ultra Legendary | 1 |
| Legendary | 2 |
| Mythical | 2 |
| Epic | 2 |
| Rare | 2 |
| Common | Unlimited |
| Basic | Unlimited |

Total must equal 10\.

This prevents:

* Ultra stacking

* Legendary spam

* Overpowered deck builds

---

# **8️⃣ BENCH SYSTEM**

Each player has:

* 1 Active slot

* 2 Bench slots

When Active dies:

1. Player chooses 1 Bench card

2. Selected card becomes Active

3. Random card from unused deck pool fills empty Bench slot

If:

* No bench cards

* No deck cards remaining

Player automatically loses.

---

# **9️⃣ ABILITY SYSTEM**

Each card:

* Has 1 unique ability

* May activate ONCE per lifetime

* Passives are always active

Ability flag:

`card.ability_used = False`

After activation:

`card.ability_used = True`

Passives do not require activation.

---

# **🔟 RANDOMNESS ENGINE**

Centralized RNG system required.

`def roll(chance_percent):`  
    `return random.random() < chance_percent / 100`

Coin Flip:

`def coin():`  
    `return random.choice(["heads", "tails"])`

No direct random calls inside ability logic.

---

# **1️⃣1️⃣ TERMINAL UI SPEC**

Minimal and clean.

Example Layout:

`-------------------------------------`  
`Opponent Active: Shaq`  
`HP: 650 / 900`  
`Status: Enraged (2)`

`-------------------------------------`  
`Your Active: Kobe Bryant`  
`HP: 120 / 350`  
`Status: None`

`Bench:`  
`1. Steph Curry (300 HP)`  
`2. Elon Musk (750 HP)`

`-------------------------------------`  
`Choose Action:`  
`1. Attack`  
`2. Use Ability`  
`-------------------------------------`

---

## **Rarity Color Codes (ANSI)**

| Rarity | ANSI |
| ----- | ----- |
| Basic | White |
| Common | Green |
| Rare | Blue |
| Epic | Magenta |
| Mythical | Red |
| Legendary | Yellow |
| Ultra Legendary | Bright Magenta |

Use ANSI escape codes for name coloring only.

---

# **1️⃣2️⃣ GAME END CONDITIONS**

A player loses if:

* They cannot replace an Active card

* Opponent reaches 25 points

Immediate victory screen displayed.

---

# **1️⃣3️⃣ FILE STRUCTURE**

`/tcg`  
    `main.py`  
    `engine.py`  
    `card.py`  
    `status.py`  
    `ability_engine.py`  
    `deck_builder.py`  
    `cards.json`  
    `utils.py`

---

# **1️⃣4️⃣ ENGINE ARCHITECTURE**

## **Core Classes**

### **Card**

* name

* max\_hp

* current\_hp

* attack\_data

* rarity

* ability

* passive

* statuses

* ability\_used

### **Player**

* deck\_pool (remaining cards)

* active

* bench (2)

* score

### **Game**

* player1

* player2

* turn

* resolve\_combat()

* check\_ko()

* apply\_status()

---

# **1️⃣5️⃣ CHAOS DESIGN PHILOSOPHY**

This game is intentionally:

* Random heavy

* Coin flip influenced

* High damage spikes

* Status stacking allowed

* Minimal defensive complexity

It is NOT:

* Balanced esports ready

* Tournament structured

* Precision optimized

It is controlled chaos.

---

# **1️⃣6️⃣ V1 MVP FEATURES**

Must include:

* Deck selection menu

* Rarity validation enforcement

* Starting selection system

* Turn engine

* Attack system

* Ability system

* Status engine

* Bench replacement system

* Point tracking

* Victory detection

* Colored output

Not included:

* AI

* Save system

* GUI

* Networking

---

# **1️⃣7️⃣ BALANCE SAFETY CAPS**

To prevent infinite nonsense:

* Max damage reduction cap: 80%

* Max dodge cap: 60%

* Max critical multiplier: 500%

* No effect may permanently stack without duration

* No ability may trigger infinitely in a loop

---

# **1️⃣8️⃣ TECHNICAL CONSTRAINTS**

* Python 3.10+

* No external libraries required

* JSON-driven card loading

* No hard-coded card stats

* Ability logic modular

---

# **1️⃣9️⃣ FUTURE EXPANSION READY**

Engine must allow:

* Adding new cards via JSON only

* Adding new status types

* Adding new rarities

* Adding AI opponent later

---

# **🔥 FINAL SUMMARY**

This game is:

* 1v1

* 10-card decks

* 1 active, 2 bench

* No draw phase

* KO grants rarity-based points

* First to 25 points wins

* Ability once per lifetime

* Clean terminal UI

* Modular architecture

