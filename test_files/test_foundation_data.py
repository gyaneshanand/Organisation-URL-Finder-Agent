#!/usr/bin/env python3
"""
Test script for foundation data integration with prompt provider.
"""

from prompt_provider import PromptProvider
from modular_url_agent import ModularURLAgent

def test_foundation_data_integration():
    """Test the foundation data integration in prompts."""
    print("🧪 Testing Foundation Data Integration")
    print("="*60)
    
    # Sample foundation data (simulating database data)
    foundation_data_complete = {
        'foundation_name': 'The Ford Foundation',
        'ein': '13-1684331',
        'foundation_contact': 'info@fordfoundation.org',
        'foundation_address': '320 E 43rd St',
        'foundation_city': 'New York, NY',
        'foundation_website_text': 'Known to be at fordfoundation.org'
    }
    
    # Test with partial data (some fields blank)
    foundation_data_partial = {
        'foundation_name': 'The William Penn Foundation',
        'ein': '',  # blank
        'foundation_contact': '',  # blank
        'foundation_address': '2 Logan Square',
        'foundation_city': 'Philadelphia, PA',
        'foundation_website_text': ''  # blank
    }
    
    # Test with no data
    foundation_data_empty = None
    
    print("1. Testing with complete foundation data:")
    print("-" * 40)
    prompt_complete = PromptProvider.get_prompt(4, "Google Search", foundation_data_complete)
    print(f"Prompt length: {len(prompt_complete)} characters")
    print("Sample of prompt with data:")
    print(prompt_complete[:500] + "...")
    
    print("\n2. Testing with partial foundation data:")
    print("-" * 40)
    prompt_partial = PromptProvider.get_prompt(4, "Google Search", foundation_data_partial)
    print(f"Prompt length: {len(prompt_partial)} characters")
    print("Sample of prompt with partial data:")
    print(prompt_partial[:500] + "...")
    
    print("\n3. Testing with no foundation data:")
    print("-" * 40)
    prompt_empty = PromptProvider.get_prompt(4, "Google Search", foundation_data_empty)
    print(f"Prompt length: {len(prompt_empty)} characters")
    print("Sample of prompt without data:")
    print(prompt_empty[:500] + "...")
    
    print("\n✅ Foundation data integration tests completed!")

def test_agent_with_foundation_data():
    """Test the agent with foundation data."""
    print("\n🤖 Testing Agent with Foundation Data")
    print("="*60)
    
    # Sample foundation data
    foundation_data = {
        'foundation_name': 'Gates Foundation',
        'ein': '56-2618866',
        'foundation_contact': 'info@gatesfoundation.org',
        'foundation_address': '440 5th Ave N',
        'foundation_city': 'Seattle, WA',
        'foundation_website_text': 'gatesfoundation.org'
    }
    
    # Create agent with foundation data
    agent = ModularURLAgent(prompt_variation=4, foundation_data=foundation_data)
    
    print("Agent created with foundation data")
    info = agent.get_current_prompt_info()
    print(f"Current prompt info: {info}")
    
    # Test updating foundation data
    new_data = {
        'foundation_name': 'Robert Wood Johnson Foundation',
        'ein': '22-2250909',
        'foundation_contact': '',
        'foundation_address': '50 College Rd E',
        'foundation_city': 'Princeton, NJ',
        'foundation_website_text': 'rwjf.org'
    }
    
    print("\n🔄 Updating foundation data...")
    agent.update_foundation_data(new_data)
    
    print("\n✅ Agent foundation data tests completed!")

def test_data_filtering():
    """Test that blank fields are properly filtered out."""
    print("\n🔍 Testing Data Filtering")
    print("="*60)
    
    # Test data with various blank/empty values
    test_data = {
        'foundation_name': 'Test Foundation',
        'ein': '',  # empty string
        'foundation_contact': '   ',  # whitespace only
        'foundation_address': 'Real Address',
        'foundation_city': None,  # None value
        'foundation_website_text': 'website.org'
    }
    
    info_section = PromptProvider._build_foundation_info_section(test_data)
    print("Generated foundation info section:")
    print(info_section)
    
    # Count how many fields were included
    lines = info_section.split('\n')
    data_lines = [line for line in lines if line.strip().startswith('-')]
    print(f"\nExpected 3 fields (name, address, website), got {len(data_lines)} fields")
    
    print("\n✅ Data filtering tests completed!")

if __name__ == "__main__":
    test_foundation_data_integration()
    test_agent_with_foundation_data()
    test_data_filtering()
