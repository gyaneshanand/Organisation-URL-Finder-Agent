"""
DuckDuckGo search provider implementation.
"""
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import BaseTool
from .base_provider import BaseSearchProvider


class DuckDuckGoProvider(BaseSearchProvider):
    """DuckDuckGo search provider using LangChain's DuckDuckGo tool."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_results = kwargs.get('max_results', 15)
    
    def get_search_tool(self) -> BaseTool:
        """Return the DuckDuckGo search tool."""
        # return DuckDuckGoSearchRun(max_results=self.max_results)
        return DuckDuckGoSearchResults(max_results=self.max_results, region="us", language="en")

    def get_provider_name(self) -> str:
        """Return the name of this search provider."""
        return "DuckDuckGo"
    
    def validate_configuration(self) -> bool:
        """DuckDuckGo doesn't require API keys, so always valid."""
        return True
