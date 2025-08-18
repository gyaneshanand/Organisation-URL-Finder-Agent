# Organisation-URL-Finder-Agent

A modular AI-powered service that finds official URLs for foundations and grant-making organizations. Now supports multiple search providers including DuckDuckGo, SerpAPI, and Tavily.

## 🚀 Features

- **Modular Search Providers**: Switch between DuckDuckGo, SerpAPI, and Tavily search engines
- **RESTful API**: Expose foundation URL finding as HTTP endpoints
- **Multiple Search Strategies**: Tries different search approaches for better results
- **URL Validation**: Verifies URLs contain foundation/grant-related content
- **Interactive Documentation**: Built-in Swagger UI and ReDoc
- **Health Checks**: Monitor API status and configuration
- **Configurable**: Easily switch providers and customize search behavior

## 🔧 Search Providers

### Available Providers

1. **DuckDuckGo** (Default - No API key required)
   - Free and privacy-focused
   - Good for general searches
   - No rate limits

2. **SerpAPI** (Requires API key)
   - Uses Google search results
   - High-quality results
   - Better for official websites

3. **Tavily** (Requires API key)
   - AI-powered search
   - Optimized for factual queries
   - Good for finding official sources

## 📊 **LangSmith Integration**

Monitor and debug your AI agent with LangSmith:

- **Automatic Tracing**: All agent interactions are logged
- **Performance Monitoring**: Track response times and success rates
- **Debugging**: See exactly what the agent is thinking
- **Analytics**: Understand usage patterns

### LangSmith Setup
```bash
# Add to your .env file:
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=your_project_name

# Test configuration
python langsmith_setup.py
```

### Provider Configuration

```python
from modular_url_agent import ModularURLAgent

# Use default provider (auto-selects best available)
agent = ModularURLAgent()

# Use specific provider
agent = ModularURLAgent(search_provider="duckduckgo")

# Switch providers dynamically
agent.switch_search_provider("tavily")
```

## 📋 API Endpoints

### Health Check
```
GET /health
```
Check if the API is running and properly configured.

### Find Foundation URL (POST)
```
POST /find-foundation-url
Content-Type: application/json

{
    "foundation_name": "The William and Flora Hewlett Foundation",
    "search_provider": "duckduckgo"  // Optional: specify provider
}
```

### Response Format
```json
{
    "foundation_name": "The William and Flora Hewlett Foundation",
    "url": "https://www.hewlett.org",
    "success": true,
    "message": "Foundation URL found successfully",
    "search_provider": "DuckDuckGo"
}
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd Organisation-URL-Finder-Agent

# Copy environment file and add your API keys
cp sample.env .env
# Edit .env and add your API keys:
# - OPENAI_API_KEY (required)
# - SERPAPI_API_KEY (optional - for SerpAPI)  
# - TAVILY_API_KEY (optional - for Tavily)
# - LANGSMITH_TRACING=true (optional - for monitoring)
# - LANGSMITH_API_KEY (optional - for LangSmith)
# - LANGSMITH_PROJECT (optional - your LangSmith project)
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. LangSmith Setup (Optional)
For monitoring and debugging your AI agent:
```bash
# Test LangSmith configuration
python langsmith_setup.py

# Your traces will appear at: https://smith.langchain.com/
```

### 4. Basic Usage

#### Command Line Usage
```python
from modular_url_agent import ModularURLAgent

# Create agent with default provider
agent = ModularURLAgent()

# Find a foundation URL
url = agent.find_foundation_url("The William Penn Foundation")
print(f"Found URL: {url}")

# Switch providers
agent.switch_search_provider("tavily")
url2 = agent.find_foundation_url("Ford Foundation")
print(f"Tavily result: {url2}")
```

#### Run Demo
```bash
python demo.py
```

### 4. Start the API Server
```bash
# Option 1: Use the startup script
./start_api.sh

# Option 2: Run directly
python main.py

# Option 3: Use uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the API
```bash
# Run the test suite
python test_api.py

# Or test manually with curl
curl -X POST "http://localhost:8000/find-foundation-url" \
     -H "Content-Type: application/json" \
     -d '{"foundation_name": "Ford Foundation"}'
```

