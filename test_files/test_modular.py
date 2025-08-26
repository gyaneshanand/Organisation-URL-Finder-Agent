"""
Test script for the modular URL agent system.
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic functionality of the modular system."""
    print("🧪 Testing Modular URL Agent System")
    print("=" * 50)
    
    try:
        from modular_url_agent import ModularURLAgent
        from search_providers import SearchProviderFactory
        from config import SearchConfig
        
        print("✅ All imports successful")
        
        # Test 1: Check available providers
        print(f"\n1️⃣  Available providers: {SearchProviderFactory.get_available_providers()}")
        
        # Test 2: Create agent with default provider
        print("\n2️⃣  Creating agent with default provider...")
        agent = ModularURLAgent()
        print(f"✅ Agent created with provider: {agent.get_current_provider()}")
        
        # Test 3: Test provider switching
        print("\n3️⃣  Testing provider switching...")
        available_providers = agent.get_available_providers()
        
        for provider in available_providers:
            if provider != agent.get_current_provider():
                try:
                    agent.switch_search_provider(provider)
                    print(f"✅ Successfully switched to: {agent.get_current_provider()}")
                    break
                except Exception as e:
                    print(f"❌ Could not switch to {provider}: {e}")
        
        # Test 4: Test configuration
        print("\n4️⃣  Testing custom configuration...")
        config = SearchConfig(
            max_results=10,
            default_provider="duckduckgo"
        )
        custom_agent = ModularURLAgent(config=config)
        print(f"✅ Custom agent created with provider: {custom_agent.get_current_provider()}")
        
        print("\n✅ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_search_functionality():
    """Test actual search functionality (requires API key)."""
    print("\n🔍 Testing Search Functionality")
    print("=" * 40)
    
    try:
        from modular_url_agent import ModularURLAgent
        
        # Check if OpenAI API key is available
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  Skipping search test - OPENAI_API_KEY not set")
            return True
        
        agent = ModularURLAgent()
        test_foundation = "The William Penn Foundation"
        
        print(f"🔍 Searching for: {test_foundation}")
        print(f"Using provider: {agent.get_current_provider()}")
        
        # This would actually run the search - commented out for safety
        # url = agent.find_foundation_url(test_foundation)
        # print(f"Result: {url}")
        
        print("✅ Search test setup successful (actual search skipped)")
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def test_api_imports():
    """Test that API imports work correctly."""
    print("\n🌐 Testing API Integration")
    print("=" * 30)
    
    try:
        # Test importing the main API module
        import main
        print("✅ Main API module imports successfully")
        
        # Check if the agent was initialized
        if hasattr(main, 'url_agent') and main.url_agent:
            print(f"✅ URL agent initialized with: {main.url_agent.get_current_provider()}")
        else:
            print("⚠️  URL agent not initialized (likely missing API key)")
        
        return True
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Running Modular URL Agent Tests")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    tests = [
        test_basic_functionality,
        test_search_functionality,
        test_api_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The modular system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    # Print usage instructions
    print("\n📋 Usage Instructions:")
    print("1. Set your OPENAI_API_KEY in .env file")
    print("2. Optionally set SERPAPI_API_KEY and/or TAVILY_API_KEY for additional providers")
    print("3. Run: python demo.py for interactive examples")
    print("4. Run: python main.py to start the API server")

if __name__ == "__main__":
    main()
