# Modular Search Provider System - Usage Guide

## 🎯 Overview

The Organisation-URL-Finder-Agent now supports a modular search provider system that allows you to switch between different search engines:

- **DuckDuckGo** (Default, no API key required)
- **SerpAPI** (Requires API key, uses Google)
- **Tavily** (Requires API key, AI-powered search)

## 🚀 Quick Start

### 1. Basic Usage

```python
from modular_url_agent import ModularURLAgent

# Create agent with default provider (auto-selects best available)
agent = ModularURLAgent()

# Find a foundation URL
url = agent.find_foundation_url("The William Penn Foundation")
print(f"Found: {url}")
```

### 2. Using a Specific Provider

```python
# Use DuckDuckGo specifically
agent = ModularURLAgent(search_provider="duckduckgo")

# Use SerpAPI (requires SERPAPI_API_KEY in .env)
agent = ModularURLAgent(search_provider="serpapi")

# Use Tavily (requires TAVILY_API_KEY in .env)
agent = ModularURLAgent(search_provider="tavily")
```

### 3. Dynamic Provider Switching

```python
agent = ModularURLAgent()

# Check current provider
print(f"Current: {agent.get_current_provider()}")

# Switch to different provider
agent.switch_search_provider("tavily")

# Find URL with new provider
url = agent.find_foundation_url("Ford Foundation")
```

### 4. Custom Configuration

```python
from config import SearchConfig

# Create custom configuration
config = SearchConfig(
    max_results=20,
    provider_preference=["tavily", "serpapi", "duckduckgo"],
    search_variations=[
        "'{name}' foundation official website",
        "'{name}' grants homepage",
        "'{name}' .org domain"
    ]
)

# Use custom config
agent = ModularURLAgent(config=config)
```

## 🔧 Environment Setup

### Required
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Optional (for additional providers)
```bash
SERPAPI_API_KEY=your_serpapi_key_here
TAVILY_API_KEY=your_tavily_key_here
DEFAULT_SEARCH_PROVIDER=duckduckgo
MAX_SEARCH_RESULTS=15
```

### Optional (for LangSmith monitoring)
```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=your_project_name
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

## 📚 API Usage

### Start the API Server
```bash
python main.py
```

### Use the API
```bash
# Find foundation URL with default provider
curl -X POST "http://localhost:8000/find-foundation-url" \
     -H "Content-Type: application/json" \
     -d '{"foundation_name": "Ford Foundation"}'

# Find foundation URL with specific provider
curl -X POST "http://localhost:8000/find-foundation-url" \
     -H "Content-Type: application/json" \
     -d '{"foundation_name": "Ford Foundation", "search_provider": "tavily"}'

# Check available providers
curl "http://localhost:8000/providers"

# Switch provider for all subsequent requests
curl -X POST "http://localhost:8000/switch-provider/tavily"
```

## 🎛️ Provider Comparison

| Feature | DuckDuckGo | SerpAPI | Tavily |
|---------|------------|---------|--------|
| **Cost** | Free | Paid | Paid |
| **API Key** | Not required | Required | Required |
| **Rate Limits** | None | Based on plan | Based on plan |
| **Result Quality** | Good | Excellent | Very Good |
| **Best For** | General searches | Official websites | Factual queries |

## 📋 Available Methods

### ModularURLAgent Class

```python
# Core methods
agent.find_foundation_url(name: str) -> str
agent.switch_search_provider(provider_name: str)
agent.get_current_provider() -> str
agent.get_available_providers() -> List[str]

# Example
agent = ModularURLAgent()
url = agent.find_foundation_url("Gates Foundation")
agent.switch_search_provider("serpapi")
```

### SearchProviderFactory

```python
from search_providers import SearchProviderFactory

# Create specific provider
provider = SearchProviderFactory.create_provider("duckduckgo")

# Get available providers
providers = SearchProviderFactory.get_available_providers()

# Create best available provider
provider = SearchProviderFactory.create_best_available_provider()
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
python test_modular.py
```

Run the interactive demo:

```bash
python demo.py
```

Test LangSmith configuration:

```bash
python langsmith_setup.py
```

## 🔍 Example Output

```
🚀 Modular URL Agent Demo
==================================================

Available providers: ['duckduckgo', 'ddg', 'serpapi', 'google', 'tavily']
Current provider: DuckDuckGo

🔍 Searching for 'The William Penn Foundation' using DuckDuckGo
✅ Found URL: https://www.williampennfoundation.org/

🔄 Switching from DuckDuckGo to tavily
✅ Now using Tavily (basic)
```

## 🛠️ Extending the System

### Adding New Search Providers

1. Create a new provider class inheriting from `BaseSearchProvider`
2. Implement required methods: `get_search_tool()`, `get_provider_name()`, `validate_configuration()`
3. Add it to the factory in `search_providers/factory.py`

```python
from .base_provider import BaseSearchProvider

class MyCustomProvider(BaseSearchProvider):
    def get_search_tool(self):
        # Return LangChain tool
        pass
    
    def get_provider_name(self):
        return "My Custom Provider"
    
    def validate_configuration(self):
        # Check if properly configured
        return True
```

## 📞 Support

- Check the README.md for full documentation
- Run `python test_modular.py` to diagnose issues
- Visit `http://localhost:8000/docs` for API documentation when the server is running
