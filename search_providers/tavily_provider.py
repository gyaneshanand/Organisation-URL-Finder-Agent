"""
Tavily search provider implementation.
"""
import os
from langchain_core.tools import BaseTool
from .base_provider import BaseSearchProvider

try:
    from langchain_community.tools.tavily_search import TavilySearchResults
except ImportError:
    TavilySearchResults = None


class TavilyProvider(BaseSearchProvider):
    """Tavily search provider using LangChain's Tavily tool."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key') or os.getenv('TAVILY_API_KEY')
        self.max_results = kwargs.get('max_results', 15)
        self.search_depth = kwargs.get('search_depth', 'basic')  # 'basic' or 'advanced'
    
    def get_search_tool(self) -> BaseTool:
        """Return the Tavily search tool."""
        if not self.validate_configuration():
            raise ValueError("Tavily requires a valid API key. Set TAVILY_API_KEY environment variable.")
        
        if TavilySearchResults is None:
            raise ImportError("Tavily not available. Install with: pip install tavily-python")
        
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
        return bool(self.api_key) and TavilySearchResults is not None
