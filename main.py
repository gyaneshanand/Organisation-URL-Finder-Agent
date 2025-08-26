from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import logging

# Import the new modular URL finding functionality
from modular_url_agent import ModularURLAgent
from search_providers import SearchProviderFactory

# Load environment variables
load_dotenv()

# Setup LangSmith if enabled
def setup_langsmith():
    """Setup LangSmith tracing if configured."""
    if os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true':
        try:
            import langsmith
            
            # Set environment variables for LangSmith
            if os.getenv('LANGSMITH_ENDPOINT'):
                os.environ['LANGCHAIN_ENDPOINT'] = os.getenv('LANGSMITH_ENDPOINT')
            if os.getenv('LANGSMITH_API_KEY'):
                os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGSMITH_API_KEY')
            if os.getenv('LANGSMITH_PROJECT'):
                os.environ['LANGCHAIN_PROJECT'] = os.getenv('LANGSMITH_PROJECT')
            
            os.environ['LANGCHAIN_TRACING_V2'] = 'true'
            
            print("✅ LangSmith tracing enabled for API")
            print(f"📊 Project: {os.getenv('LANGSMITH_PROJECT', 'default')}")
            
        except ImportError:
            print("⚠️  LangSmith not installed. Install with: pip install langsmith")
        except Exception as e:
            print(f"⚠️  Failed to setup LangSmith: {e}")

# Initialize LangSmith
setup_langsmith()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the modular agent
try:
    url_agent = ModularURLAgent(prompt_variation=1)
    logger.info(f"Initialized with search provider: {url_agent.get_current_provider()}")
except Exception as e:
    logger.error(f"Failed to initialize URL agent: {e}")
    url_agent = None

# Initialize FastAPI app
app = FastAPI(
    title="Foundation URL Finder API (Modular)",
    description="API to find official URLs for foundations and grant-making organizations using multiple search providers",
    version="2.0.0"
)

# Pydantic models for request/response
class FoundationRequest(BaseModel):
    foundation_name: str
    search_provider: Optional[str] = None
    ein: Optional[str] = None
    foundation_contact: Optional[str] = None
    foundation_address: Optional[str] = None
    foundation_city: Optional[str] = None
    foundation_website_text: Optional[str] = None
    prompt_variation: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "foundation_name": "The William and Flora Hewlett Foundation",
                "search_provider": "duckduckgo",
                "ein": "13-1684331",
                "foundation_contact": "info@hewlett.org",
                "foundation_address": "2121 Sand Hill Road",
                "foundation_city": "Menlo Park, CA",
                "foundation_website_text": "hewlett.org",
                "prompt_variation": 1
            }
        }

class FoundationResponse(BaseModel):
    foundation_name: str
    url: Optional[str] = None
    success: bool
    message: str
    search_provider: str
    prompt_variation: Optional[int] = None
    foundation_data_used: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "foundation_name": "The William and Flora Hewlett Foundation",
                "url": "https://www.hewlett.org",
                "success": True,
                "message": "Foundation URL found successfully",
                "search_provider": "DuckDuckGo",
                "prompt_variation": 1,
                "foundation_data_used": True
            }
        }

class HealthResponse(BaseModel):
    status: str
    message: str
    current_provider: Optional[str] = None
    available_providers: Optional[list] = None
    langsmith_enabled: Optional[bool] = None

