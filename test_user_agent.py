#!/usr/bin/env python
import os
import sys

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.userAgentRotation import (
    get_random_user_agent,
    get_desktop_user_agent,
    get_mobile_user_agent
)

def test_user_agent_rotation():
    print("Testing user agent rotation functionality:")
    print("-" * 50)
    
    # Test random user agents from different browsers
    print("1. Random user agents by browser type:")
    print(f"All browsers: {get_random_user_agent()}")
    print(f"Chrome: {get_random_user_agent('chrome')}")
    print(f"Firefox: {get_random_user_agent('firefox')}")
    print(f"Safari: {get_random_user_agent('safari')}")
    print(f"Edge: {get_random_user_agent('edge')}")
    print(f"Mobile: {get_random_user_agent('mobile')}")
    
    print("\n2. Testing desktop-specific agents:")
    for i in range(3):
        print(f"Desktop agent {i+1}: {get_desktop_user_agent()}")
        
    print("\n3. Testing mobile-specific agents:")
    for i in range(3):
        print(f"Mobile agent {i+1}: {get_mobile_user_agent()}")
    
    print("\n4. Testing rotation (should not have duplicates):")
    used_agents = set()
    for i in range(10):
        agent = get_random_user_agent()
        is_duplicate = agent in used_agents
        used_agents.add(agent)
        print(f"Agent {i+1}: {'[DUPLICATE]' if is_duplicate else '[NEW]'} {agent[:60]}...")
    
    print("\nTest completed.")


if __name__ == "__main__":
    test_user_agent_rotation() 