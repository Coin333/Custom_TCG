#include "../include/GameEngine.h"
#include <iostream>
#include <algorithm>
#include <limits>
#include <sstream>

GameEngine::GameEngine()
    : currentPlayerIndex(0), turnNumber(0), state(GameState::MENU),
      winner(nullptr), combatInProgress(false),
      attackingCardIndex(0), defendingCardIndex(0), defendingPlayerIndex(0) {
    players.reserve(2);
}

void GameEngine::addPlayer(const std::string& name, const Deck& deck) {
    players.emplace_back(name, deck);
}

void GameEngine::startGame() {
    if (players.size() < 2) {
        std::cerr << "Error: Need at least 2 players to start game.\n";
        return;
    }
    
    state = GameState::SETUP;
    turnNumber = 0;
    winner = nullptr;
    currentPlayerIndex = 0;
    
    // Shuffle decks
    for (auto& player : players) {
        player.shuffleDeck();
    }
    
    // Draw starting hands - first player draws 6, second draws 7
    if (!players.empty()) {
        players[0].drawCard(6);  // First player draws 6
    }
    if (players.size() > 1) {
        players[1].drawCard(7);  // Second player draws 7
    }
    
    setupGame();
}

void GameEngine::setupGame() {
    // For now, skip mulligan phase and go straight to playing
    // In a full implementation, you'd handle mulligan here
    state = GameState::PLAYING;
    startTurn();
}

Player* GameEngine::getCurrentPlayer() {
    if (currentPlayerIndex >= players.size()) {
        return nullptr;
    }
    return &players[currentPlayerIndex];
}

Player* GameEngine::getOpponent(size_t playerIndex) {
    if (players.size() != 2) {
        return nullptr;  // Only supports 2-player games
    }
    return &players[1 - playerIndex];
}

void GameEngine::nextTurn() {
    endTurn();
    
    // Switch to next player
    currentPlayerIndex = (currentPlayerIndex + 1) % players.size();
    
    // Increment turn number after both players have gone
    if (currentPlayerIndex == 0) {
        turnNumber++;
    }
    
    startTurn();
}

void GameEngine::startTurn() {
    Player* current = getCurrentPlayer();
    if (!current) return;
    
    current->startTurn();
    
    // Check win conditions at start of turn
    checkWinConditions();
}

void GameEngine::endTurn() {
    Player* current = getCurrentPlayer();
    if (!current) return;
    
    current->endTurn();
}

bool GameEngine::playCard(size_t playerIndex, size_t handIndex) {
    if (state != GameState::PLAYING) {
        return false;
    }
    
    if (playerIndex >= players.size() || playerIndex != currentPlayerIndex) {
        return false;  // Can only play on your turn
    }
    
    return players[playerIndex].playCard(handIndex);
}

bool GameEngine::playCardFromHand(size_t handIndex) {
    return playCard(currentPlayerIndex, handIndex);
}

bool GameEngine::attackWithCard(size_t fieldIndex, size_t targetFieldIndex, size_t targetPlayerIndex) {
    if (state != GameState::PLAYING) {
        return false;
    }
    
    Player* attacker = getCurrentPlayer();
    if (!attacker) return false;
    
    Card* attackingCard = attacker->getFieldCard(fieldIndex);
    if (!attackingCard || !attackingCard->canAttack || attackingCard->type != CardType::CREATURE) {
        return false;
    }
    
    // If no target specified, attack opponent directly
    if (targetFieldIndex == SIZE_MAX && targetPlayerIndex == SIZE_MAX) {
        Player* opponent = getOpponent(currentPlayerIndex);
        if (!opponent) return false;
        
        processPlayerDamage(*attackingCard, *opponent);
        attackingCard->canAttack = false;  // Used up attack
        checkWinConditions();
        return true;
    }
    
    // Attack a creature
    if (targetFieldIndex != SIZE_MAX && targetPlayerIndex != SIZE_MAX) {
        Player* defender = getOpponent(currentPlayerIndex);
        if (!defender) return false;
        
        Card* defendingCard = defender->getFieldCard(targetFieldIndex);
        if (!defendingCard) return false;
        
        processDamage(*attackingCard, *defendingCard);
        attackingCard->canAttack = false;
        
        // Update field to remove dead creatures
        attacker->updateField();
        defender->updateField();
        
        checkWinConditions();
        return true;
    }
    
    return false;
}

bool GameEngine::attackPlayer(size_t fieldIndex, size_t targetPlayerIndex) {
    return attackWithCard(fieldIndex, SIZE_MAX, targetPlayerIndex);
}

void GameEngine::resolveCombat() {
    // Combat resolution logic
    // This can be expanded for more complex combat scenarios
}

void GameEngine::processDamage(Card& attacker, Card& defender) {
    // Both creatures deal damage to each other
    defender.takeDamage(attacker.attack);
    attacker.takeDamage(defender.attack);
}

