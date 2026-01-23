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
def start_game():
    print("Starting game...")
main_menu()