#ifndef ABILITY_H
#define ABILITY_H

#include <string>
#include <vector>

// Enum for different ability types/effects
enum class AbilityType {
    DAMAGE,           // Deal damage
    HEAL,             // Heal target
    DRAW,             // Draw cards
    BUFF,             // Increase stats
    DEBUFF,           // Decrease stats
    SHIELD,           // Block damage
    SPECIAL           // Special/unique effects
};

// Enum for target types
enum class TargetType {
    SELF,             // Self
    ENEMY,            // Enemy player or card
    ALLY,             // Ally card
    BOTH,             // Both players
    NONE              // No target (passive)
};

struct Ability {
    std::string name;
    std::string description;
    AbilityType type;
    TargetType target;
    
    // Effect values
    int value;              // Damage, heal amount, etc.
    int cost_modifier;      // Additional cost to use
    int duration;           // Turns the effect lasts (0 = instant)
    
    // Constructor
    Ability(const std::string& name = "",
            const std::string& description = "",
            AbilityType type = AbilityType::SPECIAL,
            TargetType target = TargetType::NONE,
            int value = 0,
            int cost_modifier = 0,
            int duration = 0);
    
    // Check if ability can be used
    bool canUse(int current_energy) const;
    
    // Display ability info
    std::string toString() const;
};

#endif // ABILITY_H
