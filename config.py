"""
Configuration management for search providers.
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SearchConfig:
    """Configuration class for search providers."""
    
    # Default search provider
    default_provider: str = "duckduckgo"
    
    # Provider preference order (will try in this order)
    provider_preference: list = None
    
    # Common settings
    max_results: int = 15
    timeout: int = 30
    
    # Provider-specific settings
    serpapi_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    
    # LangSmith configuration
    langsmith_tracing: bool = False
    langsmith_endpoint: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    langsmith_project: Optional[str] = None
    
    # Search strategies
    search_variations: list = None
    
    def __post_init__(self):
        """Initialize default values after instantiation."""
        if self.provider_preference is None:
            self.provider_preference = ["tavily", "serpapi", "duckduckgo"]
        
        if self.search_variations is None:
            self.search_variations = [
                "'{name}' official website",
                "'{name}' .org domain",
                "'{name}' foundation grants homepage",
                "'{name}' organization website"
            ]
        
        # Load API keys from environment if not provided
        if self.serpapi_api_key is None:
            self.serpapi_api_key = os.getenv('SERPAPI_API_KEY')
        
        if self.tavily_api_key is None:
            self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        
        # Load LangSmith configuration from environment
        if self.langsmith_tracing is False:  # Only set if not explicitly provided
            self.langsmith_tracing = os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true'
        
        if self.langsmith_endpoint is None:
            self.langsmith_endpoint = os.getenv('LANGSMITH_ENDPOINT')
        
        if self.langsmith_api_key is None:
            self.langsmith_api_key = os.getenv('LANGSMITH_API_KEY')
        
        if self.langsmith_project is None:
            self.langsmith_project = os.getenv('LANGSMITH_PROJECT')
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get configuration dictionary for a specific provider."""
        base_config = {
            'max_results': self.max_results,
            'timeout': self.timeout
        }
        
        provider_name = provider_name.lower()
        
        if provider_name in ['serpapi', 'google']:
            base_config['api_key'] = self.serpapi_api_key
        elif provider_name == 'tavily':
            base_config['api_key'] = self.tavily_api_key
        
        return base_config
    
    @classmethod
    def from_env(cls) -> 'SearchConfig':
        """Create configuration from environment variables."""
        return cls(
            default_provider=os.getenv('DEFAULT_SEARCH_PROVIDER', 'duckduckgo'),
            max_results=int(os.getenv('MAX_SEARCH_RESULTS', '15')),
            timeout=int(os.getenv('SEARCH_TIMEOUT', '30')),
            serpapi_api_key=os.getenv('SERPAPI_API_KEY'),
            tavily_api_key=os.getenv('TAVILY_API_KEY'),
            langsmith_tracing=os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true',
            langsmith_endpoint=os.getenv('LANGSMITH_ENDPOINT'),
            langsmith_api_key=os.getenv('LANGSMITH_API_KEY'),
            langsmith_project=os.getenv('LANGSMITH_PROJECT')
        )
