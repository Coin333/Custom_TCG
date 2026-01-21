#ifndef GAME_ENGINE_H
#define GAME_ENGINE_H

#include "Player.h"
#include <vector>
#include <string>

enum class GameState {
    MENU,           // Main menu
    DECK_BUILDING,  // Deck building phase
    SETUP,          // Game setup (mulligan, etc.)
    PLAYING,        // Active game
    COMBAT,         // Combat phase
    GAME_OVER       // Game ended
};

class GameEngine {
private:
    std::vector<Player> players;
    size_t currentPlayerIndex;
    int turnNumber;
    GameState state;
    Player* winner;
    
    // Combat tracking
    bool combatInProgress;
    size_t attackingCardIndex;
    size_t defendingCardIndex;
    size_t defendingPlayerIndex;
    
public:
    // Constructor
    GameEngine();
    
    // Game setup
    void addPlayer(const std::string& name, const Deck& deck);
    void startGame();  // Initialize game
    void setupGame();  // Setup phase (draw starting hands, mulligan)
    
    // Game state
    GameState getState() const { return state; }
    void setState(GameState newState) { state = newState; }
    int getTurnNumber() const { return turnNumber; }
    Player* getCurrentPlayer();
    Player* getOpponent(size_t playerIndex);
    Player* getWinner() const { return winner; }
    bool isGameOver() const { return state == GameState::GAME_OVER; }
    
    // Turn management
    void nextTurn();
    void startTurn();
    void endTurn();
    
    // Card playing
    bool playCard(size_t playerIndex, size_t handIndex);
    bool playCardFromHand(size_t handIndex);
    
    // Combat
    bool attackWithCard(size_t fieldIndex, size_t targetFieldIndex = SIZE_MAX, size_t targetPlayerIndex = SIZE_MAX);
    bool attackPlayer(size_t fieldIndex, size_t targetPlayerIndex);
    void resolveCombat();
    void processDamage(Card& attacker, Card& defender);
    void processPlayerDamage(Card& attacker, Player& defender);
    
    // Ability handling
    bool useAbility(size_t playerIndex, size_t fieldIndex, size_t abilityIndex, size_t targetIndex = SIZE_MAX);
    
    // Win conditions
    void checkWinConditions();
    void endGame(Player* winner);
    
    // Utility
    void displayGameState();
    std::string getGameStateString() const;
    std::vector<Player>& getPlayers() { return players; }
    const std::vector<Player>& getPlayers() const { return players; }
    
    // Game loop helpers
    bool canMakeMove();
    std::vector<std::string> getAvailableActions(size_t playerIndex);
};

#endif // GAME_ENGINE_H
