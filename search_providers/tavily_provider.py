"""
Tavily search provider implementation.
"""
import os
from langchain_core.tools import BaseTool
from .base_provider import BaseSearchProvider

try:
    # Try the new langchain-tavily package first
    from langchain_tavily import TavilySearch as TavilySearchResults
    TAVILY_AVAILABLE = True
    USE_NEW_TAVILY = True
except ImportError:
    try:
        # Fallback to the old community package
        from langchain_community.tools.tavily_search import TavilySearchResults
        TAVILY_AVAILABLE = True
        USE_NEW_TAVILY = False
    except ImportError:
        TavilySearchResults = None
        TAVILY_AVAILABLE = False
        USE_NEW_TAVILY = False


class TavilyProvider(BaseSearchProvider):
    """Tavily search provider using LangChain's Tavily tool."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key') or os.getenv('TAVILY_API_KEY')
        self.max_results = kwargs.get('max_results', 15)
        self.search_depth = kwargs.get('search_depth', 'advanced')  # 'basic' or 'advanced'
    
    def get_search_tool(self) -> BaseTool:
        """Return the Tavily search tool."""
        if not self.validate_configuration():
            raise ValueError("Tavily requires a valid API key. Set TAVILY_API_KEY environment variable.")
        
        if not TAVILY_AVAILABLE:
            raise ImportError("Tavily not available. Install with: pip install langchain-tavily")
        
        if USE_NEW_TAVILY:
            # Use the new langchain_tavily package
            return TavilySearchResults(
                max_results=self.max_results,
                depth=self.search_depth,  # Note: parameter name changed from search_depth to depth
                tavily_api_key=self.api_key  # Note: parameter name changed from api_key to tavily_api_key
            )
        else:
            # Use the old community package
            return TavilySearchResults(
                max_results=self.max_results,
                search_depth=self.search_depth,
                api_key=self.api_key
            )
    
    def get_provider_name(self) -> str:
        """Return the name of this search provider."""
        return f"Tavily ({self.search_depth})"
    
    def validate_configuration(self) -> bool:
        """Validate that Tavily is properly configured with an API key."""
        return bool(self.api_key) and TAVILY_AVAILABLE
