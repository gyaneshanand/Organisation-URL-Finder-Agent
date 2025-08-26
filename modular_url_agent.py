"""
Modular URL Agent with pluggable search providers.
"""
import os
from typing import List, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from search_providers import SearchProviderFactory
from config import SearchConfig
from prompt_provider import PromptProvider

# Load environment
load_dotenv()

# Verify API key is available
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please add it to your .env file.")

# Configure LangSmith if enabled
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
            
            print("✅ LangSmith tracing enabled")
            print(f"📊 Project: {os.getenv('LANGSMITH_PROJECT', 'default')}")
            
        except ImportError:
            print("⚠️  LangSmith not installed. Install with: pip install langsmith")
        except Exception as e:
            print(f"⚠️  Failed to setup LangSmith: {e}")

# Initialize LangSmith
setup_langsmith()

# Define URL validator function
def url_validator(url: str) -> str:
    """Fetches the URL and returns text if 'grant' or 'foundation' is found."""
    try:
        import requests
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        r = requests.get(url, timeout=5)
        r.raise_for_status()  # Raise an exception for bad status codes
        txt = r.text.lower()
        return url if ("grant" in txt or "foundation" in txt) else ""
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return ""
    except Exception as e:
        print(f"Unexpected error validating URL {url}: {e}")
# Create URL validation tool
validate_url_tool = Tool(
    name="validate_url",
    description="Fetches the URL and returns text if 'grant' or 'foundation' is found.",
    func=url_validator
)


