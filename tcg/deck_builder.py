"""
Deck Building System for Terminal Chaos TCG
Handles deck selection, validation, and starting card selection
"""
from card import Card, load_cards_from_json, validate_deck
from utils import (
    RARITY_COLORS, RARITY_LIMITS, RARITY_POINTS,
    print_header, print_subheader, print_divider, print_error, print_success, print_warning,
    colorize, Colors, clear_screen, get_numeric_input
)


class DeckBuilder:
    """
    Interactive deck building interface.
    Allows players to select 10 cards for their deck.
    """
    
    def __init__(self, card_pool: list[Card]):
        """
        Initialize deck builder.
        
        Args:
            card_pool: List of all available cards
        """
        self.card_pool = card_pool
        self.selected_cards: list[Card] = []
        self.rarity_counts: dict[str, int] = {}
    
    def reset(self):
        """Reset deck builder state."""
        self.selected_cards = []
        self.rarity_counts = {}
    
    def get_remaining_slots(self) -> int:
        """Get number of remaining deck slots."""
        return 10 - len(self.selected_cards)
    
    def can_add_rarity(self, rarity: str) -> bool:
        """Check if another card of this rarity can be added."""
        current = self.rarity_counts.get(rarity, 0)
        limit = RARITY_LIMITS.get(rarity, float('inf'))
        return current < limit
    
    def add_card(self, card: Card) -> tuple[bool, str]:
        """
        Add a card to the deck.
        
        Args:
            card: Card to add
            
        Returns:
            Tuple of (success, message)
        """
        # Check deck size
        if len(self.selected_cards) >= 10:
            return (False, "Deck is full (10 cards)")
        
        # Check rarity limit
        if not self.can_add_rarity(card.rarity):
            limit = RARITY_LIMITS.get(card.rarity, 0)
            return (False, f"Cannot add more {card.rarity} cards (limit: {int(limit)})")
        
        # Add card (create a copy)
        self.selected_cards.append(card.copy())
        self.rarity_counts[card.rarity] = self.rarity_counts.get(card.rarity, 0) + 1
        
        return (True, f"Added {card.name} to deck")
    
    def remove_card(self, index: int) -> tuple[bool, str]:
        """
        Remove a card from the deck by index.
        
        Args:
            index: Index of card to remove (0-based)
            
        Returns:
            Tuple of (success, message)
        """
        if index < 0 or index >= len(self.selected_cards):
            return (False, "Invalid card index")
        
        card = self.selected_cards.pop(index)
        self.rarity_counts[card.rarity] -= 1
        
        return (True, f"Removed {card.name} from deck")
    
    def get_available_cards(self) -> list[Card]:
        """Get list of cards that can still be added."""
        available = []
        for card in self.card_pool:
            if self.can_add_rarity(card.rarity):
                available.append(card)
        return available
    
    def display_card_pool(self, filter_rarity: str = None):
        """Display available cards grouped by rarity."""
        print_subheader("Available Cards")
        
        # Group by rarity
        rarities = ["Basic", "Common", "Rare", "Epic", "Mythical", "Legendary", "Ultra Legendary"]
        
        index = 1
        card_index_map = {}
        
        for rarity in rarities:
            if filter_rarity and filter_rarity != rarity:
                continue
                
            cards = [c for c in self.card_pool if c.rarity == rarity]
            if not cards:
                continue
            
            # Show rarity header with limit info
            current = self.rarity_counts.get(rarity, 0)
            limit = RARITY_LIMITS.get(rarity, float('inf'))
            limit_str = "unlimited" if limit == float('inf') else str(int(limit))
            can_add = self.can_add_rarity(rarity)
            
            color = RARITY_COLORS.get(rarity, Colors.RESET)
            status = f"{Colors.SUCCESS}[{current}/{limit_str}]" if can_add else f"{Colors.ERROR}[FULL {current}/{limit_str}]"
            print(f"\n{color}{Colors.BOLD}=== {rarity} ==={Colors.RESET} {status}{Colors.RESET}")
            
            for card in cards:
                if can_add:
                    print(f"  {index}. {card.get_summary_string()}")
                    card_index_map[index] = card
                    index += 1
                else:
                    print(f"  {Colors.ERROR}X{Colors.RESET}  {card.get_summary_string()}")
        
        return card_index_map
    
    def display_current_deck(self):
        """Display current deck contents."""
        print_subheader(f"Your Deck ({len(self.selected_cards)}/10)")
        
        if not self.selected_cards:
            print("  (Empty)")
            return
        
        for i, card in enumerate(self.selected_cards, 1):
            points = RARITY_POINTS.get(card.rarity, 1)
            print(f"  {i}. {card.get_summary_string()} [{points} pts if KO'd]")
        
        # Show rarity breakdown
        print_divider("-", 40)
        print("Rarity counts:", end=" ")
        parts = []
        for rarity in ["Ultra Legendary", "Legendary", "Mythical", "Epic", "Rare", "Common", "Basic"]:
            count = self.rarity_counts.get(rarity, 0)
            if count > 0:
                parts.append(f"{colorize(rarity, rarity)}: {count}")
        print(", ".join(parts) if parts else "None")
    
    def build_deck_interactive(self, player_name: str) -> list[Card]:
        """
        Interactive deck building for a player.
        
        Args:
            player_name: Name of the player building
            
        Returns:
            Completed deck (list of 10 cards)
        """
        self.reset()
        
        while len(self.selected_cards) < 10:
            clear_screen()
            print_header(f"{player_name}'s Deck Building")
            
            # Show current deck
            self.display_current_deck()
            
            # Show available cards
            card_map = self.display_card_pool()
            
            print_divider("=")
            slots_left = 10 - len(self.selected_cards)
            print(f"\n{Colors.INFO}Slots remaining: {slots_left}{Colors.RESET}")
            print("\nOptions:")
            print("  [1-N] Add card by number")
            print("  [R]   Remove a card from deck")
            print("  [A]   Auto-fill remaining slots randomly")
            print("  [Q]   Quick build (random deck)")
            print("  [L]   Quick list (enter card numbers/names separated by commas)")
            
            choice = input("\nYour choice: ").strip().upper()
            
            if choice == 'R':
                # Remove card
                if self.selected_cards:
                    try:
                        idx = int(input("Enter card number to remove (1-based): ")) - 1
                        success, msg = self.remove_card(idx)
                        if success:
                            print_success(msg)
                        else:
                            print_error(msg)
                        input("Press Enter to continue...")
                    except ValueError:
                        print_error("Invalid number")
                        input("Press Enter to continue...")
                else:
                    print_warning("Deck is empty")
                    input("Press Enter to continue...")
            
            elif choice == 'A':
                # Auto-fill remaining slots
                self._auto_fill()
                print_success("Auto-filled remaining slots!")
                input("Press Enter to continue...")
            
            elif choice == 'Q':
                # Quick random build
                self.reset()
                self._quick_build()
                print_success("Generated random deck!")
                input("Press Enter to continue...")
            
            elif choice == 'L':
                # Quick list - enter cards separated by commas
                self._quick_list_build(card_map)
            
            else:
                # Try to add by number
                try:
                    num = int(choice)
                    if num in card_map:
                        card = card_map[num]
                        success, msg = self.add_card(card)
                        if success:
                            print_success(msg)
                        else:
                            print_error(msg)
                        input("Press Enter to continue...")
                    else:
                        print_error(f"Invalid card number: {num}")
                        input("Press Enter to continue...")
                except ValueError:
                    print_error("Invalid input")
                    input("Press Enter to continue...")
        
        # Validate final deck
        is_valid, error = validate_deck(self.selected_cards)
        if not is_valid:
            print_error(f"Deck validation error: {error}")
            # This shouldn't happen if our logic is correct
        
        # Show final deck
        clear_screen()
        print_header(f"{player_name}'s Final Deck")
        self.display_current_deck()
        print_success("\nDeck building complete!")
        input("Press Enter to continue...")
        
        return self.selected_cards.copy()
    
    def _auto_fill(self):
        """Auto-fill remaining deck slots with available cards."""
        import random
        
        while len(self.selected_cards) < 10:
            available = self.get_available_cards()
            if not available:
                break
            
            card = random.choice(available)
            self.add_card(card)
    
    def _quick_build(self):
        """Build a random valid deck quickly."""
        import random
        
        # Shuffle pool and try to add cards
        shuffled = random.sample(self.card_pool, len(self.card_pool))
        
        for card in shuffled:
            if len(self.selected_cards) >= 10:
                break
            self.add_card(card)
        
        # Fill remaining if needed
        self._auto_fill()
    
    def _quick_list_build(self, card_map: dict):
        """
        Build deck from a comma-separated list of card numbers or names.
        
        Args:
            card_map: Dict mapping numbers to cards from display_card_pool
        """
        print(f"\n{Colors.INFO}Quick List Mode{Colors.RESET}")
        print("Enter card numbers or names separated by commas.")
        print("Example: '1, 5, 12, Noah Tsui, CaseOh'")
        print(f"You need {10 - len(self.selected_cards)} more cards.")
        print("Type 'cancel' to go back.\n")
        
        # Build name lookup
        name_to_card = {card.name.lower(): card for card in self.card_pool}
        
        while True:
            user_input = input("Cards: ").strip()
            
            if user_input.lower() == 'cancel':
                print_warning("Cancelled quick list.")
                input("Press Enter to continue...")
                return
            
            # Parse the input
            items = [item.strip() for item in user_input.split(',')]
            
            # Save current state in case we need to rollback
            saved_cards = self.selected_cards.copy()
            saved_counts = self.rarity_counts.copy()
            
            errors = []
            added = []
            
            for item in items:
                if not item:
                    continue
                    
                card = None
                
                # Try as number first
                try:
                    num = int(item)
                    if num in card_map:
                        card = card_map[num]
                    else:
                        errors.append(f"Invalid number: {num}")
                        continue
                except ValueError:
                    # Try as card name (case-insensitive)
                    card_name_lower = item.lower()
                    if card_name_lower in name_to_card:
                        card = name_to_card[card_name_lower]
                    else:
                        # Try partial match
                        matches = [c for c in self.card_pool if card_name_lower in c.name.lower()]
                        if len(matches) == 1:
                            card = matches[0]
                        elif len(matches) > 1:
                            errors.append(f"'{item}' matches multiple cards: {', '.join(m.name for m in matches[:3])}")
                            continue
                        else:
                            errors.append(f"Card not found: '{item}'")
                            continue
                
                if card:
                    # Check if we can add this card
                    success, msg = self.add_card(card)
                    if success:
                        added.append(card.name)
                    else:
                        errors.append(f"{card.name}: {msg}")
            
            # Show results
            if added:
                print_success(f"Added {len(added)} cards: {', '.join(added)}")
            
            if errors:
                print_error("Errors:")
                for err in errors:
                    print(f"  - {err}")
                
                # Ask if they want to keep partial additions or retry
                if added:
                    keep = input(f"\nKeep the {len(added)} successfully added cards? (y/n): ").strip().lower()
                    if keep != 'y':
                        # Rollback
                        self.selected_cards = saved_cards
                        self.rarity_counts = saved_counts
                        print_warning("Rolled back changes. Try again.")
                        continue
                else:
                    print_warning("No cards were added. Try again.")
                    continue
            
            # Check if deck is complete
            if len(self.selected_cards) >= 10:
                print_success("Deck complete!")
            else:
                print(f"Deck has {len(self.selected_cards)}/10 cards.")
            
            input("Press Enter to continue...")
            return


