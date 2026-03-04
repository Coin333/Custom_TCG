#!/usr/bin/env python3
"""
Comprehensive Passive Ability Test Script
Tests all passive abilities to ensure they activate correctly
"""
import sys
sys.path.insert(0, '.')

from card import load_cards_from_json, Card
from ability_engine import ability_engine
from status import create_status, StatusManager

# Store test results
results = {"passed": [], "failed": []}

def test_passive(card_name: str, test_name: str, test_func):
    """Run a test and track result."""
    try:
        result = test_func()
        if result:
            results["passed"].append(f"{card_name}: {test_name}")
            print(f"  ✓ {test_name}")
            return True
        else:
            results["failed"].append(f"{card_name}: {test_name}")
            print(f"  ✗ {test_name}")
            return False
    except Exception as e:
        results["failed"].append(f"{card_name}: {test_name} - {str(e)}")
        print(f"  ✗ {test_name} - ERROR: {e}")
        return False

def get_card(cards, name):
    """Get a card by name."""
    for c in cards:
        if c.name == name:
            return c.copy()
    return None

def main():
    print("=" * 60)
    print("COMPREHENSIVE PASSIVE TEST")
    print("=" * 60)
    
    cards = load_cards_from_json("cards.json")
    print(f"Loaded {len(cards)} cards\n")
    
    # ========================================
    # DONALD TRUMP - Secret Service
    # ========================================
    print("DONALD TRUMP - Secret Service Passive")
    trump = get_card(cards, "Donald Trump")
    
    test_passive("Donald Trump", "Has passive field defined", lambda: trump.passive is not None)
    test_passive("Donald Trump", "Passive is secret_service", lambda: trump.passive.effect_id == "secret_service")
    
    # Trigger passive at turn_start
    ability_engine.trigger_passive(trump, "secret_service", "turn_start", {})
    test_passive("Donald Trump", "25% DR status applied", lambda: trump.status_manager.has_status("Secret Service"))
    test_passive("Donald Trump", "DR value is 25%", lambda: trump.status_manager.get_damage_reduction() >= 25)
    
    # ========================================
    # STEPH CURRY - Steph Defense
    # ========================================
    print("\nSTEPH CURRY - Steph Defense Passive")
    steph = get_card(cards, "Steph Curry")
    
    test_passive("Steph Curry", "Has passive field defined", lambda: steph.passive is not None)
    test_passive("Steph Curry", "Passive is steph_defense", lambda: steph.passive.effect_id == "steph_defense")
    
    # Trigger passive at battle_start
    ability_engine.trigger_passive(steph, "steph_defense", "battle_start", {})
    test_passive("Steph Curry", "33% DR status applied", lambda: steph.status_manager.has_status("Steph Defense"))
    test_passive("Steph Curry", "DR value is 33%", lambda: steph.status_manager.get_damage_reduction() >= 33)
    
    # ========================================
    # ISHOWSPEED - Backflip
    # ========================================
    print("\nISHOWSPEED - Backflip Passive")
    speed = get_card(cards, "IShowSpeed")
    
    test_passive("IShowSpeed", "Has passive field defined", lambda: speed.passive is not None)
    test_passive("IShowSpeed", "Passive is backflip", lambda: speed.passive.effect_id == "backflip")
    # Backflip is 25% chance so we just test the handler exists
    test_passive("IShowSpeed", "Backflip handler exists", lambda: "backflip" in ability_engine._passives)
    
    # ========================================
    # ANDREW TATE - Alpha
    # ========================================
    print("\nANDREW TATE - Alpha Passive")
    tate = get_card(cards, "Andrew Tate")
    
    test_passive("Andrew Tate", "Has passive field defined", lambda: tate.passive is not None)
    test_passive("Andrew Tate", "Passive is alpha", lambda: tate.passive.effect_id == "alpha")
    
    # Trigger passive at battle_start
    ability_engine.trigger_passive(tate, "alpha", "battle_start", {})
    test_passive("Andrew Tate", "25% DR status applied", lambda: tate.status_manager.has_status("Alpha"))
    test_passive("Andrew Tate", "DR value is 25%", lambda: tate.status_manager.get_damage_reduction() >= 25)
    
    # ========================================
    # MLK - MLK Peace
    # ========================================
    print("\nMLK - MLK Peace Passive")
    mlk = get_card(cards, "MLK")
    
    test_passive("MLK", "Has passive field defined", lambda: mlk.passive is not None)
    test_passive("MLK", "Passive is mlk_peace", lambda: mlk.passive.effect_id == "mlk_peace")
    
    # Trigger passive at battle_start
    ability_engine.trigger_passive(mlk, "mlk_peace", "battle_start", {})
    test_passive("MLK", "80% DR status applied", lambda: mlk.status_manager.has_status("MLK Peace"))
    test_passive("MLK", "DR value is 80%", lambda: mlk.status_manager.get_damage_reduction() >= 80)
    
    # ========================================
    # SADDAM HUSSEIN - Saddam Shield
    # ========================================
    print("\nSADDAM HUSSEIN - Saddam Shield Passive")
    saddam = get_card(cards, "Saddam Hussein")
    
    test_passive("Saddam Hussein", "Has passive field defined", lambda: saddam.passive is not None)
    test_passive("Saddam Hussein", "Passive is saddam_shield", lambda: saddam.passive.effect_id == "saddam_shield")
    
    # Trigger passive at battle_start
    ability_engine.trigger_passive(saddam, "saddam_shield", "battle_start", {})
    test_passive("Saddam Hussein", "50% DR status applied", lambda: saddam.status_manager.has_status("Saddam Shield"))
    test_passive("Saddam Hussein", "DR value is 50%", lambda: saddam.status_manager.get_damage_reduction() >= 50)
    
    # ========================================
    # MONKEY - Monkey Agility
    # ========================================
    print("\nMONKEY - Monkey Agility Passive")
    monkey = get_card(cards, "Monkey")
    
    test_passive("Monkey", "Has passive field defined", lambda: monkey.passive is not None)
    test_passive("Monkey", "Passive is monkey_agility", lambda: monkey.passive.effect_id == "monkey_agility")
    
    # Trigger passive at battle_start
    ability_engine.trigger_passive(monkey, "monkey_agility", "battle_start", {})
    test_passive("Monkey", "20% dodge status applied", lambda: monkey.status_manager.has_status("Monkey Agility"))
    test_passive("Monkey", "Dodge value is 20%", lambda: monkey.status_manager.get_dodge_chance() >= 20)
    
    # ========================================
    # NOAH TSUI - Jump + Asian Blindness
    # ========================================
    print("\nNOAH TSUI - Jump + Asian Blindness Passives")
    noah = get_card(cards, "Noah Tsui")
    
    test_passive("Noah Tsui", "Has primary passive field", lambda: noah.passive is not None)
    test_passive("Noah Tsui", "Primary passive is jump", lambda: noah.passive.effect_id == "jump")
    test_passive("Noah Tsui", "Has secondary passive field", lambda: noah.secondary_passive is not None)
    test_passive("Noah Tsui", "Secondary is asian_blindness", lambda: noah.secondary_passive.effect_id == "asian_blindness")
    
    # Trigger passive at battle_start
    ability_engine.trigger_passive(noah, "jump", "battle_start", {})
    test_passive("Noah Tsui", "50% dodge status applied", lambda: noah.status_manager.has_status("Jump"))
    test_passive("Noah Tsui", "Dodge value is 50%", lambda: noah.status_manager.get_dodge_chance() >= 50)
    
    ability_engine.trigger_passive(noah, "asian_blindness", "battle_start", {})
    test_passive("Noah Tsui", "Asian Blindness status applied", lambda: noah.status_manager.has_status("Asian Blindness"))
    
    # ========================================
    # COLIN SWEENEY - Procrastination
    # ========================================
    print("\nCOLIN SWEENEY - Procrastination Passive")
    colin = get_card(cards, "Colin Sweeney")
    
    test_passive("Colin Sweeney", "Has passive field defined", lambda: colin.passive is not None)
    test_passive("Colin Sweeney", "Passive is procrastination", lambda: colin.passive.effect_id == "procrastination")
    
    # Trigger passive at battle_start
    ability_engine.trigger_passive(colin, "procrastination", "battle_start", {})
    test_passive("Colin Sweeney", "Procrastination status applied", lambda: colin.status_manager.has_status("Procrastination"))
    
    # ========================================
    # ALDO ORTIZ - Slipped + High Dodge
    # ========================================
    print("\nALDO ORTIZ - Slipped + High Dodge Passives")
    aldo = get_card(cards, "Aldo Ortiz")
    
    test_passive("Aldo Ortiz", "Has primary passive field", lambda: aldo.passive is not None)
    test_passive("Aldo Ortiz", "Primary passive is aldo_slip", lambda: aldo.passive.effect_id == "aldo_slip")
    test_passive("Aldo Ortiz", "Has secondary passive field", lambda: aldo.secondary_passive is not None)
    test_passive("Aldo Ortiz", "Secondary is high_dodge", lambda: aldo.secondary_passive.effect_id == "high_dodge")
    
    # Trigger high_dodge at turn_start (HP should be full, over 1000)
    ability_engine.trigger_passive(aldo, "high_dodge", "turn_start", {})
    test_passive("Aldo Ortiz", "High Dodge applied (HP > 1000)", lambda: aldo.status_manager.has_status("High Dodge"))
    test_passive("Aldo Ortiz", "Dodge is 75%", lambda: aldo.status_manager.get_dodge_chance() >= 75)
    
    # Test that high dodge is removed when HP < 1000
    aldo2 = get_card(cards, "Aldo Ortiz")
    aldo2.current_hp = 500
    ability_engine.trigger_passive(aldo2, "high_dodge", "turn_start", {})
    test_passive("Aldo Ortiz", "High Dodge NOT applied (HP < 1000)", lambda: not aldo2.status_manager.has_status("High Dodge"))
    
    # ========================================
    # VERIFY ALL CARDS WITH PASSIVES
    # ========================================
    print("\nVERIFYING ALL PASSIVE CARDS")
    cards_with_passives = [
        ("Donald Trump", "secret_service"),
        ("Steph Curry", "steph_defense"),
        ("IShowSpeed", "backflip"),
        ("Andrew Tate", "alpha"),
        ("MLK", "mlk_peace"),
        ("Saddam Hussein", "saddam_shield"),
        ("Monkey", "monkey_agility"),
        ("Noah Tsui", "jump"),
        ("Colin Sweeney", "procrastination"),
        ("Aldo Ortiz", "aldo_slip"),
    ]
    
    for name, expected_id in cards_with_passives:
        card = get_card(cards, name)
        test_passive(name, f"Has correct passive ({expected_id})", 
                     lambda c=card, eid=expected_id: c.passive is not None and c.passive.effect_id == eid)
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 60)
    print("PASSIVE TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {len(results['passed'])}")
    print(f"Failed: {len(results['failed'])}")
    
    if results["failed"]:
        print("\nFailed tests:")
        for f in results["failed"]:
            print(f"  - {f}")
    
    return len(results["failed"]) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
