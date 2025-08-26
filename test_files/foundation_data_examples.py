#!/usr/bin/env python3
"""
Example usage of foundation data integration with the URL Agent.
"""

from modular_url_agent import ModularURLAgent
from prompt_provider import PromptProvider

def example_with_complete_data():
    """Example using complete foundation data."""
    print("📊 Example 1: Complete Foundation Data")
    print("="*50)
    
    # Complete foundation data from database
    foundation_data = {
        'foundation_name': 'The Ford Foundation',
        'ein': '13-1684331',
        'foundation_contact': 'info@fordfoundation.org',
        'foundation_address': '320 E 43rd St',
        'foundation_city': 'New York, NY 10017',
        'foundation_website_text': 'Primary website at fordfoundation.org'
    }
    
    # Create agent with foundation data (using prompt variation 4 for best data integration)
    agent = ModularURLAgent(
        prompt_variation=4,  # Most detailed prompt with data integration
        foundation_data=foundation_data
    )
    
    print("Agent created with complete foundation data")
    print(f"Current prompt variation: {agent.get_current_prompt_info()['variation']}")
    
    # The search will now use the foundation data to validate results
    # url = agent.find_foundation_url("Ford Foundation")
    print("🔍 Ready to search with enhanced data validation")

def example_with_partial_data():
    """Example using partial foundation data (some fields blank)."""
    print("\n📊 Example 2: Partial Foundation Data")
    print("="*50)
    
    # Partial data - some fields are blank/empty
    foundation_data = {
        'foundation_name': 'Robert Wood Johnson Foundation',
        'ein': '',  # Not available
        'foundation_contact': '',  # Not available
        'foundation_address': '50 College Rd E',
        'foundation_city': 'Princeton, NJ',
        'foundation_website_text': ''  # Not available
    }
    
    agent = ModularURLAgent(
        prompt_variation=4,
        foundation_data=foundation_data
    )
    
    print("Agent created with partial foundation data")
    print("Only non-blank fields will be included in the prompt")

def example_updating_data():
    """Example showing how to update foundation data dynamically."""
    print("\n🔄 Example 3: Updating Foundation Data")
    print("="*50)
    
    # Start with basic data
    initial_data = {
        'foundation_name': 'Gates Foundation',
        'ein': '',
        'foundation_contact': '',
        'foundation_address': '',
        'foundation_city': 'Seattle, WA',
        'foundation_website_text': ''
    }
    
    agent = ModularURLAgent(prompt_variation=4, foundation_data=initial_data)
    print("Agent created with basic data")
    
    # Later, update with more complete data
    updated_data = {
        'foundation_name': 'Bill & Melinda Gates Foundation',
        'ein': '56-2618866',
        'foundation_contact': 'info@gatesfoundation.org',
        'foundation_address': '440 5th Ave N',
        'foundation_city': 'Seattle, WA 98109',
        'foundation_website_text': 'Main site: gatesfoundation.org'
    }
    
    agent.update_foundation_data(updated_data)
    print("Foundation data updated with complete information")

def example_no_data():
    """Example with no foundation data (backward compatibility)."""
    print("\n❌ Example 4: No Foundation Data (Backward Compatible)")
    print("="*50)
    
    # Agent without foundation data works exactly as before
    agent = ModularURLAgent(prompt_variation=4)
    
    print("Agent created without foundation data")
    print("Prompt will work normally without additional data section")

def show_prompt_differences():
    """Show how prompts differ with and without foundation data."""
    print("\n🔍 Example 5: Prompt Comparison")
    print("="*50)
    
    foundation_data = {
        'foundation_name': 'Example Foundation',
        'ein': '12-3456789',
        'foundation_contact': 'contact@example.org',
        'foundation_address': '123 Main St',
        'foundation_city': 'Anytown, ST',
        'foundation_website_text': 'example.org'
    }
    
    # Prompt without data
    prompt_without = PromptProvider.get_prompt(4, "Google Search")
    print(f"Prompt without data: {len(prompt_without)} characters")
    
    # Prompt with data
    prompt_with = PromptProvider.get_prompt(4, "Google Search", foundation_data)
    print(f"Prompt with data: {len(prompt_with)} characters")
    
    difference = len(prompt_with) - len(prompt_without)
    print(f"Difference: +{difference} characters for foundation data section")

# Database integration example
def database_integration_example():
    """Example of how to integrate with database queries."""
    print("\n💾 Example 6: Database Integration Pattern")
    print("="*50)
    
    def get_foundation_data_from_db(foundation_name):
        """
        Simulate getting foundation data from database.
        Replace this with your actual database query.
        """
        # Example SQL query (pseudo-code):
        # SELECT foundation_name, ein, foundation_contact, 
        #        foundation_address, foundation_city, foundation_website_text 
        # FROM foundations 
        # WHERE foundation_name LIKE %foundation_name%
        
        # Simulated database result
        return {
            'foundation_name': foundation_name,
            'ein': '12-3456789',
            'foundation_contact': 'info@foundation.org',
            'foundation_address': '123 Foundation Ave',
            'foundation_city': 'Foundation City, ST',
            'foundation_website_text': 'foundation.org'
        }
    
    # Usage pattern
    foundation_name = "Example Foundation"
    
    # 1. Get data from database
    db_data = get_foundation_data_from_db(foundation_name)
    
    # 2. Create agent with database data
    agent = ModularURLAgent(
        prompt_variation=4,
        foundation_data=db_data
    )
    
    # 3. Search with enhanced data
    # url = agent.find_foundation_url(foundation_name)
    
    print("Database integration pattern demonstrated")
    print("Agent will use database data to enhance search accuracy")

if __name__ == "__main__":
    example_with_complete_data()
    example_with_partial_data()
    example_updating_data()
    example_no_data()
    show_prompt_differences()
    database_integration_example()
