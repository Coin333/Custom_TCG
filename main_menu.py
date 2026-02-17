import random
import json
import pygame
import os

def main_menu():
    running = True

    while running:
        print("\n=== CARD GAME ===")
        print("1. Start Game")
        print("2. Rules")
        print("3. Quit")

        choice = input("> ").strip()

        if choice == "1":
            start_game()
        elif choice == "2":
            show_rules()
        elif choice == "3":
            running = False
        else:
            print("Invalid choice. Try again.")

    print("Game closed cleanly 👋")
def show_rules():
    """Display game rules and mechanics."""
    print("\n" + "="*50)
    print("GAME RULES")
    print("="*50)
    print("\nOBJECTIVE:")
    print("Defeat your opponent by reducing all their cards' HP to 0!")
    print("\nCARD STATS:")
    print("- Damage: Base attack power")
    print("- HP: Health points (card dies at 0)")
    print("- Damage Reduction: % of damage blocked")
    print("- Dodge: Chance to avoid attacks")
    print("- Double Hit: Chance to attack twice")
    print("- True Damage: % of opponent HP (ignores damage reduction)")
    print("\nTRAITS:")
    print("- Short/Tall: Height traits")
    print("- Male/Female: Gender traits")
    print("- African American: +5% dodge")
    print("- Chuzz: +10% double hit chance")
    print("- Fat: -5% dodge")
    print("\nABILITIES:")
    print("Each card has a unique ability that activates during combat!")
    print("Abilities can deal extra damage, heal, or apply special effects.")
    print("\nCOMBAT:")
    print("1. Cards attack each other simultaneously")
    print("2. Abilities may activate based on their chance")
    print("3. Damage is reduced by damage reduction")
    print("4. True damage bypasses damage reduction")
    print("5. Cards with 0 HP are defeated")
    print("\n" + "="*50)
    input("\nPress Enter to return to menu...")

def start_game():
    """Start a new game."""
    from game import game
    game()

if __name__ == "__main__":
    main_menu()
