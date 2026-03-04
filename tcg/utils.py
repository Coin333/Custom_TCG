"""
Utility functions for Terminal Chaos TCG
Includes: RNG system, ANSI color codes, display helpers
"""
import random


# ============================================
# ANSI COLOR CODES FOR TERMINAL OUTPUT
# ============================================
class Colors:
    """ANSI escape codes for terminal colors"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Rarity colors
    BASIC = "\033[97m"          # White
    COMMON = "\033[92m"         # Green
    RARE = "\033[94m"           # Blue
    EPIC = "\033[95m"           # Magenta
    MYTHICAL = "\033[91m"       # Red
    LEGENDARY = "\033[93m"      # Yellow
    ULTRA_LEGENDARY = "\033[95;1m"  # Bright Magenta
    
    # UI colors
    HEADER = "\033[96m"         # Cyan
    WARNING = "\033[93m"        # Yellow
    ERROR = "\033[91m"          # Red
    SUCCESS = "\033[92m"        # Green
    INFO = "\033[94m"           # Blue


# Rarity to color mapping
RARITY_COLORS = {
    "Basic": Colors.BASIC,
    "Common": Colors.COMMON,
    "Rare": Colors.RARE,
    "Epic": Colors.EPIC,
    "Mythical": Colors.MYTHICAL,
    "Legendary": Colors.LEGENDARY,
    "Ultra Legendary": Colors.ULTRA_LEGENDARY
}

# Rarity to points mapping
RARITY_POINTS = {
    "Basic": 1,
    "Common": 2,
    "Rare": 3,
    "Epic": 5,
    "Mythical": 7,
    "Legendary": 10,
    "Ultra Legendary": 15
}

# Deck building limits
RARITY_LIMITS = {
    "Ultra Legendary": 1,
    "Legendary": 2,
    "Mythical": 2,
    "Epic": 2,
    "Rare": 2,
    "Common": float('inf'),  # Unlimited
    "Basic": float('inf')    # Unlimited
}


# ============================================
# RANDOMNESS ENGINE (CENTRALIZED)
# ============================================
def roll(chance_percent: float) -> bool:
    """
    Roll for a percentage chance.
    
    Args:
        chance_percent: Chance (0-100) of returning True
        
    Returns:
        True if roll succeeds, False otherwise
    """
    return random.random() < chance_percent / 100


def coin() -> str:
    """
    Flip a coin.
    
    Returns:
        "heads" or "tails"
    """
    return random.choice(["heads", "tails"])


def random_choice(items: list):
    """
    Select a random item from a list.
    
    Args:
        items: List to choose from
        
    Returns:
        Random item from the list
    """
    if not items:
        return None
    return random.choice(items)


def shuffle(items: list) -> list:
    """
    Shuffle a list and return it.
    
    Args:
        items: List to shuffle
        
    Returns:
        Shuffled copy of the list
    """
    result = items.copy()
    random.shuffle(result)
    return result


# ============================================
# DISPLAY HELPERS
# ============================================
def colorize(text: str, rarity: str) -> str:
    """
    Apply rarity color to text.
    
    Args:
        text: Text to colorize
        rarity: Rarity level
        
    Returns:
        Colored string with ANSI codes
    """
    color = RARITY_COLORS.get(rarity, Colors.RESET)
    return f"{color}{text}{Colors.RESET}"


def print_divider(char: str = "-", length: int = 50):
    """Print a divider line."""
    print(char * length)


def print_header(text: str):
    """Print a styled header."""
    print_divider("=")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(50)}{Colors.RESET}")
    print_divider("=")


def print_subheader(text: str):
    """Print a styled subheader."""
    print(f"\n{Colors.INFO}{text}{Colors.RESET}")
    print_divider("-", 40)


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.SUCCESS}{text}{Colors.RESET}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}{text}{Colors.RESET}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.ERROR}{text}{Colors.RESET}")


def clear_screen():
    """Clear the terminal screen."""
    print("\033[H\033[J", end="")


def get_valid_input(prompt: str, valid_options: list, allow_multiple: bool = False) -> str:
    """
    Get validated user input.
    
    Args:
        prompt: Input prompt to display
        valid_options: List of valid input options
        allow_multiple: If True, accept comma-separated values
        
    Returns:
        User's validated choice(s)
    """
    while True:
        user_input = input(prompt).strip()
        
        if allow_multiple:
            choices = [c.strip() for c in user_input.split(",")]
            if all(c in valid_options for c in choices):
                return choices
            print_error(f"Invalid selection. Valid options: {', '.join(valid_options)}")
        else:
            if user_input in valid_options:
                return user_input
            print_error(f"Invalid selection. Valid options: {', '.join(valid_options)}")


def get_numeric_input(prompt: str, min_val: int, max_val: int) -> int:
    """
    Get a numeric input within a range.
    
    Args:
        prompt: Input prompt
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Valid integer in range
    """
    while True:
        try:
            user_input = int(input(prompt).strip())
            if min_val <= user_input <= max_val:
                return user_input
            print_error(f"Please enter a number between {min_val} and {max_val}")
        except ValueError:
            print_error("Please enter a valid number")


def format_hp(current: int, max_hp: int) -> str:
    """Format HP display with color based on health percentage."""
    percent = current / max_hp if max_hp > 0 else 0
    
    if percent > 0.6:
        color = Colors.SUCCESS
    elif percent > 0.3:
        color = Colors.WARNING
    else:
        color = Colors.ERROR
    
    return f"{color}{current} / {max_hp}{Colors.RESET}"


def format_status_list(statuses: list) -> str:
    """Format status effects for display."""
    if not statuses:
        return "None"
    
    status_strs = []
    for status in statuses:
        if status.duration > 0:
            status_strs.append(f"{status.name} ({status.duration})")
        else:
            status_strs.append(status.name)
    
    return ", ".join(status_strs)


# ============================================
# BALANCE CAPS (Safety limits)
# ============================================
CAPS = {
    "damage_reduction": 80,      # Max 80% damage reduction
    "dodge": 75,                 # Max 75% dodge chance (Aldo Ortiz has 75%)
    "critical_multiplier": 10000,  # Max 10000% crit multiplier (100x for Aldo)
}


def apply_cap(value: float, cap_type: str) -> float:
    """
    Apply safety caps to prevent infinite stacking.
    
    Args:
        value: Current value
        cap_type: Type of cap to apply
        
    Returns:
        Capped value
    """
    if cap_type in CAPS:
        return min(value, CAPS[cap_type])
    return value