class ProvidersResponse(BaseModel):
    current_provider: str
    available_providers: list

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Foundation URL Finder API (Modular) with Database Integration",
        "version": "2.1.0",
        "current_provider": url_agent.get_current_provider() if url_agent else "Not initialized",
        "langsmith_enabled": os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true',
        "langsmith_project": os.getenv('LANGSMITH_PROJECT') if os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true' else None,
        "features": {
            "foundation_data_integration": True,
            "prompt_variations": [1, 2, 3, 4],
            "supported_data_fields": [
                "foundation_name",
                "ein", 
                "foundation_contact",
                "foundation_address", 
                "foundation_city",
                "foundation_website_text"
            ]
        },
        "endpoints": {
            "health": "/health",
            "providers": "/providers",
            "find_foundation_url": "/find-foundation-url (POST)",
            "find_foundation_url_get": "/find-foundation-url/{foundation_name} (GET)",
            "switch_provider": "/switch-provider/{provider_name} (POST)",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Verify OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        return HealthResponse(
            status="unhealthy",
            message="OpenAI API key not configured"
        )
    
    if not url_agent:
        return HealthResponse(
            status="unhealthy",
            message="URL agent not initialized"
        )
    
    # Check LangSmith status
    langsmith_enabled = os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true'
    
    return HealthResponse(
        status="healthy",
        message="API is running and configured correctly",
        current_provider=url_agent.get_current_provider(),
        available_providers=url_agent.get_available_providers(),
        langsmith_enabled=langsmith_enabled
    )

@app.get("/providers", response_model=ProvidersResponse)
async def get_providers():
    """Get current and available search providers"""
    if not url_agent:
        raise HTTPException(status_code=500, detail="URL agent not initialized")
    
    return ProvidersResponse(
        current_provider=url_agent.get_current_provider(),
        available_providers=url_agent.get_available_providers()
    )

@app.post("/switch-provider/{provider_name}")
async def switch_provider(provider_name: str):
    """Switch to a different search provider"""
    if not url_agent:
        raise HTTPException(status_code=500, detail="URL agent not initialized")
    
    try:
        old_provider = url_agent.get_current_provider()
        url_agent.switch_search_provider(provider_name)
        new_provider = url_agent.get_current_provider()
        
        return {
            "success": True,
            "message": f"Switched from {old_provider} to {new_provider}",
            "old_provider": old_provider,
            "new_provider": new_provider
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to switch provider: {str(e)}")

@app.post("/find-foundation-url", response_model=FoundationResponse)
async def find_foundation_url_post(request: FoundationRequest):
    """
    Find the official URL for a foundation using POST request
    
    - **foundation_name**: The name of the foundation to search for
    - **search_provider**: Optional search provider to use for this request
    - **ein**: Optional EIN tax ID number
    - **foundation_contact**: Optional foundation contact information
    - **foundation_address**: Optional foundation address
    - **foundation_city**: Optional foundation city
    - **foundation_website_text**: Optional known website information
    - **prompt_variation**: Optional prompt variation to use (1-4, default: 1, recommended: 4 for database data)
    """
    if not url_agent:
        raise HTTPException(status_code=500, detail="URL agent not initialized")
    
    try:
        if not request.foundation_name.strip():
            raise HTTPException(status_code=400, detail="Foundation name cannot be empty")
        
        # Build foundation data dictionary from request
        foundation_data = {}
        foundation_data_provided = False
        
        if request.foundation_name:
            foundation_data['foundation_name'] = request.foundation_name
        if request.ein:
            foundation_data['ein'] = request.ein
            foundation_data_provided = True
        if request.foundation_contact:
            foundation_data['foundation_contact'] = request.foundation_contact
            foundation_data_provided = True
        if request.foundation_address:
            foundation_data['foundation_address'] = request.foundation_address
            foundation_data_provided = True
        if request.foundation_city:
            foundation_data['foundation_city'] = request.foundation_city
            foundation_data_provided = True
        if request.foundation_website_text:
            foundation_data['foundation_website_text'] = request.foundation_website_text
            foundation_data_provided = True
        
        # Determine prompt variation to use
        prompt_variation = request.prompt_variation or (4 if foundation_data_provided else 1)
        
        # Create a new agent instance with the provided data
        # Save original agent state
        original_provider = url_agent.get_current_provider()
        original_variation = url_agent.prompt_variation
        
        # Switch provider temporarily if requested
        if request.search_provider:
            url_agent.switch_search_provider(request.search_provider)
        
        # Update agent with foundation data and prompt variation
        if foundation_data_provided:
            url_agent.update_foundation_data(foundation_data)
        
        if prompt_variation != original_variation:
            url_agent.switch_prompt_variation(prompt_variation)
        
        logger.info(f"Searching for URL for foundation: {request.foundation_name}")
        if foundation_data_provided:
            logger.info(f"Using foundation data with prompt variation {prompt_variation}")
        
        # Use the modular URL finding function
        url = url_agent.find_foundation_url(request.foundation_name)
        current_provider = url_agent.get_current_provider()
        
        # Restore original agent state
        if request.search_provider and original_provider != current_provider:
            url_agent.switch_search_provider(original_provider)
        
        if prompt_variation != original_variation:
            url_agent.switch_prompt_variation(original_variation)
        
        if foundation_data_provided:
            url_agent.update_foundation_data(None)  # Clear foundation data
        
        # Check if URL was found successfully
        if url and url.startswith("http") and not url.startswith("Unable"):
            return FoundationResponse(
                foundation_name=request.foundation_name,
                url=url,
                success=True,
                message="Foundation URL found successfully",
                search_provider=current_provider,
                prompt_variation=prompt_variation,
                foundation_data_used=foundation_data_provided
            )
        else:
            return FoundationResponse(
                foundation_name=request.foundation_name,
                url=None,
                success=False,
                message=url if url.startswith("Unable") else "Unable to find foundation URL",
                search_provider=current_provider,
                prompt_variation=prompt_variation,
                foundation_data_used=foundation_data_provided
            )
            
    except Exception as e:
        logger.error(f"Error finding URL for {request.foundation_name}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while searching for foundation URL: {str(e)}"
        )

@app.get("/find-foundation-url/{foundation_name}", response_model=FoundationResponse)
async def find_foundation_url_get(
    foundation_name: str, 
    search_provider: Optional[str] = None,
    ein: Optional[str] = None,
    foundation_contact: Optional[str] = None,
    foundation_address: Optional[str] = None,
    foundation_city: Optional[str] = None,
    foundation_website_text: Optional[str] = None,
    prompt_variation: Optional[int] = None
):
    """
    Find the official URL for a foundation using GET request
    
    - **foundation_name**: The name of the foundation to search for
    - **search_provider**: Optional search provider to use for this request
    - **ein**: Optional EIN tax ID number
    - **foundation_contact**: Optional foundation contact information
    - **foundation_address**: Optional foundation address
    - **foundation_city**: Optional foundation city
    - **foundation_website_text**: Optional known website information
    - **prompt_variation**: Optional prompt variation to use (1-4)
    """
    request = FoundationRequest(
        foundation_name=foundation_name, 
        search_provider=search_provider,
        ein=ein,
        foundation_contact=foundation_contact,
        foundation_address=foundation_address,
        foundation_city=foundation_city,
        foundation_website_text=foundation_website_text,
        prompt_variation=prompt_variation
    )
    return await find_foundation_url_post(request)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "The requested endpoint was not found",
        "available_endpoints": ["/", "/health", "/providers", "/find-foundation-url", "/switch-provider", "/docs"]
    }

if __name__ == "__main__":
    import uvicorn
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please add your OpenAI API key to the .env file.")
        exit(1)
    
    print("🚀 Starting Foundation URL Finder API (Modular)...")
    print("🔧 Available search providers:", SearchProviderFactory.get_available_providers())
    if url_agent:
        print(f"🎯 Current provider: {url_agent.get_current_provider()}")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🏃‍♂️ Interactive API at: http://localhost:8000/redoc")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
