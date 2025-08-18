"""
Example usage of the modular URL agent with different search providers.
"""
from modular_url_agent import ModularURLAgent
from config import SearchConfig

def main():
    """Demonstrate the modular URL agent with different search providers."""
    
    print("🚀 Modular URL Agent Demo")
    print("=" * 50)
    
    # Example foundation to search for
    foundation_name = "The William Penn Foundation"
    
    # Method 1: Use default configuration (auto-selects best available provider)
    print("\n1️⃣  Using default configuration:")
    agent = ModularURLAgent()
    print(f"Available providers: {agent.get_available_providers()}")
    print(f"Current provider: {agent.get_current_provider()}")
    
    url = agent.find_foundation_url(foundation_name)
    print(f"Result: {url}")
    
    # Method 2: Specify a particular search provider
    print("\n2️⃣  Using DuckDuckGo specifically:")
    try:
        ddg_agent = ModularURLAgent(search_provider="duckduckgo")
        url_ddg = ddg_agent.find_foundation_url(foundation_name)
        print(f"DuckDuckGo result: {url_ddg}")
    except Exception as e:
        print(f"Error with DuckDuckGo: {e}")
    
    # Method 3: Try switching providers dynamically
    print("\n3️⃣  Switching providers dynamically:")
    try:
        agent.switch_search_provider("tavily")
        url_tavily = agent.find_foundation_url(foundation_name)
        print(f"Tavily result: {url_tavily}")
    except Exception as e:
        print(f"Could not use Tavily: {e}")
    
    # Method 4: Custom configuration
    print("\n4️⃣  Using custom configuration:")
    custom_config = SearchConfig(
        max_results=10,
        provider_preference=["duckduckgo", "tavily", "serpapi"],
        search_variations=[
            "'{name}' foundation official website",
            "'{name}' grants .org site",
            "'{name}' homepage"
        ]
    )
    
    custom_agent = ModularURLAgent(config=custom_config)
    url_custom = custom_agent.find_foundation_url(foundation_name)
    print(f"Custom config result: {url_custom}")
    
    print("\n✅ Demo complete!")


def interactive_demo():
    """Interactive demo where user can choose search provider."""
    
    print("🎯 Interactive Search Provider Demo")
    print("=" * 40)
    
    agent = ModularURLAgent()
    
    while True:
        print(f"\nCurrent provider: {agent.get_current_provider()}")
        print("Available providers:", ", ".join(agent.get_available_providers()))
        
        foundation = input("\nEnter foundation name (or 'quit' to exit): ").strip()
        if foundation.lower() == 'quit':
            break
        
        provider = input("Choose provider (or press Enter for current): ").strip()
        
        if provider:
            try:
                agent.switch_search_provider(provider)
            except Exception as e:
                print(f"Error switching to {provider}: {e}")
                continue
        
        url = agent.find_foundation_url(foundation)
        print(f"\n🎯 Result: {url}")


if __name__ == "__main__":
    # Run the main demo
    main()
    
    # Uncomment the line below for interactive demo
    # interactive_demo()
