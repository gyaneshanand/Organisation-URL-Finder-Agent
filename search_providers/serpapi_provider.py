"""
SerpAPI search provider implementation.
"""
import os
from langchain_core.tools import BaseTool, Tool
from .base_provider import BaseSearchProvider

try:
    from langchain_community.utilities import SerpAPIWrapper
except ImportError:
    SerpAPIWrapper = None


class SerpAPIProvider(BaseSearchProvider):
    """SerpAPI search provider using LangChain's SerpAPI tool."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key') or os.getenv('SERPAPI_API_KEY')
        self.max_results = kwargs.get('max_results', 15)
        self.search_engine = kwargs.get('search_engine', 'google')
    
    def get_search_tool(self) -> BaseTool:
        """Return the SerpAPI search tool."""
        if not self.validate_configuration():
            raise ValueError("SerpAPI requires a valid API key. Set SERPAPI_API_KEY environment variable.")
        
        if SerpAPIWrapper is None:
            raise ImportError("SerpAPI not available. Install with: pip install google-search-results")
        
        search = SerpAPIWrapper(
            serpapi_api_key=self.api_key,
            params={
                "engine": self.search_engine,
                "gl": "us",
                "hl": "en",
                "num": self.max_results
            }
        )
        
        return Tool(
            name="serpapi_search",
            description="Search the web using SerpAPI with Google search engine. Useful for finding official websites and current information.",
            func=search.run
        )
    
    def get_provider_name(self) -> str:
        """Return the name of this search provider."""
        return f"SerpAPI ({self.search_engine})"
    
    def validate_configuration(self) -> bool:
        """Validate that SerpAPI is properly configured with an API key."""
        return bool(self.api_key) and SerpAPIWrapper is not None
