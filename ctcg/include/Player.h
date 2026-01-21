#ifndef PLAYER_H
#define PLAYER_H

#include "Deck.h"
#include "Card.h"
#include <vector>
#include <string>

class Player {
private:
    std::string name;
    int maxHealth;
    int currentHealth;
    int energy;          // Current energy/mana
    int maxEnergy;       // Maximum energy this turn
    
    Deck deck;
    std::vector<Card> hand;      // Cards in hand
    std::vector<Card> field;     // Cards in play
    std::vector<Card> graveyard; // Discarded/destroyed cards
    
public:
    // Constructor
    Player(const std::string& name, const Deck& deck, int startingHealth = 20);
    
    // Getters
    std::string getName() const { return name; }
    int getHealth() const { return currentHealth; }
    int getMaxHealth() const { return maxHealth; }
    int getEnergy() const { return energy; }
    int getMaxEnergy() const { return maxEnergy; }
    size_t getHandSize() const { return hand.size(); }
    size_t getFieldSize() const { return field.size(); }
    size_t getDeckSize() const { return deck.size(); }
    const std::vector<Card>& getHand() const { return hand; }
    const std::vector<Card>& getField() const { return field; }
    const Deck& getDeck() const { return deck; }
    
    // Game actions
    void drawCard(int count = 1);
    bool playCard(size_t handIndex);  // Play card from hand
    bool playCard(const Card& card);  // Play card directly
    void discardCard(size_t handIndex);
    void shuffleDeck();
    
    // Field management
    void addToField(const Card& card);
    bool removeFromField(size_t fieldIndex);  // Returns true if successful
    Card* getFieldCard(size_t index);
    void updateField();  // Remove dead creatures, update states
    
    // Combat
    void takeDamage(int damage);
    void heal(int amount);
    bool isAlive() const { return currentHealth > 0; }
    
    // Turn management
    void startTurn();  // Called at start of turn
    void endTurn();    // Called at end of turn
    
    // Energy management
    void setEnergy(int amount);
    void consumeEnergy(int amount);
    bool canAfford(int cost) const { return energy >= cost; }
    
    // Utility
    void shuffleHandIntoDeck();  // For mulligan
    std::string toString() const;
    std::string getStatusString() const;
};

#endif // PLAYER_H
