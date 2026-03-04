#!/usr/bin/env python3
"""
Test script for Terminal Chaos TCG
Validates all game mechanics before playing
"""
import sys
import os

# Add tcg directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import utils
import status
import card
import ability_engine as ae

def test_status_system():
    """Test status effect system."""
    print("Testing status system...")
    
    sm = status.StatusManager()
    
    # Test adding status
    burn = status.create_status("Burn", 3, "test")
    sm.add_status(burn)
    assert sm.has_status("Burn"), "Burn not added"
    assert len(sm.statuses) == 1, "Wrong status count"
    
    # Test stacking
    burn2 = status.create_status("Burn", 2, "test")
    sm.add_status(burn2)
    assert len(sm.statuses) == 2, "Stacking failed"
    
    # Test non-stackable
    sleep = status.create_status("Sleep", 1, "test")
    sm.add_status(sleep)
    sleep2 = status.create_status("Sleep", 1, "test")
    result = sm.add_status(sleep2)
    assert result == False, "Sleep should not stack"
    
    # Test tick
    sm2 = status.StatusManager()
    s = status.create_status("Burn", 2, "test")
    sm2.add_status(s)
    sm2.tick_all()
    assert sm2.statuses[0].duration == 1, "Tick failed"
    
    print("  Status system OK")
    return True


def test_card_system():
    """Test card creation and mechanics."""
    print("Testing card system...")
    
    cards = card.load_cards_from_json("cards.json")
    assert len(cards) > 0, "No cards loaded"
    
    c1 = cards[0].copy()
    
    # Test HP
    assert c1.is_alive(), "Card should be alive"
    original_hp = c1.current_hp
    c1.take_damage(50)
    assert c1.current_hp == original_hp - 50, f"Wrong HP: {c1.current_hp}"
    
    # Test heal
    c1.heal(25)
    assert c1.current_hp == original_hp - 25, f"Wrong HP after heal: {c1.current_hp}"
    
    # Test overheal cap
    c1.heal(1000)
    assert c1.current_hp == c1.max_hp, "Heal should cap at max HP"
    
    # Test death
    c1.take_damage(c1.max_hp + 100)
    assert not c1.is_alive(), "Card should be dead"
    assert c1.current_hp == 0, "HP should not go negative"
    
    print("  Card system OK")
    return True


def test_ability_engine():
    """Test ability execution."""
    print("Testing ability engine...")
    
    cards = card.load_cards_from_json("cards.json")
    c1 = cards[0].copy()
    c2 = cards[5].copy()
    
    # Test direct damage
    initial_hp = c2.current_hp
    result = ae.ability_engine.execute_ability(c1, c2, "direct_damage", {"damage": 50})
    assert result.success, "Ability should succeed"
    assert c2.current_hp == initial_hp - 50, "Damage not applied"
    
    # Test heal
    c1.take_damage(50)
    result = ae.ability_engine.execute_ability(c1, c2, "heal_self", {"amount": 30})
    assert result.success, "Heal should succeed"
    assert result.healing_done == 30, "Wrong heal amount"
    
    # Test status application
    result = ae.ability_engine.execute_ability(c1, c2, "apply_status", {"status": "Burn", "duration": 2})
    assert result.success, "Status ability should succeed"
    assert c2.has_status("Burn"), "Burn not applied"
    
    print("  Ability engine OK")
    return True


def test_damage_calculation():
    """Test damage calculation order."""
    print("Testing damage calculation...")
    
    cards = card.load_cards_from_json("cards.json")
    c1 = cards[0].copy()
    c2 = cards[0].copy()
    
    # Base damage
    base_dmg = c1.get_attack_damage(c2.max_hp)
    assert base_dmg == c1.attack.base_damage, "Base damage wrong"
    
    # With ATK buff
    enraged = status.create_status("Enraged", 2, "test")
    c1.add_status(enraged)
    buffed_dmg = c1.get_attack_damage(c2.max_hp)
    assert buffed_dmg > base_dmg, f"Buff not applied: {buffed_dmg} <= {base_dmg}"
    
    # With ATK debuff
    c1.status_manager.clear_all()
    weakened = status.create_status("Weakened", 2, "test")
    c1.add_status(weakened)
    debuffed_dmg = c1.get_attack_damage(c2.max_hp)
    assert debuffed_dmg < base_dmg, f"Debuff not applied: {debuffed_dmg} >= {base_dmg}"
    
    print("  Damage calculation OK")
    return True


def test_deck_validation():
    """Test deck building rules."""
    print("Testing deck validation...")
    
    cards = card.load_cards_from_json("cards.json")
    
    # Valid deck
    test_deck = [cards[i].copy() for i in range(10)]
    is_valid, error = card.validate_deck(test_deck)
    print(f"  Sample deck: {is_valid} - {error if error else 'Valid'}")
    
    # Too few cards
    small_deck = [cards[0].copy() for _ in range(5)]
    is_valid, error = card.validate_deck(small_deck)
    assert not is_valid, "Small deck should be invalid"
    
    # Too many cards
    big_deck = [cards[0].copy() for _ in range(15)]
    is_valid, error = card.validate_deck(big_deck)
    assert not is_valid, "Big deck should be invalid"
    
    print("  Deck validation OK")
    return True


def test_rng_system():
    """Test RNG functions."""
    print("Testing RNG system...")
    
    # Test roll
    results = [utils.roll(50) for _ in range(100)]
    assert True in results and False in results, "Roll seems broken"
    
    # Test coin
    results = [utils.coin() for _ in range(100)]
    assert "heads" in results and "tails" in results, "Coin seems broken"
    
    # Test caps
    capped = utils.apply_cap(100, "dodge")
    assert capped == 75, f"Dodge cap failed: {capped}"
    
    capped = utils.apply_cap(100, "damage_reduction")
    assert capped == 80, f"DR cap failed: {capped}"
    
    print("  RNG system OK")
    return True


def test_points_system():
    """Test point values."""
    print("Testing points system...")
    
    expected = {
        "Basic": 1,
        "Common": 2,
        "Rare": 3,
        "Epic": 5,
        "Mythical": 7,
        "Legendary": 10,
        "Ultra Legendary": 15
    }
    
    for rarity, points in expected.items():
        assert utils.RARITY_POINTS[rarity] == points, f"{rarity} points wrong"
    
    print("  Points system OK")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("Terminal Chaos TCG - Test Suite")
    print("=" * 50)
    print()
    
    tests = [
        test_status_system,
        test_card_system,
        test_ability_engine,
        test_damage_calculation,
        test_deck_validation,
        test_rng_system,
        test_points_system,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1
    
    print()
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("\nALL TESTS PASSED! Game is ready to play.")
        print("\nTo start the game, run:")
        print("  python3 main.py")
        return True
    else:
        print("\nSome tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