def select_starting_cards(deck: list[Card], player_name: str) -> tuple[Card, list[Card], list[Card]]:
    """
    Allow player to select their starting Active and Bench cards.
    
    Args:
        deck: Player's 10-card deck
        player_name: Player's name
        
    Returns:
        Tuple of (active_card, bench_cards, remaining_deck_pool)
    """
    clear_screen()
    print_header(f"{player_name}'s Starting Selection")
    
    # Display all cards in deck
    print_subheader("Your Deck")
    for i, card in enumerate(deck, 1):
        print(f"  {i}. {card.get_summary_string()}")
    
    print_divider("=")
    print(f"\n{Colors.INFO}Select 1 Active card and 2 Bench cards.{Colors.RESET}")
    print("The remaining 7 cards will be your deck pool.\n")
    
    # Select Active card
    print(f"{Colors.WARNING}Select your ACTIVE card (1-10):{Colors.RESET}")
    active_idx = get_numeric_input("Active card: ", 1, 10) - 1
    active_card = deck[active_idx]
    print_success(f"Active: {active_card.name}")
    
    # Select Bench cards
    available_indices = [i for i in range(10) if i != active_idx]
    print(f"\n{Colors.WARNING}Select your first BENCH card:{Colors.RESET}")
    print("Available:", ", ".join(str(i+1) for i in available_indices))
    
    while True:
        bench1_idx = get_numeric_input("Bench card 1: ", 1, 10) - 1
        if bench1_idx in available_indices:
            break
        print_error("That card is already selected!")
    
    bench1 = deck[bench1_idx]
    print_success(f"Bench 1: {bench1.name}")
    
    available_indices.remove(bench1_idx)
    print(f"\n{Colors.WARNING}Select your second BENCH card:{Colors.RESET}")
    print("Available:", ", ".join(str(i+1) for i in available_indices))
    
    while True:
        bench2_idx = get_numeric_input("Bench card 2: ", 1, 10) - 1
        if bench2_idx in available_indices:
            break
        print_error("That card is already selected!")
    
    bench2 = deck[bench2_idx]
    print_success(f"Bench 2: {bench2.name}")
    
    # Create remaining deck pool
    selected_indices = {active_idx, bench1_idx, bench2_idx}
    remaining = [deck[i] for i in range(10) if i not in selected_indices]
    
    # Show summary
    print_divider("=")
    print(f"\n{Colors.SUCCESS}Selection Complete!{Colors.RESET}")
    print(f"  Active: {active_card.get_colored_name()}")
    print(f"  Bench:  {bench1.get_colored_name()}, {bench2.get_colored_name()}")
    print(f"  Deck Pool: {len(remaining)} cards remaining")
    
    input("\nPress Enter to continue...")
    
    return (active_card, [bench1, bench2], remaining)
