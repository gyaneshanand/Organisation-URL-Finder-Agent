# API Usage Examples with Foundation Data

## Starting the API
```bash
python main.py
```

## Basic Usage Examples

### 1. Simple Foundation Search (No Additional Data)
```bash
curl -X POST "http://localhost:8000/find-foundation-url" \
     -H "Content-Type: application/json" \
     -d '{
       "foundation_name": "Ford Foundation"
     }'
```

### 2. Enhanced Search with Complete Foundation Data
```bash
curl -X POST "http://localhost:8000/find-foundation-url" \
     -H "Content-Type: application/json" \
     -d '{
       "foundation_name": "Ford Foundation",
       "ein": "13-1684331",
       "foundation_contact": "info@fordfoundation.org",
       "foundation_address": "320 E 43rd St",
       "foundation_city": "New York, NY",
       "foundation_website_text": "fordfoundation.org",
       "prompt_variation": 4
     }'
```

### 3. Search with Partial Foundation Data
```bash
curl -X POST "http://localhost:8000/find-foundation-url" \
     -H "Content-Type: application/json" \
     -d '{
       "foundation_name": "William Penn Foundation",
       "foundation_address": "2 Logan Square", 
       "foundation_city": "Philadelphia, PA",
       "prompt_variation": 4
     }'
```

### 4. GET Request with Query Parameters
```bash
curl "http://localhost:8000/find-foundation-url/Ford%20Foundation?ein=13-1684331&foundation_city=New%20York,%20NY&prompt_variation=4"
```

### 5. Using Different Search Provider
```bash
curl -X POST "http://localhost:8000/find-foundation-url" \
     -H "Content-Type: application/json" \
     -d '{
       "foundation_name": "Gates Foundation",
       "search_provider": "tavily",
       "foundation_city": "Seattle, WA",
       "prompt_variation": 4
     }'
```

## Response Format

### Successful Response
```json
{
  "foundation_name": "Ford Foundation",
  "url": "https://www.fordfoundation.org",
  "success": true,
  "message": "Foundation URL found successfully",
  "search_provider": "DuckDuckGo",
  "prompt_variation": 4,
  "foundation_data_used": true
}
```

### Failed Response
```json
{
  "foundation_name": "Unknown Foundation",
  "url": null,
  "success": false,
  "message": "Unable to find foundation URL",
  "search_provider": "DuckDuckGo",
  "prompt_variation": 1,
  "foundation_data_used": false
}
```

## API Information
```bash
curl "http://localhost:8000/"
```

## Health Check
```bash
curl "http://localhost:8000/health"
```

## Available Providers
```bash
curl "http://localhost:8000/providers"
```

## Interactive Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Python Usage Example

```python
import requests

# Enhanced search with foundation data
data = {
    "foundation_name": "Robert Wood Johnson Foundation",
    "ein": "22-2250909",
    "foundation_address": "50 College Rd E",
    "foundation_city": "Princeton, NJ",
    "foundation_website_text": "rwjf.org",
    "prompt_variation": 4
}

response = requests.post(
    "http://localhost:8000/find-foundation-url",
    json=data
)

result = response.json()
print(f"Found URL: {result['url']}")
print(f"Used foundation data: {result['foundation_data_used']}")
```

## Key Features

### Foundation Data Fields
- `foundation_name` (required): Foundation name
- `ein` (optional): EIN tax ID number
- `foundation_contact` (optional): Contact information
- `foundation_address` (optional): Street address
- `foundation_city` (optional): City and state
- `foundation_website_text` (optional): Known website info

### Prompt Variations
- `1`: Original working prompt (default)
- `2`: Enhanced prompt with specific methodology
- `3`: Concise and focused prompt
- `4`: Detailed systematic prompt (recommended for database data)

### Smart Features
- Automatically filters out blank/empty fields
- Uses prompt variation 4 when foundation data is provided
- Maintains backward compatibility
- Enhanced validation with available data
