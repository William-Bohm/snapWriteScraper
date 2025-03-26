import random
from typing import List, Dict, Optional


class UserAgentRotator:
    """Utility class for generating and rotating realistic user agents"""
    
    def __init__(self):
        # Chrome user agents (Windows, macOS, Linux)
        self.chrome_agents = [
            # Windows Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            # macOS Chrome
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            # Linux Chrome
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]
        
        # Firefox user agents
        self.firefox_agents = [
            # Windows Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
            # macOS Firefox
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:119.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:118.0) Gecko/20100101 Firefox/118.0",
            # Linux Firefox
            "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:119.0) Gecko/20100101 Firefox/119.0",
        ]
        
        # Safari user agents (macOS only)
        self.safari_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        ]
        
        # Edge user agents
        self.edge_agents = [
            # Windows Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.2151.97",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76",
            # macOS Edge
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.2151.97",
        ]
        
        # Mobile user agents (iOS and Android)
        self.mobile_agents = [
            # iOS Safari
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            # Android Chrome
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
        ]
        
        # Combine all user agents into one dictionary
        self.user_agents: Dict[str, List[str]] = {
            "chrome": self.chrome_agents,
            "firefox": self.firefox_agents,
            "safari": self.safari_agents,
            "edge": self.edge_agents,
            "mobile": self.mobile_agents,
            "all": (self.chrome_agents + self.firefox_agents + 
                   self.safari_agents + self.edge_agents + self.mobile_agents)
        }
        
        # Keep track of used user agents to avoid repetition
        self.used_agents = set()
        
    def get_random_user_agent(self, browser_type: str = "all", avoid_duplicates: bool = True) -> str:
        """
        Get a random user agent string from the specified browser type
        
        Args:
            browser_type: Type of browser to get user agent for 
                          ('chrome', 'firefox', 'safari', 'edge', 'mobile', or 'all')
            avoid_duplicates: Whether to avoid returning recently used user agents
            
        Returns:
            A random user agent string
        """
        # Get the list of user agents for the specified browser type
        browser_type = browser_type.lower()
        if browser_type not in self.user_agents:
            browser_type = "all"
        
        available_agents = self.user_agents[browser_type]
        
        if avoid_duplicates and len(self.used_agents) >= len(available_agents):
            # If we've used all agents, reset the used agents list
            self.used_agents.clear()
        
        # Get unused agents
        unused_agents = [agent for agent in available_agents if agent not in self.used_agents]
        
        # If all agents have been used or we're not avoiding duplicates, use all available agents
        if not unused_agents:
            unused_agents = available_agents
        
        # Select a random user agent
        user_agent = random.choice(unused_agents)
        
        # Add to used agents if avoiding duplicates
        if avoid_duplicates:
            self.used_agents.add(user_agent)
        
        return user_agent
    
    def get_desktop_user_agent(self) -> str:
        """Get a random desktop user agent (no mobile)"""
        desktop_types = ["chrome", "firefox", "safari", "edge"]
        browser_type = random.choice(desktop_types)
        return self.get_random_user_agent(browser_type)
    
    def get_mobile_user_agent(self) -> str:
        """Get a random mobile user agent"""
        return self.get_random_user_agent("mobile")


# Create a singleton instance for easy import
user_agent_rotator = UserAgentRotator()


def get_random_user_agent(browser_type: str = "all") -> str:
    """
    Get a random user agent string
    
    Args:
        browser_type: Type of browser to get user agent for 
                      ('chrome', 'firefox', 'safari', 'edge', 'mobile', or 'all')
    
    Returns:
        A random user agent string
    """
    return user_agent_rotator.get_random_user_agent(browser_type)


def get_desktop_user_agent() -> str:
    """Get a random desktop user agent string (no mobile)"""
    return user_agent_rotator.get_desktop_user_agent()


def get_mobile_user_agent() -> str:
    """Get a random mobile user agent string"""
    return user_agent_rotator.get_mobile_user_agent()


# Example usage
if __name__ == "__main__":
    # Print a few random user agents
    print("Random user agent:", get_random_user_agent())
    print("Random Chrome user agent:", get_random_user_agent("chrome"))
    print("Random Firefox user agent:", get_random_user_agent("firefox"))
    print("Random desktop user agent:", get_desktop_user_agent())
    print("Random mobile user agent:", get_mobile_user_agent())
