#include "../include/Deck.h"
#include <random>
#include <algorithm>
#include <chrono>
#include <sstream>

Deck::Deck(size_t maxSize) : maxSize(maxSize) {
    cards.reserve(maxSize);
}

void Deck::addCard(const Card& card) {
    if (cards.size() < maxSize) {
        cards.push_back(card);
    }
}

void Deck::addCard(const Card& card, int quantity) {
    for (int i = 0; i < quantity && cards.size() < maxSize; ++i) {
        cards.push_back(card);
    }
}

bool Deck::removeCard(const std::string& cardName) {
    auto it = std::find_if(cards.begin(), cards.end(),
        [&cardName](const Card& card) {
            return card.name == cardName;
        });
    
    if (it != cards.end()) {
        cards.erase(it);
        return true;
    }
    return false;
}

bool Deck::removeCard(const std::string& cardName, int quantity) {
    int removed = 0;
    while (removed < quantity) {
        auto it = std::find_if(cards.begin(), cards.end(),
            [&cardName](const Card& card) {
                return card.name == cardName;
            });
        
        if (it != cards.end()) {
            cards.erase(it);
            removed++;
        } else {
            break;
        }
    }
    return removed > 0;
}

void Deck::shuffle() {
    unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
    std::shuffle(cards.begin(), cards.end(), std::default_random_engine(seed));
}

Card Deck::drawCard() {
    if (cards.empty()) {
        // Return a default "empty" card - in a real game you'd handle this differently
        return Card("Empty", "No cards left in deck", CardType::SPELL, 0, 0, 0);
    }
    
    Card drawn = cards.back();
    cards.pop_back();
    return drawn;
}

Card Deck::drawCard(int index) {
    if (index < 0 || index >= static_cast<int>(cards.size())) {
        return Card("Empty", "Invalid index", CardType::SPELL, 0, 0, 0);
    }
    
    Card drawn = cards[index];
    cards.erase(cards.begin() + index);
    return drawn;
}

bool Deck::isEmpty() const {
    return cards.empty();
}

size_t Deck::size() const {
    return cards.size();
}

void Deck::clear() {
    cards.clear();
}

std::vector<Card> Deck::getCards() const {
    return cards;
}

Card Deck::getCard(size_t index) const {
    if (index >= cards.size()) {
        return Card("Empty", "Invalid index", CardType::SPELL, 0, 0, 0);
    }
    return cards[index];
}

int Deck::countCard(const std::string& cardName) const {
    return std::count_if(cards.begin(), cards.end(),
        [&cardName](const Card& card) {
            return card.name == cardName;
        });
}

bool Deck::isValid() const {
    // Basic validation: deck should have at least some cards
    // In a real TCG, you might have minimum/maximum size requirements
    return !cards.empty() && cards.size() <= maxSize;
}

std::string Deck::toString() const {
    std::ostringstream oss;
    oss << "Deck (" << cards.size() << "/" << maxSize << " cards):\n";
    
    // Group cards by name
    std::vector<std::string> uniqueNames;
    for (const auto& card : cards) {
        if (std::find(uniqueNames.begin(), uniqueNames.end(), card.name) == uniqueNames.end()) {
            uniqueNames.push_back(card.name);
        }
    }
    
    for (const auto& name : uniqueNames) {
        int count = countCard(name);
        oss << "  " << count << "x " << name << "\n";
    }
    
    return oss.str();
}
