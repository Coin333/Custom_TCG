#ifndef CARD_H
#define CARD_H

#include "Ability.h"
#include <string>
#include <vector>
#include <memory>

// Card type enum
enum class CardType {
    CREATURE,         // Attack/defense cards
    SPELL,            // One-time effect cards
    ARTIFACT          // Ongoing effect cards
};

class Card {
public:
    // Basic card properties
    std::string name;
    std::string description;
    CardType type;
    
    // Combat stats (for creatures)
    int cost;               // Energy/mana cost to play
    int attack;             // Attack damage
    int hitPoints;          // Current hit points
    int maxHitPoints;       // Maximum hit points
    
    // Card state
    bool canAttack;         // Whether card can attack this turn
    bool isPlayed;          // Whether card is in play
    int turnPlayed;         // Turn number when played
    
    // Abilities
    std::vector<Ability> abilities;
    
    // Constructor
    Card(const std::string& name = "Unknown",
         const std::string& description = "",
         CardType type = CardType::CREATURE,
         int cost = 1,
         int attack = 0,
         int hitPoints = 1);
    
    // Card operations
    void takeDamage(int damage);
    void heal(int amount);
    bool isAlive() const;
    void resetTurnState();  // Reset attack state for new turn
    
    // Ability management
    void addAbility(const Ability& ability);
    bool hasAbility(const std::string& abilityName) const;
    
    // Get card info
    std::string getTypeString() const;
    std::string toString() const;
    std::string getStatsString() const;
    
    // Static factory methods for common cards
    static Card createBasicCreature(const std::string& name, int cost, int attack, int hp);
    static Card createSpell(const std::string& name, const std::string& description, int cost);
};

#endif // CARD_H
