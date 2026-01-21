// Example card definitions
// This file demonstrates how to create cards with different abilities

#include "../../include/Card.h"
#include "../../include/Ability.h"

// Example basic creatures
Card createGoblin() {
    Card goblin = Card::createBasicCreature("Goblin", 1, 1, 1);
    goblin.description = "A small but fierce creature.";
    return goblin;
}

Card createOrcWarrior() {
    Card orc = Card::createBasicCreature("Orc Warrior", 3, 3, 3);
    orc.description = "A strong warrior from the mountains.";
    
    // Add a charge ability (can attack immediately)
    Ability charge("Charge", "Can attack the turn it's played", 
                   AbilityType::BUFF, TargetType::SELF, 0, 0, 0);
    orc.addAbility(charge);
    
    return orc;
}

Card createDragon() {
    Card dragon = Card::createBasicCreature("Dragon", 8, 6, 8);
    dragon.description = "A fearsome flying beast.";
    
    // Add flying ability
    Ability flying("Flying", "Can only be blocked by creatures with Flying", 
                   AbilityType::SPECIAL, TargetType::SELF, 0, 0, 0);
    dragon.addAbility(flying);
    
    // Add fire breath ability
    Ability fireBreath("Fire Breath", "Deals 2 damage when attacking", 
                       AbilityType::DAMAGE, TargetType::ENEMY, 2, 0, 0);
    dragon.addAbility(fireBreath);
    
    return dragon;
}

// Example spell cards
Card createLightningBolt() {
    Card spell = Card::createSpell("Lightning Bolt", "Deal 3 damage to any target", 2);
    
    Ability damage("Lightning", "Deal 3 damage", 
                   AbilityType::DAMAGE, TargetType::ENEMY, 3, 0, 0);
    spell.addAbility(damage);
    
    return spell;
}

Card createHealingPotion() {
    Card spell = Card::createSpell("Healing Potion", "Restore 5 hit points", 2);
    
    Ability heal("Heal", "Restore 5 hit points", 
                 AbilityType::HEAL, TargetType::ALLY, 5, 0, 0);
    spell.addAbility(heal);
    
    return spell;
}
