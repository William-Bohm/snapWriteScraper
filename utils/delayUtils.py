import time
import random
from typing import Tuple, Optional


def random_delay(min_seconds: float = 1.0, 
                max_seconds: float = 3.0, 
                human_factor: bool = True,
                verbose: bool = False) -> float:
    """
    Pause execution for a random amount of time to simulate human behavior
    
    Args:
        min_seconds: Minimum delay time in seconds
        max_seconds: Maximum delay time in seconds
        human_factor: Add human-like randomness to the delay pattern
        verbose: Whether to print the delay duration
        
    Returns:
        The actual sleep duration in seconds
    """
    # Ensure valid range
    if min_seconds < 0:
        min_seconds = 0
    if max_seconds < min_seconds:
        max_seconds = min_seconds + 1.0
    
    # Base random delay
    base_delay = random.uniform(min_seconds, max_seconds)
    
    # Add human-like variability if enabled
    if human_factor:
        # Occasionally add a bit more randomness (simulating distraction)
        if random.random() < 0.15:  # 15% chance
            base_delay += random.uniform(0.5, 2.0)
        
        # Very occasionally add a longer pause (simulating thinking)
        if random.random() < 0.05:  # 5% chance
            base_delay += random.uniform(1.0, 4.0)
    
    # Round to make logs more readable but keep 2 decimal points for variability
    sleep_duration = round(base_delay, 2)
    
    if verbose:
        print(f"Waiting for {sleep_duration}s...")
    
    # Perform the actual delay
    time.sleep(sleep_duration)
    
    return sleep_duration


def random_typing_delay(text: str, 
                       min_cps: float = 5.0, 
                       max_cps: float = 15.0,
                       verbose: bool = False) -> Tuple[str, float]:
    """
    Calculate a random delay to simulate human typing speed
    
    Args:
        text: The text being typed
        min_cps: Minimum characters per second
        max_cps: Maximum characters per second 
        verbose: Whether to print the typing speed
    
    Returns:
        The text and total sleep duration
    """
    if not text:
        return text, 0.0
    
    # Ensure valid range
    if min_cps <= 0:
        min_cps = 5.0
    if max_cps <= min_cps:
        max_cps = min_cps + 10.0
    
    # Random typing speed in this range
    chars_per_second = random.uniform(min_cps, max_cps)
    
    # Calculate total typing time
    total_time = len(text) / chars_per_second
    
    if verbose:
        print(f"Typing '{text}' at {round(chars_per_second, 1)} chars/second ({round(total_time, 2)}s)")
    
    return text, total_time


def human_like_delay(action_type: str = "general", verbose: bool = True) -> float:
    """
    Add a human-like delay based on the type of action being performed
    
    Args:
        action_type: Type of action ('navigate', 'click', 'type', 'search', 'read', 'general')
        verbose: Whether to print the delay information
        
    Returns:
        The actual sleep duration in seconds
    """
    delay_ranges = {
        "navigate": (1.5, 3.5),     # Page navigation delay
        "click": (0.3, 1.2),        # Clicking a button/link
        "type": (0.5, 1.5),         # Before typing
        "search": (1.0, 2.5),       # After search submission
        "read": (2.0, 5.0),         # Simulating reading content
        "scroll": (0.7, 2.0),       # After scrolling
        "general": (0.5, 2.0)       # Default delay
    }
    
    # Get the delay range for the specified action type
    action_range = delay_ranges.get(action_type.lower(), delay_ranges["general"])
    
    # Add a descriptive message if verbose
    if verbose:
        action_messages = {
            "navigate": "Waiting for page to load",
            "click": "Preparing to click",
            "type": "Getting ready to type",
            "search": "Waiting for search results",
            "read": "Reading content",
            "scroll": "Pausing after scrolling",
            "general": "Waiting briefly"
        }
        message = action_messages.get(action_type.lower(), "Waiting")
        print(f"{message}...")
    
    # Use the basic random delay function
    return random_delay(
        min_seconds=action_range[0],
        max_seconds=action_range[1],
        human_factor=True,
        verbose=verbose
    )


def get_random_scroll_size(min_pixels: int = 300, 
                          max_pixels: int = 800,
                          human_factor: bool = True) -> int:
    """
    Get a random scroll distance to simulate human-like scrolling
    
    Args:
        min_pixels: Minimum scroll distance in pixels
        max_pixels: Maximum scroll distance in pixels
        human_factor: Add human-like variability to scroll distance
        
    Returns:
        Scroll distance in pixels
    """
    # Base random scroll distance
    scroll_distance = random.randint(min_pixels, max_pixels)
    
    # Add human-like variability if enabled
    if human_factor:
        # Occasionally do a small scroll
        if random.random() < 0.2:  # 20% chance
            scroll_distance = random.randint(100, 250)
        
        # Occasionally do a larger scroll
        if random.random() < 0.1:  # 10% chance
            scroll_distance = random.randint(max_pixels, max_pixels * 1.5)
            
        # Very occasionally do a much larger scroll
        if random.random() < 0.05:  # 5% chance
            scroll_distance = random.randint(max_pixels * 1.5, max_pixels * 2.5)
    
    return int(scroll_distance)


def scroll_down_pause(driver, 
                     scroll_size: Optional[int] = None, 
                     scroll_pause_time: Optional[float] = None,
                     verbose: bool = True) -> Tuple[int, float]:
    """
    Scroll down with a human-like pause
    
    Args:
        driver: Selenium WebDriver instance
        scroll_size: Scroll distance in pixels (if None, a random size is chosen)
        scroll_pause_time: Pause time in seconds (if None, a random time is chosen)
        verbose: Whether to print scroll information
        
    Returns:
        Tuple of (scroll_size, pause_time)
    """
    # Get random scroll size if not provided
    if scroll_size is None:
        scroll_size = get_random_scroll_size()
    
    # Execute scroll
    if verbose:
        print(f"Scrolling down {scroll_size} pixels...")
    
    # Use JavaScript to scroll
    driver.execute_script(f"window.scrollBy(0, {scroll_size});")
    
    # Pause after scrolling
    if scroll_pause_time is None:
        scroll_pause_time = human_like_delay("scroll", verbose=verbose)
    else:
        time.sleep(scroll_pause_time)
        
    return scroll_size, scroll_pause_time 