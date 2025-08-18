"""
Factory for creating search providers.
"""
from typing import Dict, Type, Optional
from .base_provider import BaseSearchProvider
from .duckduckgo_provider import DuckDuckGoProvider
from .serpapi_provider import SerpAPIProvider
from .tavily_provider import TavilyProvider


class SearchProviderFactory:
    """Factory class for creating search providers."""
    
    _providers: Dict[str, Type[BaseSearchProvider]] = {
        'duckduckgo': DuckDuckGoProvider,
        'ddg': DuckDuckGoProvider,  # Alias
        'serpapi': SerpAPIProvider,
        'google': SerpAPIProvider,  # Alias for SerpAPI with Google
        'tavily': TavilyProvider,
    }
    
    @classmethod
    def create_provider(self, provider_name: str, **kwargs) -> BaseSearchProvider:
        """
        Create a search provider instance.
        
        Args:
            provider_name: Name of the provider ('duckduckgo', 'serpapi', 'tavily')
            **kwargs: Configuration parameters for the provider
            
        Returns:
            BaseSearchProvider: Configured search provider instance
            
        Raises:
            ValueError: If provider_name is not supported
        """
        provider_name = provider_name.lower()
        
        if provider_name not in self._providers:
            available = ', '.join(self._providers.keys())
            raise ValueError(f"Unknown search provider: {provider_name}. Available providers: {available}")
        
        provider_class = self._providers[provider_name]
        return provider_class(**kwargs)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names."""
        return list(cls._providers.keys())
    
    @classmethod
    def create_best_available_provider(cls, preferred_order: Optional[list] = None, **kwargs) -> BaseSearchProvider:
        """
        Create the best available provider based on configuration.
        
        Args:
            preferred_order: List of provider names in order of preference
            **kwargs: Configuration parameters
            
        Returns:
            BaseSearchProvider: The first available and properly configured provider
        """
        if preferred_order is None:
            preferred_order = ['tavily', 'serpapi', 'duckduckgo']
        
        for provider_name in preferred_order:
            try:
                provider = cls.create_provider(provider_name, **kwargs)
                if provider.validate_configuration():
                    print(f"✅ Using search provider: {provider.get_provider_name()}")
                    return provider
                else:
                    print(f"⚠️  {provider.get_provider_name()} not properly configured, trying next...")
            except Exception as e:
                print(f"⚠️  Failed to create {provider_name} provider: {e}")
                continue
        
        # Fallback to DuckDuckGo if nothing else works
        print("🔄 Falling back to DuckDuckGo provider")
        return DuckDuckGoProvider(**kwargs)
