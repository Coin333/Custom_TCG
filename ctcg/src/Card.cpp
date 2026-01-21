#include "../include/Card.h"
#include <sstream>

Card::Card(const std::string& name,
           const std::string& description,
           CardType type,
           int cost,
           int attack,
           int hitPoints)
    : name(name), description(description), type(type),
      cost(cost), attack(attack), hitPoints(hitPoints), maxHitPoints(hitPoints),
      canAttack(false), isPlayed(false), turnPlayed(0) {
}

void Card::takeDamage(int damage) {
    hitPoints -= damage;
    if (hitPoints < 0) {
        hitPoints = 0;
    }
}

void Card::heal(int amount) {
    hitPoints += amount;
    if (hitPoints > maxHitPoints) {
        hitPoints = maxHitPoints;
    }
}

bool Card::isAlive() const {
    return hitPoints > 0;
}

void Card::resetTurnState() {
    canAttack = true;  // Reset attack ability for new turn
}

void Card::addAbility(const Ability& ability) {
    abilities.push_back(ability);
}

bool Card::hasAbility(const std::string& abilityName) const {
    for (const auto& ability : abilities) {
        if (ability.name == abilityName) {
            return true;
        }
    }
    return false;
}

std::string Card::getTypeString() const {
    switch (type) {
        case CardType::CREATURE:
            return "Creature";
        case CardType::SPELL:
            return "Spell";
        case CardType::ARTIFACT:
            return "Artifact";
        default:
            return "Unknown";
    }
}

std::string Card::toString() const {
    std::ostringstream oss;
    oss << "[" << name << "] " << getTypeString();
    oss << " | Cost: " << cost;
    
    if (type == CardType::CREATURE) {
        oss << " | ATK: " << attack << " | HP: " << hitPoints << "/" << maxHitPoints;
    }
    
    if (!abilities.empty()) {
        oss << " | Abilities: ";
        for (size_t i = 0; i < abilities.size(); ++i) {
            oss << abilities[i].name;
            if (i < abilities.size() - 1) oss << ", ";
        }
    }
    
    if (!description.empty()) {
        oss << "\n" << description;
    }
    
    return oss.str();
}

std::string Card::getStatsString() const {
    std::ostringstream oss;
    oss << name << " - Cost: " << cost;
    if (type == CardType::CREATURE) {
        oss << ", ATK: " << attack << ", HP: " << hitPoints << "/" << maxHitPoints;
    }
    return oss.str();
}

Card Card::createBasicCreature(const std::string& name, int cost, int attack, int hp) {
    return Card(name, "", CardType::CREATURE, cost, attack, hp);
}

Card Card::createSpell(const std::string& name, const std::string& description, int cost) {
    Card spell(name, description, CardType::SPELL, cost, 0, 0);
    return spell;
}
