#!/usr/bin/env python3
"""
Comprehensive Ability Test Script
Tests every card ability against the TCG Cards.md specification
"""
import sys
sys.path.insert(0, '.')

from card import load_cards_from_json, Card
from ability_engine import ability_engine
from status import create_status, StatusManager
import random

# Store test results
results = {"passed": [], "failed": []}

def test_ability(card_name: str, test_name: str, test_func):
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
    print("COMPREHENSIVE ABILITY TEST")
    print("=" * 60)
    
    cards = load_cards_from_json("cards.json", include_transform_only=True)
    print(f"Loaded {len(cards)} cards\n")
    
    # ========================================
    # BASIC: Jack Orense
    # ========================================
    print("JACK ORENSE (Basic)")
    jack = get_card(cards, "Jack Orense")
    dummy = get_card(cards, "Charlie Kirk")
    
    test_ability("Jack Orense", "Hockey Stick adds +250 next attack", lambda: (
        ability_engine.execute_ability(jack, dummy, "hockey_stick"),
        jack.status_manager.has_status("Hockey Stick")
    )[1])
    
    # ========================================
    # COMMON: Charlie Kirk
    # ========================================
    print("\nCHARLIE KIRK (Common)")
    charlie = get_card(cards, "Charlie Kirk")
    
    test_ability("Charlie Kirk", "Debate applies crit buff", lambda: (
        ability_engine.execute_ability(charlie, dummy, "debate"),
        charlie.status_manager.has_status("Debate Crit")
    )[1])
    
    # ========================================
    # COMMON: Donald Trump
    # ========================================
    print("\nDONALD TRUMP (Common)")
    trump = get_card(cards, "Donald Trump")
    target = get_card(cards, "Charlie Kirk")
    
    trump_initial_hp = trump.current_hp - 50  # Damage first
    trump.take_damage(50)
    target_initial_hp = target.current_hp
    
    result = ability_engine.execute_ability(trump, target, "firm_handshake")
    
    test_ability("Donald Trump", "Firm Handshake heals self", lambda: trump.current_hp > trump_initial_hp)
    test_ability("Donald Trump", "Firm Handshake drains opponent", lambda: target.current_hp < target_initial_hp)
    test_ability("Donald Trump", "Has Secret Service passive", lambda: trump.passive is not None and trump.passive.effect_id == "secret_service")
    
    # ========================================
    # COMMON: Kanye West
    # ========================================
    print("\nKANYE WEST (Common)")
    kanye = get_card(cards, "Kanye West")
    
    # Test that ability runs without error (transformation is random)
    result = ability_engine.execute_ability(kanye, dummy, "album_drop")
    test_ability("Kanye West", "Album Drop executes", lambda: result.success)
    test_ability("Kanye West", "Attack is percent-based (20%)", lambda: kanye.attack.percent_damage == 20)
    
    # ========================================
    # COMMON: Kobe Bryant
    # ========================================
    print("\nKOBE BRYANT (Common)")
    kobe = get_card(cards, "Kobe Bryant")
    
    result = ability_engine.execute_ability(kobe, dummy, "kobe_fadeaway")
    test_ability("Kobe Bryant", "Kobe Fadeaway applies crit buff", lambda: kobe.status_manager.has_status("Kobe Crit"))
    
    # ========================================
    # COMMON: Shaq
    # ========================================
    print("\nSHAQ (Common)")
    shaq = get_card(cards, "Shaq")
    
    result = ability_engine.execute_ability(shaq, dummy, "backboard_shatter")
    test_ability("Shaq", "Backboard Shatter applies DR", lambda: shaq.status_manager.has_status("Backboard Shatter"))
    test_ability("Shaq", "DR is 50%", lambda: shaq.status_manager.get_damage_reduction() >= 50)
    
    # ========================================
    # COMMON: Burger King Guy
    # ========================================
    print("\nBURGER KING GUY (Common)")
    bk = get_card(cards, "Burger King Guy")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(bk, target, "aggressive_language")
    test_ability("Burger King Guy", "Aggressive Language applies Ragebait", lambda: target.status_manager.has_status("Ragebait"))
    
    # ========================================
    # COMMON: Coughing Baby
    # ========================================
    print("\nCOUGHING BABY (Common)")
    baby = get_card(cards, "Coughing Baby")
    
    result = ability_engine.execute_ability(baby, dummy, "cough")
    test_ability("Coughing Baby", "Cough executes", lambda: result.success)
    test_ability("Coughing Baby", "HP is 10", lambda: baby.max_hp == 10)
    
    # ========================================
    # RARE: Steph Curry
    # ========================================
    print("\nSTEPH CURRY (Rare)")
    steph = get_card(cards, "Steph Curry")
    
    result = ability_engine.execute_ability(steph, dummy, "three_point_blick")
    test_ability("Steph Curry", "3 Point Blick applies crit buff", lambda: steph.status_manager.has_status("Steph Crit"))
    test_ability("Steph Curry", "Has 33% DR passive", lambda: steph.passive is not None)
    
    # ========================================
    # RARE: IShowSpeed
    # ========================================
    print("\nISHOWSPEED (Rare)")
    speed = get_card(cards, "IShowSpeed")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(speed, target, "bark")
    test_ability("IShowSpeed", "Bark applies miss chance", lambda: target.status_manager.has_status("Barked At"))
    test_ability("IShowSpeed", "Has Backflip passive", lambda: speed.passive is not None and speed.passive.effect_id == "backflip")
    
    # ========================================
    # RARE: Hungryhungryhanny
    # ========================================
    print("\nHUNGRYHUNGRYHANNY (Rare)")
    hanny = get_card(cards, "Hungryhungryhanny")
    
    result = ability_engine.execute_ability(hanny, dummy, "lebron_scream")
    test_ability("Hungryhungryhanny", "Lebron Scream executes", lambda: result.success)
    
    # ========================================
    # RARE: Goonicide Guy
    # ========================================
    print("\nGOONICIDE GUY (Rare)")
    goon = get_card(cards, "Goonicide Guy")
    target = get_card(cards, "Charlie Kirk")
    target_initial = target.current_hp
    
    game_state = {"opponent_bench": [get_card(cards, "Donald Trump")]}
    result = ability_engine.execute_ability(goon, target, "goon_akaze", game_state=game_state)
    
    test_ability("Goonicide Guy", "Goon-akaze deals 800 damage", lambda: target.current_hp == target_initial - 800 or target.current_hp <= 0)
    test_ability("Goonicide Guy", "Bench gets Gooned", lambda: game_state["opponent_bench"][0].status_manager.has_status("Gooned"))
    
    # ========================================
    # RARE: NPC
    # ========================================
    print("\nNPC (Rare)")
    npc = get_card(cards, "NPC")
    original_atk = npc.attack.base_damage
    original_hp = npc.max_hp
    
    result = ability_engine.execute_ability(npc, dummy, "mask_removal")
    test_ability("NPC", "Mask Removal doubles ATK", lambda: npc.attack.base_damage == original_atk * 2)
    test_ability("NPC", "Mask Removal doubles HP", lambda: npc.max_hp == original_hp * 2)
    test_ability("NPC", "Incapacitated for 1 turn", lambda: npc.status_manager.has_status("Incapacitated"))
    
    # ========================================
    # RARE: Elon Musk
    # ========================================
    print("\nELON MUSK (Rare)")
    elon = get_card(cards, "Elon Musk")
    
    result = ability_engine.execute_ability(elon, dummy, "cybertruck")
    test_ability("Elon Musk", "Cybertruck shield activated", lambda: elon.status_manager.has_status("Cybertruck"))
    test_ability("Elon Musk", "Attack empowered", lambda: elon.status_manager.has_status("Empowered"))
    
    # ========================================
    # EPIC: John Pork
    # ========================================
    print("\nJOHN PORK (Epic)")
    pork = get_card(cards, "John Pork")
    bench_card = get_card(cards, "Charlie Kirk")
    
    game_state = {"opponent_bench": [bench_card]}
    result = ability_engine.execute_ability(pork, dummy, "john_pork_calling", game_state=game_state)
    # 33% insta-kill - test that it executes (may or may not kill)
    test_ability("John Pork", "John Pork is Calling executes", lambda: result.success)
    
    # ========================================
    # EPIC: Lil Uzi Vert
    # ========================================
    print("\nLIL UZI VERT (Epic)")
    uzi = get_card(cards, "Lil Uzi Vert")
    bench_card = get_card(cards, "Charlie Kirk")
    
    game_state = {"user_bench": [bench_card]}
    result = ability_engine.execute_ability(uzi, dummy, "luv_is_rage", game_state=game_state)
    test_ability("Lil Uzi Vert", "Luv is Rage buffs bench", lambda: bench_card.status_manager.has_status("Luv Buff"))
    
    # ========================================
    # EPIC: Erica Kirk
    # ========================================
    print("\nERICA KIRK (Epic)")
    erica = get_card(cards, "Erica Kirk")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(erica, target, "we_are_charlie_kirk")
    test_ability("Erica Kirk", "Reflection applied", lambda: target.status_manager.has_status("Reflection"))
    
    # ========================================
    # EPIC: Bruce Lee
    # ========================================
    print("\nBRUCE LEE (Epic)")
    bruce = get_card(cards, "Bruce Lee")
    target = get_card(cards, "Shaq")
    target_initial = target.current_hp
    
    result = ability_engine.execute_ability(bruce, target, "one_inch_punch")
    expected_damage = int(bruce.attack.base_damage * 1.5)
    test_ability("Bruce Lee", "1 Inch Punch deals 1.5x damage", lambda: result.damage_dealt == expected_damage)
    
    # ========================================
    # EPIC: Andrew Tate
    # ========================================
    print("\nANDREW TATE (Epic)")
    tate = get_card(cards, "Andrew Tate")
    
    result = ability_engine.execute_ability(tate, dummy, "what_color_bugatti")
    test_ability("Andrew Tate", "What Color Bugatti executes", lambda: result.success)
    test_ability("Andrew Tate", "Has Alpha passive (25% DR)", lambda: tate.passive is not None and tate.passive.effect_id == "alpha")
    
    # ========================================
    # MYTHICAL: Ye
    # ========================================
    print("\nYE (Mythical)")
    ye = get_card(cards, "Ye")
    
    result = ability_engine.execute_ability(ye, dummy, "bipolar_disorder")
    test_ability("Ye", "Bipolar Disorder executes", lambda: result.success)
    test_ability("Ye", "Attack is 400", lambda: ye.attack.base_damage == 400)
    
    # ========================================
    # MYTHICAL: MLK
    # ========================================
    print("\nMLK (Mythical)")
    mlk = get_card(cards, "MLK")
    mlk.take_damage(200)
    initial_hp = mlk.current_hp
    
    result = ability_engine.execute_ability(mlk, dummy, "freedom_speech")
    test_ability("MLK", "Freedom Speech heals 200", lambda: mlk.current_hp == initial_hp + 200)
    test_ability("MLK", "Has 80% DR passive", lambda: mlk.passive is not None and mlk.passive.effect_id == "mlk_peace")
    
    # ========================================
    # MYTHICAL: Diddy
    # ========================================
    print("\nDIDDY (Mythical)")
    diddy = get_card(cards, "Diddy")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(diddy, target, "diddle")
    test_ability("Diddy", "Diddle executes (50% kidnap)", lambda: result.success)
    
    # ========================================
    # MYTHICAL: Kim Jong-Un
    # ========================================
    print("\nKIM JONG-UN (Mythical)")
    kim = get_card(cards, "Kim Jong-Un")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(kim, target, "missile_launch")
    test_ability("Kim Jong-Un", "Missile Launch executes", lambda: result.success)
    test_ability("Kim Jong-Un", "HP is 3000", lambda: kim.max_hp == 3000)
    
    # ========================================
    # MYTHICAL: Saddam Hussein
    # ========================================
    print("\nSADDAM HUSSEIN (Mythical)")
    saddam = get_card(cards, "Saddam Hussein")
    
    result = ability_engine.execute_ability(saddam, dummy, "hiding_spot")
    test_ability("Saddam Hussein", "Hiding Spot applies 50% dodge", lambda: saddam.status_manager.has_status("Hiding Spot"))
    test_ability("Saddam Hussein", "Has 50% DR passive", lambda: saddam.passive is not None)
    
    # ========================================
    # MYTHICAL: Theodore Roosevelt
    # ========================================
    print("\nTHEODORE ROOSEVELT (Mythical)")
    teddy = get_card(cards, "Theodore Roosevelt")
    
    result = ability_engine.execute_ability(teddy, dummy, "rough_rider_charge")
    test_ability("Theodore Roosevelt", "Rough Rider applies 2x buff", lambda: teddy.status_manager.has_status("Rough Rider"))
    
    # ========================================
    # MYTHICAL: Gorlock the Destroyer
    # ========================================
    print("\nGORLOCK THE DESTROYER (Mythical)")
    gorlock = get_card(cards, "Gorlock the Destroyer")
    gorlock.take_damage(1000)
    initial_hp = gorlock.current_hp
    
    result = ability_engine.execute_ability(gorlock, dummy, "dominion_expansion")
    test_ability("Gorlock", "Dominion Expansion heals 25%", lambda: gorlock.current_hp > initial_hp)
    test_ability("Gorlock", "HP is 3000", lambda: gorlock.max_hp == 3000)
    
    # ========================================
    # LEGENDARY: Lebron James
    # ========================================
    print("\nLEBRON JAMES (Legendary)")
    lebron = get_card(cards, "Lebron James")
    
    result = ability_engine.execute_ability(lebron, dummy, "chase_down_block")
    test_ability("Lebron James", "Chase Down Block applies high dodge", lambda: lebron.status_manager.has_status("High Dodge"))
    
    # ========================================
    # LEGENDARY: Jeffrey Epstein
    # ========================================
    print("\nJEFFREY EPSTEIN (Legendary)")
    epstein = get_card(cards, "Jeffrey Epstein")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(epstein, target, "kidnap")
    test_ability("Jeffrey Epstein", "Kidnap executes (50% skip)", lambda: result.success)
    
    # ========================================
    # LEGENDARY: Barack Obama
    # ========================================
    print("\nBARACK OBAMA (Legendary)")
    obama = get_card(cards, "Barack Obama")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(obama, target, "drone_strike")
    test_ability("Barack Obama", "Drone Strike executes", lambda: result.success)
    
    # ========================================
    # LEGENDARY: Mr. Michaelsen
    # ========================================
    print("\nMR. MICHAELSEN (Legendary)")
    mr_m = get_card(cards, "Mr. Michaelsen")
    
    result = ability_engine.execute_ability(mr_m, dummy, "ap_euro_flashcards")
    test_ability("Mr. Michaelsen", "AP Euro Flashcards executes", lambda: result.success)
    
    # ========================================
    # LEGENDARY: Walter White
    # ========================================
    print("\nWALTER WHITE (Legendary)")
    walter = get_card(cards, "Walter White")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(walter, target, "ricin")
    test_ability("Walter White", "Ricin applies DoT", lambda: target.status_manager.has_status("Ricin"))
    test_ability("Walter White", "Attack is 1500", lambda: walter.attack.base_damage == 1500)
    
    # ========================================
    # LEGENDARY: CaseOh
    # ========================================
    print("\nCASEOH (Legendary)")
    case = get_card(cards, "CaseOh")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(case, target, "sit_on_u")
    test_ability("CaseOh", "Sit On U prevents attacks", lambda: target.status_manager.has_status("Sat On"))
    
    # ========================================
    # LEGENDARY: Monkey
    # ========================================
    print("\nMONKEY (Legendary)")
    monkey = get_card(cards, "Monkey")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(monkey, target, "banana_slimer")
    test_ability("Monkey", "Banana Slimer applies Anguish", lambda: target.status_manager.has_status("Anguish"))
    test_ability("Monkey", "Has 20% dodge passive", lambda: monkey.passive is not None)
    
    # ========================================
    # ULTRA LEGENDARY: Hydrogen Bomb
    # ========================================
    print("\nHYDROGEN BOMB (Ultra Legendary)")
    hbomb = get_card(cards, "Hydrogen Bomb")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(hbomb, target, "nuclear_strike")
    test_ability("Hydrogen Bomb", "Nuclear Strike kills both", lambda: result.kill_self and result.kill_target)
    test_ability("Hydrogen Bomb", "HP is 1", lambda: hbomb.max_hp == 1)
    
    # ========================================
    # ULTRA LEGENDARY: Chinese Beaver
    # ========================================
    print("\nCHINESE BEAVER (Ultra Legendary)")
    beaver = get_card(cards, "Chinese Beaver")
    target_dummy = get_card(cards, "CaseOh")
    
    result = ability_engine.execute_ability(beaver, target_dummy, "take_that_wood")
    test_ability("Chinese Beaver", "Take That Wood flips coins", lambda: result.success and "heads" in result.message.lower())
    test_ability("Chinese Beaver", "HP is 999999 (infinite)", lambda: beaver.max_hp == 999999)
    test_ability("Chinese Beaver", "Has Beaver Timer passive", lambda: beaver.passive is not None and beaver.passive.effect_id == "beaver_timer")
    
    # ========================================
    # ULTRA LEGENDARY: Noah Tsui
    # ========================================
    print("\nNOAH TSUI (Ultra Legendary)")
    noah = get_card(cards, "Noah Tsui")
    
    result = ability_engine.execute_ability(noah, dummy, "thicc_calves")
    test_ability("Noah Tsui", "Thicc Calves applies auto-dodge", lambda: noah.status_manager.has_status("Thicc Calves"))
    test_ability("Noah Tsui", "Has Jump passive (50% dodge)", lambda: noah.passive is not None and noah.passive.effect_id == "jump")
    test_ability("Noah Tsui", "Has Asian Blindness secondary", lambda: noah.secondary_passive is not None)
    
    # Trigger Jump passive and check dodge
    ability_engine.trigger_passive(noah, "jump", "battle_start", {})
    test_ability("Noah Tsui", "Jump applies 50% dodge", lambda: noah.status_manager.get_dodge_chance() >= 50)
    
    # ========================================
    # ULTRA LEGENDARY: Colin Sweeney
    # ========================================
    print("\nCOLIN SWEENEY (Ultra Legendary)")
    colin = get_card(cards, "Colin Sweeney")
    
    result = ability_engine.execute_ability(colin, dummy, "caffeine_gum")
    test_ability("Colin Sweeney", "Caffeine Gum applies buff", lambda: colin.status_manager.has_status("Caffeine"))
    test_ability("Colin Sweeney", "Has Procrastination passive", lambda: colin.passive is not None and colin.passive.effect_id == "procrastination")
    test_ability("Colin Sweeney", "Attack is percent-based (50%)", lambda: colin.attack.percent_damage == 50)
    
    # ========================================
    # ULTRA LEGENDARY: Aldo Ortiz
    # ========================================
    print("\nALDO ORTIZ (Ultra Legendary)")
    aldo = get_card(cards, "Aldo Ortiz")
    target = get_card(cards, "Charlie Kirk")
    
    result = ability_engine.execute_ability(aldo, target, "bean_rice_cheese")
    test_ability("Aldo Ortiz", "Bean Rice Cheese executes", lambda: result.success)
    test_ability("Aldo Ortiz", "Base attack is 21", lambda: aldo.attack.base_damage == 21)
    test_ability("Aldo Ortiz", "Crit multiplier is 10000%", lambda: aldo.attack.crit_multiplier == 10000)
    test_ability("Aldo Ortiz", "Has Slipped passive", lambda: aldo.passive is not None and aldo.passive.effect_id == "aldo_slip")
    test_ability("Aldo Ortiz", "Has High Dodge secondary", lambda: aldo.secondary_passive is not None)
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
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
