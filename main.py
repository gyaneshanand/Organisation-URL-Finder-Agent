from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import logging

# Import the URL finding functionality from our existing module
from url_agent import find_foundation_url

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Foundation URL Finder API",
    description="API to find official URLs for foundations and grant-making organizations",
    version="1.0.0"
)

# Pydantic models for request/response
class FoundationRequest(BaseModel):
    foundation_name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "foundation_name": "The William and Flora Hewlett Foundation"
            }
        }

class FoundationResponse(BaseModel):
    foundation_name: str
    url: Optional[str] = None
    success: bool
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "foundation_name": "The William and Flora Hewlett Foundation",
                "url": "https://www.hewlett.org",
                "success": True,
                "message": "Foundation URL found successfully"
            }
        }

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Foundation URL Finder API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "find_foundation_url": "/find-foundation-url (POST)",
            "find_foundation_url_get": "/find-foundation-url/{foundation_name} (GET)",
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
    
    return HealthResponse(
        status="healthy",
        message="API is running and configured correctly"
    )

@app.post("/find-foundation-url", response_model=FoundationResponse)
async def find_foundation_url_post(request: FoundationRequest):
    """
    Find the official URL for a foundation using POST request
    
    - **foundation_name**: The name of the foundation to search for
    """
    try:
        if not request.foundation_name.strip():
            raise HTTPException(status_code=400, detail="Foundation name cannot be empty")
        
        logger.info(f"Searching for URL for foundation: {request.foundation_name}")
        
        # Use the existing URL finding function
        url = find_foundation_url(request.foundation_name)
        
        # Check if URL was found successfully
        if url and url.startswith("http") and not url.startswith("Unable"):
            return FoundationResponse(
                foundation_name=request.foundation_name,
                url=url,
                success=True,
                message="Foundation URL found successfully"
            )
        else:
            return FoundationResponse(
                foundation_name=request.foundation_name,
                url=None,
                success=False,
                message=url if url.startswith("Unable") else "Unable to find foundation URL"
            )
            
    except Exception as e:
        logger.error(f"Error finding URL for {request.foundation_name}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error while searching for foundation URL: {str(e)}"
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "The requested endpoint was not found",
        "available_endpoints": ["/", "/health", "/find-foundation-url", "/docs"]
    }

if __name__ == "__main__":
    import uvicorn
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please add your OpenAI API key to the .env file.")
        exit(1)
    
    print("🚀 Starting Foundation URL Finder API...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🏃‍♂️ Interactive API at: http://localhost:8000/redoc")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
