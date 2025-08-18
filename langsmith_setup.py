"""
LangSmith configuration and testing utilities.
"""
import os
from dotenv import load_dotenv

def setup_langsmith_env():
    """Setup LangSmith environment variables from config."""
    load_dotenv()
    
    # Check if LangSmith is enabled
    if os.getenv('LANGSMITH_TRACING', 'false').lower() != 'true':
        print("❌ LangSmith tracing is disabled. Set LANGSMITH_TRACING=true in .env file")
        return False
    
    # Set up LangChain environment variables for LangSmith
    required_vars = {
        'LANGSMITH_ENDPOINT': 'LANGCHAIN_ENDPOINT',
        'LANGSMITH_API_KEY': 'LANGCHAIN_API_KEY', 
        'LANGSMITH_PROJECT': 'LANGCHAIN_PROJECT'
    }
    
    missing_vars = []
    for env_var, langchain_var in required_vars.items():
        value = os.getenv(env_var)
        if value:
            os.environ[langchain_var] = value
            print(f"✅ {env_var} -> {langchain_var}")
        else:
            missing_vars.append(env_var)
    
    if missing_vars:
        print(f"⚠️  Missing required variables: {', '.join(missing_vars)}")
        return False
    
    # Enable tracing
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    print("✅ LangSmith tracing enabled globally")
    return True

def test_langsmith_connection():
    """Test LangSmith connection."""
    try:
        import langsmith
        
        if not setup_langsmith_env():
            return False
        
        # Try to create a client
        client = langsmith.Client()
        
        # Test connection by getting project info
        project_name = os.getenv('LANGCHAIN_PROJECT', 'default')
        print(f"🔍 Testing connection to project: {project_name}")
        
        # This will raise an exception if connection fails
        runs = list(client.list_runs(project_name=project_name, limit=1))
        print("✅ Successfully connected to LangSmith!")
        return True
        
    except ImportError:
        print("❌ LangSmith not installed. Install with: pip install langsmith")
        return False
    except Exception as e:
        print(f"❌ Failed to connect to LangSmith: {e}")
        print("Please check your LANGSMITH_API_KEY and LANGSMITH_PROJECT settings")
        return False

def print_langsmith_status():
    """Print current LangSmith configuration status."""
    print("🔍 LangSmith Configuration Status")
    print("=" * 40)
    
    load_dotenv()
    
    # Check tracing setting
    tracing_enabled = os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true'
    print(f"Tracing Enabled: {'✅ Yes' if tracing_enabled else '❌ No'}")
    
    if not tracing_enabled:
        print("\nTo enable LangSmith tracing, add to your .env file:")
        print("LANGSMITH_TRACING=true")
        return
    
    # Check required variables
    config_vars = {
        'LANGSMITH_ENDPOINT': os.getenv('LANGSMITH_ENDPOINT'),
        'LANGSMITH_API_KEY': os.getenv('LANGSMITH_API_KEY'),
        'LANGSMITH_PROJECT': os.getenv('LANGSMITH_PROJECT')
    }
    
    print("\nConfiguration:")
    for var, value in config_vars.items():
        if value:
            if 'API_KEY' in var:
                display_value = value[:8] + "..." if len(value) > 8 else value
            else:
                display_value = value
            print(f"  {var}: ✅ {display_value}")
        else:
            print(f"  {var}: ❌ Not set")
    
    # Test connection if all vars are set
    if all(config_vars.values()):
        print("\n🧪 Testing connection...")
        test_langsmith_connection()
    else:
        print("\n⚠️  Some configuration variables are missing")

def main():
    """Main function for testing LangSmith setup."""
    print("🚀 LangSmith Setup and Test Utility")
    print("=" * 50)
    
    print_langsmith_status()
    
    print("\n📋 Quick Setup Guide:")
    print("1. Add LangSmith credentials to your .env file:")
    print("   LANGSMITH_TRACING=true")
    print("   LANGSMITH_API_KEY=your_api_key_here")
    print("   LANGSMITH_PROJECT=your_project_name")
    print("   LANGSMITH_ENDPOINT=https://api.smith.langchain.com")
    print("\n2. Install LangSmith: pip install langsmith")
    print("3. Run this script again to test the connection")
    print("4. Start your agent - traces will appear in LangSmith!")

if __name__ == "__main__":
    main()