## ⚙️ Configuration & Customization

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Search Provider API Keys
SERPAPI_API_KEY=your_serpapi_key_here
TAVILY_API_KEY=your_tavily_key_here

# Optional - Search Configuration
DEFAULT_SEARCH_PROVIDER=duckduckgo
MAX_SEARCH_RESULTS=15
SEARCH_TIMEOUT=30
```

### Custom Configuration
```python
from config import SearchConfig
from modular_url_agent import ModularURLAgent

# Create custom configuration
config = SearchConfig(
    default_provider="tavily",
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

### Provider Comparison

| Provider | API Key Required | Rate Limits | Result Quality | Cost |
|----------|------------------|-------------|----------------|------|
| DuckDuckGo | No | None | Good | Free |
| SerpAPI | Yes | Based on plan | Excellent | Paid |
| Tavily | Yes | Based on plan | Very Good | Paid |

## 📁 Project Structure

```
Organisation-URL-Finder-Agent/
├── search_providers/          # Modular search provider system
│   ├── __init__.py
│   ├── base_provider.py       # Abstract base class
│   ├── duckduckgo_provider.py # DuckDuckGo implementation
│   ├── serpapi_provider.py    # SerpAPI implementation
│   ├── tavily_provider.py     # Tavily implementation
│   └── factory.py             # Provider factory
├── config.py                  # Configuration management
├── modular_url_agent.py       # New modular agent
├── url_agent.py              # Original agent (legacy)
├── main.py                   # FastAPI application
├── demo.py                   # Usage examples
├── test_api.py               # API tests
├── requirements.txt          # Dependencies
├── sample.env                # Environment template
└── README.md                 # This file
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Files
- `.env`: Environment variables (copy from `sample.env`)
- `requirements.txt`: Python dependencies
- `main.py`: FastAPI application
- `url_agent.py`: Core URL finding logic
- `test_api.py`: API test suite

## Usage Examples

### Python Requests
```python
import requests

# POST request
response = requests.post(
    "http://localhost:8000/find-foundation-url",
    json={"foundation_name": "Gates Foundation"}
)
result = response.json()
print(f"URL: {result['url']}")

# GET request
response = requests.get(
    "http://localhost:8000/find-foundation-url/Gates Foundation"
)
result = response.json()
print(f"URL: {result['url']}")
```

### cURL
```bash
# POST request
curl -X POST "http://localhost:8000/find-foundation-url" \
     -H "Content-Type: application/json" \
     -d '{"foundation_name": "Rockefeller Foundation"}'

# GET request
curl "http://localhost:8000/find-foundation-url/Rockefeller%20Foundation"
```

### JavaScript/Fetch
```javascript
// POST request
const response = await fetch('http://localhost:8000/find-foundation-url', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        foundation_name: 'Ford Foundation'
    })
});
const result = await response.json();
console.log('URL:', result.url);
```

## Architecture

The API is built with:
- **FastAPI**: Modern Python web framework for APIs
- **LangChain**: AI agent framework for intelligent search
- **OpenAI GPT-4**: Language model for intelligent URL discovery
- **DuckDuckGo Search**: Web search capabilities
- **Pydantic**: Data validation and serialization

## Development

### Project Structure
```
Organisation-URL-Finder-Agent/
├── main.py              # FastAPI application
├── url_agent.py         # Core URL finding logic
├── test_api.py          # API test suite
├── start_api.sh         # Startup script
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
├── sample.env           # Environment template
└── README.md           # This file
```

### Running in Development
```bash
# Start with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the startup script
./start_api.sh
```

### Testing
```bash
# Run the test suite
python test_api.py

# Test specific endpoints
curl http://localhost:8000/health
```

## Deployment

### Production Considerations
1. **Security**: Set proper CORS policies and API authentication
2. **Environment**: Use production ASGI server (gunicorn + uvicorn)
3. **Monitoring**: Add logging, metrics, and health checks
4. **Rate Limiting**: Implement request throttling
5. **Caching**: Cache results to reduce API calls

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

See LICENSE file for details.