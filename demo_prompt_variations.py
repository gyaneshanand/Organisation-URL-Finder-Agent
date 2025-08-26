#!/usr/bin/env python3
"""
Example usage of the new prompt provider system.
This demonstrates how to experiment with different prompt variations.
"""

from modular_url_agent import ModularURLAgent
from prompt_provider import PromptProvider

def demonstrate_prompt_variations():
    """Demonstrate how to use different prompt variations."""
    print("🎯 Demonstrating Prompt Variation System")
    print("="*60)
    
    # Show all available variations
    print("\n📋 Available Prompt Variations:")
    PromptProvider.list_all_variations()
    
    # Create agent with specific variation
    print(f"\n🤖 Creating agent with prompt variation 1...")
    agent = ModularURLAgent(prompt_variation=1)
    
    # Show current settings
    info = agent.get_current_prompt_info()
    print(f"Current settings: {info}")
    
    # Test foundation (you can change this)
    foundation_name = "Ford Foundation"
    
    print(f"\n🔍 Testing different prompt variations with: '{foundation_name}'")
    print("-" * 60)
    
    # Test each variation
    for variation in [1, 2, 3, 4]:
        print(f"\n🧪 Testing Variation {variation}")
        print(f"Description: {PromptProvider.get_variation_description(variation)}")
        
        # Switch to this variation
        agent.switch_prompt_variation(variation)
        
        # You can uncomment the line below to actually test the search
        # (This requires API keys and may take time)
        # result = agent.find_foundation_url(foundation_name)
        # print(f"Result: {result}")
        
        print("✅ Variation switched successfully")
    
    print(f"\n🎉 Demonstration complete!")
    print(f"💡 To actually test searches, uncomment the search lines in the code.")

def show_prompt_content():
    """Show the actual content of each prompt variation."""
    print("\n📄 Prompt Content Preview")
    print("="*60)
    
    for variation in [1, 2, 3, 4]:
        print(f"\n--- Variation {variation} ---")
        print(f"Description: {PromptProvider.get_variation_description(variation)}")
        prompt = PromptProvider.get_prompt(variation, "Example Search Provider")
        print(f"Length: {len(prompt)} characters")
        print(f"Preview: {prompt[:200]}...")
        print("-" * 40)

if __name__ == "__main__":
    demonstrate_prompt_variations()
    show_prompt_content()