class ModularURLAgent:
    """Modular URL Agent that can switch between different search providers."""
    
    def __init__(self, 
                 search_provider: str = None,
                 config: SearchConfig = None,
                 llm_model: str = "gpt-4",
                 llm_temperature: float = 0.1,
                 prompt_variation: int = 1,
                 foundation_data: dict = None):
        """
        Initialize the modular URL agent.
        
        Args:
            search_provider: Name of the search provider to use
            config: SearchConfig instance, will create default if None
            llm_model: OpenAI model to use
            llm_temperature: Temperature for the LLM
            prompt_variation: Which prompt variation to use (1, 2, 3, etc.)
            foundation_data: Optional foundation data dict with keys:
                - foundation_name, ein, foundation_contact, foundation_address,
                - foundation_city, foundation_website_text
        """
        self.config = config or SearchConfig.from_env()
        self.llm = ChatOpenAI(temperature=llm_temperature, model=llm_model)
        self.prompt_variation = prompt_variation
        self.foundation_data = foundation_data
        
        # Set up search provider
        if search_provider:
            self.search_provider = SearchProviderFactory.create_provider(
                search_provider, 
                **self.config.get_provider_config(search_provider)
            )
        else:
            self.search_provider = SearchProviderFactory.create_best_available_provider(
                preferred_order=self.config.provider_preference,
                **self.config.get_provider_config(self.config.default_provider)
            )
        
        # Set up tools
        self.search_tool = self.search_provider.get_search_tool()
        self.tools = [self.search_tool, validate_url_tool]
        
        # Set up agent
        self._setup_agent()
    
    def _setup_agent(self):
        """Set up the LangChain agent with the search tools."""
        # Get the system prompt from PromptProvider
        system_prompt = PromptProvider.get_prompt(
            variation=self.prompt_variation,
            search_provider_name=self.search_provider.get_provider_name(),
            foundation_data=self.foundation_data
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            max_execution_time=60
        )
    
    def switch_search_provider(self, provider_name: str):
        """
        Switch to a different search provider.
        
        Args:
            provider_name: Name of the new search provider
        """
        print(f"🔄 Switching from {self.search_provider.get_provider_name()} to {provider_name}")
        
        self.search_provider = SearchProviderFactory.create_provider(
            provider_name,
            **self.config.get_provider_config(provider_name)
        )
        
        self.search_tool = self.search_provider.get_search_tool()
        self.tools = [self.search_tool, validate_url_tool]
        self._setup_agent()
        
        print(f"✅ Now using {self.search_provider.get_provider_name()}")
    
    def switch_prompt_variation(self, variation: int):
        """
        Switch to a different prompt variation.
        
        Args:
            variation: Prompt variation number
        """
        old_variation = self.prompt_variation
        self.prompt_variation = variation
        self._setup_agent()
        print(f"🔄 Switched from prompt variation {old_variation} to {variation}")
        print(f"📝 Variation {variation}: {PromptProvider.get_variation_description(variation)}")
    
    def update_foundation_data(self, foundation_data: dict):
        """
        Update foundation data and refresh the agent.
        
        Args:
            foundation_data: Dictionary containing foundation information
        """
        self.foundation_data = foundation_data
        self._setup_agent()
        print(f"📊 Foundation data updated and agent refreshed")
    
    def get_current_prompt_info(self) -> dict:
        """Get information about the current prompt variation."""
        return {
            "variation": self.prompt_variation,
            "description": PromptProvider.get_variation_description(self.prompt_variation),
            "search_provider": self.search_provider.get_provider_name()
        }
    
    def list_prompt_variations(self):
        """List all available prompt variations."""
        PromptProvider.list_all_variations()
    
    def find_foundation_url(self, name: str) -> str:
        """
        Find the official URL for a foundation.
        
        Args:
            name: Name of the foundation/organization
            
        Returns:
            str: The official URL or error message
        """
        print(f"🔍 Searching for '{name}' using {self.search_provider.get_provider_name()}")
        
        # Generate search variations based on config
        search_variations = [
            variation.format(name=name) for variation in self.config.search_variations
        ]
        
        # Add a general search prompt
        search_variations.append(
            f"I am looking for the homepage URL of the organization: '{name}'. Please search for the official website and return only the URL."
        )
        
        for i, prompt_text in enumerate(search_variations):
            try:
                print(f"🔍 Attempt {i+1}: {prompt_text}")
                response = self.agent_executor.invoke({"input": prompt_text})
                result = response["output"].strip()
                
                # Check if we got a valid URL
                if result.startswith("http") and not ("sorry" in result.lower() or "unable" in result.lower()):
                    print(f"✅ Found URL on attempt {i+1}: {result}")
                    return result
                    
            except Exception as e:
                print(f"❌ Attempt {i+1} failed: {e}")
                continue
        
        return f"Unable to find URL for {name} after multiple attempts with {self.search_provider.get_provider_name()}"
    
    def get_available_providers(self) -> List[str]:
        """Get list of available search providers."""
        return SearchProviderFactory.get_available_providers()
    
    def get_current_provider(self) -> str:
        """Get the name of the current search provider."""
        return self.search_provider.get_provider_name()


def main():
    """Example usage of the modular URL agent with prompt variations."""
    
    # Create agent with default provider and prompt variation
    agent = ModularURLAgent(prompt_variation=1)
    
    print(f"Available providers: {agent.get_available_providers()}")
    print(f"Current provider: {agent.get_current_provider()}")
    
    # Show current prompt info
    print(f"Current prompt info: {agent.get_current_prompt_info()}")
    
    # List all available prompt variations
    print("\n" + "="*50)
    agent.list_prompt_variations()
    print("="*50 + "\n")
    
    # Search for a foundation with default prompt
    foundation_name = "The William Penn Foundation"
    print(f"🔍 Testing with prompt variation 1:")
    url = agent.find_foundation_url(foundation_name)
    print(f"✅ Result: {url}")
    
    # Example: Switch to a different prompt variation
    print(f"\n🔄 Switching to prompt variation 2...")
    agent.switch_prompt_variation(2)
    url2 = agent.find_foundation_url(foundation_name)
    print(f"✅ Result with variation 2: {url2}")
    
    # Example: Switch to a different provider (if available)
    try:
        agent.switch_search_provider("tavily")
        url3 = agent.find_foundation_url(foundation_name)
        print(f"✅ Result with Tavily: {url3}")
    except Exception as e:
        print(f"Could not switch to Tavily: {e}")


if __name__ == "__main__":
    main()
