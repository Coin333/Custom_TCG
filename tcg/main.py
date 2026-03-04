#!/usr/bin/env python3
"""
Terminal Chaos TCG - Main Entry Point
A chaotic, fast-paced terminal-based trading card game for 2 players.
"""
import os
import sys

# Add tcg directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from card import load_cards_from_json
from deck_builder import DeckBuilder, select_starting_cards
from engine import GameEngine, Player
from utils import (
    print_header, print_subheader, print_divider, print_error, print_success,
    Colors, clear_screen
)


def display_title_screen():
    """Display the game's title screen."""
    clear_screen()
    
    title = """
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║       ██████╗██╗   ██╗███████╗████████╗ ██████╗ ███╗   ███╗║
    ║      ██╔════╝██║   ██║██╔════╝╚══██╔══╝██╔═══██╗████╗ ████║║
    ║      ██║     ██║   ██║███████╗   ██║   ██║   ██║██╔████╔██║║
    ║      ██║     ██║   ██║╚════██║   ██║   ██║   ██║██║╚██╔╝██║║
    ║      ╚██████╗╚██████╔╝███████║   ██║   ╚██████╔╝██║ ╚═╝ ██║║
    ║       ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝║
    ║                                                            ║
    ║                      ████████╗ ██████╗ ██████╗             ║
    ║                      ╚══██╔══╝██╔════╝██╔════╝             ║
    ║                         ██║   ██║     ██║  ███╗            ║
    ║                         ██║   ██║     ██║   ██║            ║
    ║                         ██║   ╚██████╗╚██████╔╝            ║
    ║                         ╚═╝    ╚═════╝ ╚═════╝             ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """
    
    print(f"{Colors.HEADER}{title}{Colors.RESET}")
    print("                    A Chaotic Card Battle Experience")
    print("                         2 Player Local Game")
    print("\n" + "=" * 65)


def display_rules():
    """Display game rules."""
    clear_screen()
    print_header("HOW TO PLAY")
    
    print(f"""
{Colors.INFO}OBJECTIVE:{Colors.RESET}
  Be the first player to reach {Colors.WARNING}25 points{Colors.RESET} by KO'ing opponent cards!

{Colors.INFO}SETUP:{Colors.RESET}
  • Each player builds a 10-card deck
  • Select 1 Active card and 2 Bench cards
  • Remaining 7 cards form your deck pool

{Colors.INFO}TURN STRUCTURE:{Colors.RESET}
  1. Start of Turn - Status effects resolve
  2. Action Phase - Attack OR use Ability
  3. Combat Resolution - Damage calculated
  4. KO Check - Replace fallen cards

{Colors.INFO}SCORING (Points on KO):{Colors.RESET}
  • {Colors.BASIC}Basic: 1{Colors.RESET}    • {Colors.COMMON}Common: 2{Colors.RESET}    • {Colors.RARE}Rare: 3{Colors.RESET}
  • {Colors.EPIC}Epic: 5{Colors.RESET}     • {Colors.MYTHICAL}Mythical: 7{Colors.RESET}  • {Colors.LEGENDARY}Legendary: 10{Colors.RESET}
  • {Colors.ULTRA_LEGENDARY}Ultra Legendary: 15{Colors.RESET}

{Colors.INFO}DECK LIMITS:{Colors.RESET}
  • Ultra Legendary: 1    • Legendary: 2
  • Mythical: 2           • Epic: 2
  • Rare: 2               • Common/Basic: Unlimited

{Colors.INFO}ABILITIES:{Colors.RESET}
  • Each card has one ability
  • Active abilities can be used ONCE per card lifetime
  • Passive abilities are always active

{Colors.WARNING}REMEMBER: This game is CHAOTIC by design!{Colors.RESET}
  High damage, coin flips, and status stacking are all part of the fun.
""")
    
    input("\nPress Enter to continue...")


def get_player_names() -> tuple[str, str]:
    """Get player names."""
    clear_screen()
    print_header("PLAYER SETUP")
    
    print(f"\n{Colors.INFO}Enter player names:{Colors.RESET}\n")
    
    p1_name = input("Player 1 name: ").strip()
    if not p1_name:
        p1_name = "Player 1"
    
    p2_name = input("Player 2 name: ").strip()
    if not p2_name:
        p2_name = "Player 2"
    
    # Ensure names are different
    if p1_name == p2_name:
        p2_name = p2_name + " (2)"
    
    print_success(f"\nWelcome {p1_name} and {p2_name}!")
    input("Press Enter to continue...")
    
    return (p1_name, p2_name)


