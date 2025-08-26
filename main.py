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
    
    class Config:
        json_schema_extra = {
            "example": {
                "foundation_name": "The William and Flora Hewlett Foundation",
                "search_provider": "duckduckgo"
            }
        }

class FoundationResponse(BaseModel):
    foundation_name: str
    url: Optional[str] = None
    success: bool
    message: str
    search_provider: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "foundation_name": "The William and Flora Hewlett Foundation",
                "url": "https://www.hewlett.org",
                "success": True,
                "message": "Foundation URL found successfully",
                "search_provider": "DuckDuckGo"
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
        "message": "Foundation URL Finder API (Modular)",
        "version": "2.0.0",
        "current_provider": url_agent.get_current_provider() if url_agent else "Not initialized",
        "langsmith_enabled": os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true',
        "langsmith_project": os.getenv('LANGSMITH_PROJECT') if os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true' else None,
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
    """
    if not url_agent:
        raise HTTPException(status_code=500, detail="URL agent not initialized")
    
    try:
        if not request.foundation_name.strip():
            raise HTTPException(status_code=400, detail="Foundation name cannot be empty")
        
        # Switch provider temporarily if requested
        original_provider = None
        if request.search_provider:
            original_provider = url_agent.get_current_provider()
            url_agent.switch_search_provider(request.search_provider)
        
        logger.info(f"Searching for URL for foundation: {request.foundation_name}")
        
        # Use the modular URL finding function
        url = url_agent.find_foundation_url(request.foundation_name)
        current_provider = url_agent.get_current_provider()
        
        # Switch back to original provider if we changed it
        if original_provider and original_provider != current_provider:
            url_agent.switch_search_provider(original_provider)
        
        # Check if URL was found successfully
        if url and url.startswith("http") and not url.startswith("Unable"):
            return FoundationResponse(
                foundation_name=request.foundation_name,
                url=url,
                success=True,
                message="Foundation URL found successfully",
                search_provider=current_provider
            )
        else:
            return FoundationResponse(
                foundation_name=request.foundation_name,
                url=None,
                success=False,
                message=url if url.startswith("Unable") else "Unable to find foundation URL",
                search_provider=current_provider
            )
            
    except Exception as e:
        logger.error(f"Error finding URL for {request.foundation_name}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while searching for foundation URL: {str(e)}"
        )

@app.get("/find-foundation-url/{foundation_name}", response_model=FoundationResponse)
async def find_foundation_url_get(foundation_name: str, search_provider: Optional[str] = None):
    """
    Find the official URL for a foundation using GET request
    
    - **foundation_name**: The name of the foundation to search for
    - **search_provider**: Optional search provider to use for this request
    """
    request = FoundationRequest(foundation_name=foundation_name, search_provider=search_provider)
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
