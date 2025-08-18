"""
Base search provider interface for modular search functionality.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Dict
from langchain_core.tools import BaseTool


class BaseSearchProvider(ABC):
    """Abstract base class for search providers."""
    
    def __init__(self, **kwargs):
        """Initialize the search provider with configuration."""
        self.config = kwargs
    
    @abstractmethod
    def get_search_tool(self) -> BaseTool:
        """Return the langchain tool for this search provider."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of this search provider."""
        pass
    
    @abstractmethod
    def validate_configuration(self) -> bool:
        """Validate that the provider is properly configured."""
        pass
    
    def get_max_results(self) -> int:
        """Get the maximum number of results to return."""
        return self.config.get('max_results', 10)
    
    def get_timeout(self) -> int:
        """Get the timeout for search requests."""
        return self.config.get('timeout', 30)