def main_menu() -> str:
    """Display main menu and get choice."""
    clear_screen()
    display_title_screen()
    
    print(f"\n{Colors.INFO}MAIN MENU{Colors.RESET}")
    print_divider("-", 30)
    print("  1. Start New Game")
    print("  2. View Rules")
    print("  3. Quick Game (Random Decks)")
    print("  4. Exit")
    print_divider("-", 30)
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        if choice in ["1", "2", "3", "4"]:
            return choice
        print_error("Invalid choice. Please enter 1-4.")


def run_game(quick_mode: bool = False):
    """Run a full game."""
    # Get player names
    p1_name, p2_name = get_player_names()
    
    # Load card pool
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cards_path = os.path.join(script_dir, "cards.json")
    
    try:
        # Load draftable cards for deck building
        card_pool = load_cards_from_json(cards_path)
        # Load all cards including transform-only for transformations
        all_cards = load_cards_from_json(cards_path, include_transform_only=True)
    except FileNotFoundError:
        print_error(f"Error: Could not find {cards_path}")
        print_error("Make sure cards.json is in the same directory as main.py")
        input("Press Enter to exit...")
        return
    except Exception as e:
        print_error(f"Error loading cards: {e}")
        input("Press Enter to exit...")
        return
    
    print_success(f"Loaded {len(card_pool)} cards!")
    
    # Deck building phase
    deck_builder = DeckBuilder(card_pool)
    
    if quick_mode:
        # Quick random decks
        clear_screen()
        print_header("Quick Game - Random Decks")
        
        deck_builder._quick_build()
        p1_deck = deck_builder.selected_cards.copy()
        deck_builder.reset()
        
        deck_builder._quick_build()
        p2_deck = deck_builder.selected_cards.copy()
        
        print_success(f"Generated random decks for both players!")
        input("Press Enter to continue...")
    else:
        # Manual deck building
        p1_deck = deck_builder.build_deck_interactive(p1_name)
        deck_builder.reset()
        p2_deck = deck_builder.build_deck_interactive(p2_name)
    
    # Starting selection phase
    clear_screen()
    print_header("STARTING SELECTION")
    print(f"\n{Colors.WARNING}Each player will now select their starting cards.{Colors.RESET}")
    print("You will choose 1 Active card and 2 Bench cards.")
    input("\nPress Enter when ready...")
    
    # Pass device prompt
    clear_screen()
    print_header(f"PASS DEVICE TO {p1_name.upper()}")
    print(f"\n{p1_name}, press Enter when ready to select your cards...")
    input()
    
    p1_active, p1_bench, p1_pool = select_starting_cards(p1_deck, p1_name)
    
    # Pass to P2
    clear_screen()
    print_header(f"PASS DEVICE TO {p2_name.upper()}")
    print(f"\n{p2_name}, press Enter when ready to select your cards...")
    input()
    
    p2_active, p2_bench, p2_pool = select_starting_cards(p2_deck, p2_name)
    
    # Create players
    player1 = Player(
        name=p1_name,
        deck_pool=p1_pool,
        active=p1_active,
        bench=p1_bench,
        score=0
    )
    
    player2 = Player(
        name=p2_name,
        deck_pool=p2_pool,
        active=p2_active,
        bench=p2_bench,
        score=0
    )
    
    # Initialize game engine with full card pool for transformations
    engine = GameEngine(player1, player2, card_pool=all_cards)
    
    # Coin flip for first player
    engine.coin_flip_starting_player()
    
    # Run the game
    engine.run_game()


def main():
    """Main entry point."""
    try:
        while True:
            choice = main_menu()
            
            if choice == "1":
                run_game(quick_mode=False)
            elif choice == "2":
                display_rules()
            elif choice == "3":
                run_game(quick_mode=True)
            elif choice == "4":
                clear_screen()
                print("\nThanks for playing Terminal Chaos TCG!")
                print("May chaos be ever in your favor.\n")
                break
    
    except KeyboardInterrupt:
        clear_screen()
        print("\n\nGame interrupted. Thanks for playing!")
        sys.exit(0)


if __name__ == "__main__":
    main()