void GameEngine::processPlayerDamage(Card& attacker, Player& defender) {
    // Creature deals damage directly to player
    defender.takeDamage(attacker.attack);
}

bool GameEngine::useAbility(size_t playerIndex, size_t fieldIndex, size_t abilityIndex, size_t targetIndex) {
    if (state != GameState::PLAYING) {
        return false;
    }
    
    if (playerIndex >= players.size()) {
        return false;
    }
    
    Player* player = &players[playerIndex];
    Card* card = player->getFieldCard(fieldIndex);
    
    if (!card || abilityIndex >= card->abilities.size()) {
        return false;
    }
    
    Ability& ability = card->abilities[abilityIndex];
    
    // Check if player can afford the ability
    if (!player->canAfford(ability.cost_modifier)) {
        return false;
    }
    
    // Consume energy
    player->consumeEnergy(ability.cost_modifier);
    
    // Process ability based on type
    switch (ability.type) {
        case AbilityType::DAMAGE: {
            if (ability.target == TargetType::ENEMY) {
                Player* opponent = getOpponent(playerIndex);
                if (opponent) {
                    if (targetIndex != SIZE_MAX && targetIndex < opponent->getFieldSize()) {
                        Card* target = opponent->getFieldCard(targetIndex);
                        if (target) {
                            target->takeDamage(ability.value);
                        }
                    } else {
                        opponent->takeDamage(ability.value);
                    }
                }
            }
            break;
        }
        case AbilityType::HEAL: {
            if (ability.target == TargetType::SELF || ability.target == TargetType::ALLY) {
                if (targetIndex != SIZE_MAX && targetIndex < player->getFieldSize()) {
                    Card* target = player->getFieldCard(targetIndex);
                    if (target) {
                        target->heal(ability.value);
                    }
                } else {
                    player->heal(ability.value);
                }
            }
            break;
        }
        // Add more ability type handlers as needed
        default:
            break;
    }
    
    checkWinConditions();
    return true;
}

void GameEngine::checkWinConditions() {
    // Check if any player has died
    for (auto& player : players) {
        if (!player.isAlive()) {
            // Find the winner (opponent)
            for (auto& other : players) {
                if (&other != &player) {
                    endGame(&other);
                    return;
                }
            }
        }
    }
}

void GameEngine::endGame(Player* winnerPlayer) {
    winner = winnerPlayer;
    state = GameState::GAME_OVER;
}

bool GameEngine::canMakeMove() {
    if (state != GameState::PLAYING) {
        return false;
    }
    
    Player* current = getCurrentPlayer();
    if (!current || !current->isAlive()) {
        return false;
    }
    
    // Check if player can play any card or attack with any card
    const auto& hand = current->getHand();
    for (const auto& card : hand) {
        if (current->canAfford(card.cost)) {
            return true;
        }
    }
    
    const auto& field = current->getField();
    for (const auto& card : field) {
        if (card.canAttack) {
            return true;
        }
    }
    
    return false;
}

std::vector<std::string> GameEngine::getAvailableActions(size_t playerIndex) {
    std::vector<std::string> actions;
    
    if (playerIndex != currentPlayerIndex) {
        return actions;  // Not your turn
    }
    
    Player* player = getCurrentPlayer();
    if (!player) return actions;
    
    // Add playable cards
    const auto& hand = player->getHand();
    for (size_t i = 0; i < hand.size(); ++i) {
        if (player->canAfford(hand[i].cost)) {
            actions.push_back("Play card " + std::to_string(i + 1) + ": " + hand[i].name);
        }
    }
    
    // Add attack options
    const auto& field = player->getField();
    for (size_t i = 0; i < field.size(); ++i) {
        if (field[i].canAttack) {
            actions.push_back("Attack with " + field[i].name + " (index " + std::to_string(i) + ")");
        }
    }
    
    // Always can end turn
    actions.push_back("End turn");
    
    return actions;
}

void GameEngine::displayGameState() {
    std::cout << "\n=== Turn " << turnNumber << " ===\n";
    std::cout << "Current Player: " << (getCurrentPlayer() ? getCurrentPlayer()->getName() : "None") << "\n\n";
    
    for (size_t i = 0; i < players.size(); ++i) {
        bool isCurrent = (i == currentPlayerIndex);
        std::cout << (isCurrent ? ">>> " : "    ");
        std::cout << players[i].getStatusString();
        std::cout << "\n";
    }
    
    if (state == GameState::GAME_OVER && winner) {
        std::cout << "\n*** GAME OVER ***\n";
        std::cout << "Winner: " << winner->getName() << "!\n";
    }
}

std::string GameEngine::getGameStateString() const {
    std::ostringstream oss;
    oss << "Turn: " << turnNumber << "\n";
    oss << "State: " << static_cast<int>(state) << "\n";
    
    for (const auto& player : players) {
        oss << player.toString() << "\n";
    }
    
    return oss.str();
}
