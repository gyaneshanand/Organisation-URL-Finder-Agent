# Organisation-URL-Finder-Agent

A FastAPI-based service that finds official URLs for foundations and grant-making organizations using AI-powered search.

## Features

- **RESTful API**: Expose foundation URL finding as HTTP endpoints
- **Multiple Search Strategies**: Tries different search approaches for better results
- **URL Validation**: Verifies URLs contain foundation/grant-related content
- **Interactive Documentation**: Built-in Swagger UI and ReDoc
- **Health Checks**: Monitor API status and configuration

## API Endpoints

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
    "foundation_name": "The William and Flora Hewlett Foundation"
}
```


### Response Format
```json
{
    "foundation_name": "The William and Flora Hewlett Foundation",
    "url": "https://www.hewlett.org",
    "success": true,
    "message": "Foundation URL found successfully"
}
```

## Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd Organisation-URL-Finder-Agent

# Copy environment file and add your OpenAI API key
cp sample.env .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the API Server
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