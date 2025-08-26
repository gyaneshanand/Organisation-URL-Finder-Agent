#!/usr/bin/env python3
"""
Test script for the new prompt provider functionality.
"""

from prompt_provider import PromptProvider
from modular_url_agent import ModularURLAgent

def test_prompt_provider():
    """Test the prompt provider functionality."""
    print("🧪 Testing Prompt Provider")
    print("="*50)
    
    # Test listing all variations
    print("1. Listing all available variations:")
    PromptProvider.list_all_variations()
    
    # Test getting specific prompts
    print("\n2. Testing specific prompt retrieval:")
    for i in [1, 2, 3, 4]:
        print(f"\n--- Variation {i} ---")
        prompt = PromptProvider.get_prompt(i, "Google Search")
        print(f"Length: {len(prompt)} characters")
        print(f"First 100 chars: {prompt[:100]}...")
    
    # Test invalid variation
    print("\n3. Testing invalid variation:")
    prompt = PromptProvider.get_prompt(99, "Test Provider")
    print(f"Invalid variation result: {prompt[:50]}...")
    
    print("\n✅ Prompt Provider tests completed!")

def test_agent_with_variations():
    """Test the agent with different prompt variations."""
    print("\n🤖 Testing Agent with Prompt Variations")
    print("="*50)
    
    # Create agent with variation 1
    agent = ModularURLAgent(prompt_variation=1)
    
    # Test current prompt info
    info = agent.get_current_prompt_info()
    print(f"Current prompt info: {info}")
    
    # Test switching variations
    for variation in [2, 3, 4, 1]:
        print(f"\n🔄 Switching to variation {variation}")
        agent.switch_prompt_variation(variation)
        current_info = agent.get_current_prompt_info()
        print(f"Current variation: {current_info['variation']}")
        print(f"Description: {current_info['description']}")
    
    print("\n✅ Agent variation tests completed!")

if __name__ == "__main__":
    test_prompt_provider()
    test_agent_with_variations()
