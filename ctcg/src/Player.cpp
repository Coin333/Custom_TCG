#include "../include/Player.h"
#include <algorithm>
#include <sstream>
#include <random>

Player::Player(const std::string& name, const Deck& deck, int startingHealth)
    : name(name), maxHealth(startingHealth), currentHealth(startingHealth),
      energy(0), maxEnergy(0), deck(deck) {
    hand.reserve(10);
    field.reserve(7);
}

void Player::drawCard(int count) {
    for (int i = 0; i < count && !deck.isEmpty(); ++i) {
        Card drawn = deck.drawCard();
        if (drawn.name != "Empty") {  // Valid card
            hand.push_back(drawn);
        }
    }
}

bool Player::playCard(size_t handIndex) {
    if (handIndex >= hand.size()) {
        return false;
    }
    
    Card card = hand[handIndex];
    
    // Check if player can afford the card
    if (!canAfford(card.cost)) {
        return false;
    }
    
    // Consume energy
    consumeEnergy(card.cost);
    
    // Mark card as played
    card.isPlayed = true;
    
    // Add to field if it's a creature/artifact
    if (card.type == CardType::CREATURE || card.type == CardType::ARTIFACT) {
        addToField(card);
    } else {
        // Spells go to graveyard after being played
        graveyard.push_back(card);
    }
    
    // Remove from hand
    hand.erase(hand.begin() + handIndex);
    
    return true;
}

bool Player::playCard(const Card& card) {
    // Check if player can afford the card
    if (!canAfford(card.cost)) {
        return false;
    }
    
    // Consume energy
    consumeEnergy(card.cost);
    
    // Create a copy and mark as played
    Card playedCard = card;
    playedCard.isPlayed = true;
    
    // Add to field if it's a creature/artifact
    if (card.type == CardType::CREATURE || card.type == CardType::ARTIFACT) {
        addToField(playedCard);
    } else {
        // Spells go to graveyard after being played
        graveyard.push_back(playedCard);
    }
    
    return true;
}

void Player::discardCard(size_t handIndex) {
    if (handIndex < hand.size()) {
        graveyard.push_back(hand[handIndex]);
        hand.erase(hand.begin() + handIndex);
    }
}

void Player::shuffleDeck() {
    deck.shuffle();
}

void Player::addToField(const Card& card) {
    field.push_back(card);
    field.back().resetTurnState();  // Reset attack state
}

bool Player::removeFromField(size_t fieldIndex) {
    if (fieldIndex >= field.size()) {
        return false;
    }
    
    graveyard.push_back(field[fieldIndex]);
    field.erase(field.begin() + fieldIndex);
    return true;
}

Card* Player::getFieldCard(size_t index) {
    if (index >= field.size()) {
        return nullptr;
    }
    return &field[index];
}

void Player::updateField() {
    // Remove dead creatures
    field.erase(
        std::remove_if(field.begin(), field.end(),
            [](const Card& card) {
                return !card.isAlive();
            }),
        field.end()
    );
    
    // Reset attack states for new turn (called by startTurn)
    for (auto& card : field) {
        card.resetTurnState();
    }
}

void Player::takeDamage(int damage) {
    currentHealth -= damage;
    if (currentHealth < 0) {
        currentHealth = 0;
    }
}

void Player::heal(int amount) {
    currentHealth += amount;
    if (currentHealth > maxHealth) {
        currentHealth = maxHealth;
    }
}

void Player::startTurn() {
    // Increase max energy (capped at 10)
    if (maxEnergy < 10) {
        maxEnergy++;
    }
    energy = maxEnergy;
    
    // Draw a card
    drawCard(1);
    
    // Update field and reset attack states
    updateField();
    
    // Reset attack states
    for (auto& card : field) {
        card.canAttack = true;
    }
}

void Player::endTurn() {
    // Any end-of-turn cleanup can go here
    // For now, just mark that turn is ending
}

void Player::setEnergy(int amount) {
    energy = amount;
    if (energy < 0) energy = 0;
    if (energy > maxEnergy) energy = maxEnergy;
}

void Player::consumeEnergy(int amount) {
    energy -= amount;
    if (energy < 0) energy = 0;
}

void Player::shuffleHandIntoDeck() {
    // Put all cards from hand back into deck
    while (!hand.empty()) {
        deck.addCard(hand.back());
        hand.pop_back();
    }
    deck.shuffle();
}

std::string Player::toString() const {
    std::ostringstream oss;
    oss << name << " - HP: " << currentHealth << "/" << maxHealth
        << " | Energy: " << energy << "/" << maxEnergy
        << " | Hand: " << hand.size()
        << " | Field: " << field.size()
        << " | Deck: " << deck.size();
    return oss.str();
}

std::string Player::getStatusString() const {
    std::ostringstream oss;
    oss << "=== " << name << " ===\n";
    oss << "Health: " << currentHealth << "/" << maxHealth << "\n";
    oss << "Energy: " << energy << "/" << maxEnergy << "\n";
    oss << "Hand Size: " << hand.size() << "\n";
    oss << "Field Size: " << field.size() << "\n";
    oss << "Deck Size: " << deck.size() << "\n";
    
    if (!field.empty()) {
        oss << "\nField:\n";
        for (size_t i = 0; i < field.size(); ++i) {
            oss << "  " << (i + 1) << ". " << field[i].getStatsString();
            if (field[i].canAttack) {
                oss << " [Can Attack]";
            }
            oss << "\n";
        }
    }
    
    if (!hand.empty()) {
        oss << "\nHand:\n";
        for (size_t i = 0; i < hand.size(); ++i) {
            oss << "  " << (i + 1) << ". " << hand[i].getStatsString() << "\n";
        }
    }
    
    return oss.str();
}
