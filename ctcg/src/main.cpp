#include "../include/GameEngine.h"
#include "../include/Deck.h"
#include "../include/Card.h"
#include "../include/Ability.h"
#include <iostream>

// Helper function to create a simple starter deck
Deck createStarterDeck(const std::string& name) {
    Deck deck(30);
    
    // Add basic creatures
    for (int i = 0; i < 4; ++i) {
        deck.addCard(Card::createBasicCreature("Goblin", 1, 1, 1));
    }
    
    for (int i = 0; i < 3; ++i) {
        deck.addCard(Card::createBasicCreature("Orc Warrior", 3, 3, 3));
    }
    
    for (int i = 0; i < 2; ++i) {
        Card dragon = Card::createBasicCreature("Dragon", 8, 6, 8);
        dragon.description = "A fearsome flying beast.";
        deck.addCard(dragon);
    }
    
    // Add some spells
    for (int i = 0; i < 3; ++i) {
        Card spell = Card::createSpell("Lightning Bolt", "Deal 3 damage", 2);
        Ability damage("Lightning", "Deal 3 damage", 
                       AbilityType::DAMAGE, TargetType::ENEMY, 3, 0, 0);
        spell.addAbility(damage);
        deck.addCard(spell);
    }
    
    // Fill rest with basic creatures
    for (int i = 0; i < 18; ++i) {
        int cost = (i % 5) + 1;
        int attack = cost;
        int hp = cost + 1;
        deck.addCard(Card::createBasicCreature("Creature " + std::to_string(cost), cost, attack, hp));
    }
    
    return deck;
}

int main() {
    std::cout << "=== Custom Trading Card Game ===\n\n";
    
    // Create game engine
    GameEngine game;
    
    // Create decks for players
    Deck deck1 = createStarterDeck("Deck 1");
    Deck deck2 = createStarterDeck("Deck 2");
    
    // Add players
    game.addPlayer("Player 1", deck1);
    game.addPlayer("Player 2", deck2);
    
    // Start the game
    std::cout << "Starting game...\n";
    game.startGame();
    
    // Simple game loop (for demonstration)
    // In a real implementation, you'd have proper turn handling and input
    std::cout << "\n=== Game Started ===\n";
    
    int turns = 0;
    const int MAX_TURNS = 20;  // Prevent infinite loop
    
    while (!game.isGameOver() && turns < MAX_TURNS) {
        game.displayGameState();
        
        Player* currentPlayer = game.getCurrentPlayer();
        if (!currentPlayer) break;
        
        std::cout << "\n--- " << currentPlayer->getName() << "'s Turn ---\n";
        
        // Auto-play first affordable card from hand (simplified AI)
        const auto& hand = currentPlayer->getHand();
        bool playedCard = false;
        for (size_t i = 0; i < hand.size(); ++i) {
            if (currentPlayer->canAfford(hand[i].cost)) {
                if (game.playCardFromHand(i)) {
                    std::cout << currentPlayer->getName() << " plays: " << hand[i].name << "\n";
                    playedCard = true;
                    break;
                }
            }
        }
        
        // Auto-attack with first available creature (simplified AI)
        const auto& field = currentPlayer->getField();
        for (size_t i = 0; i < field.size(); ++i) {
            if (field[i].canAttack) {
                // Attack opponent directly (simplified - assumes 2-player game)
                // Use attackWithCard with no target to attack opponent directly
                if (game.attackWithCard(i)) {
                    std::cout << currentPlayer->getName() << " attacks with " 
                              << field[i].name << "!\n";
                }
                break;
            }
        }
        
        // End turn
        game.nextTurn();
        turns++;
        
        std::cout << "\n";
    }
    
    if (game.isGameOver()) {
        Player* winner = game.getWinner();
        if (winner) {
            std::cout << "\n*** GAME OVER ***\n";
            std::cout << "Winner: " << winner->getName() << "!\n";
        }
    } else {
        std::cout << "\nMax turns reached.\n";
    }
    
    return 0;
}
