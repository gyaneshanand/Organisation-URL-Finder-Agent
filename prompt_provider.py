"""
Prompt Provider for URL Agent - Manages different prompt variations for experimentation.
"""

class PromptProvider:
    """Manages different system prompt variations for the URL agent."""
    
    @staticmethod
    def get_prompt(variation: int = 1, search_provider_name: str = "search provider", foundation_data: dict = None) -> str:
        """
        Get a system prompt based on the variation number.
        
        Args:
            variation: Prompt variation number (1, 2, 3, etc.)
            search_provider_name: Name of the search provider being used
            foundation_data: Optional dictionary containing foundation information:
                - foundation_name: Foundation Name
                - ein: EIN number
                - foundation_contact: Foundation Contact
                - foundation_address: Foundation Address
                - foundation_city: Foundation City
                - foundation_website_text: Foundation Website Address Text
            
        Returns:
            str: The system prompt text
        """
        prompts = {
            1: PromptProvider._get_prompt_v1(search_provider_name, foundation_data),
            2: PromptProvider._get_prompt_v2(search_provider_name, foundation_data),
            3: PromptProvider._get_prompt_v3(search_provider_name, foundation_data),
            4: PromptProvider._get_prompt_v4(search_provider_name, foundation_data),
        }
        
        if variation not in prompts:
            print(f"⚠️  Prompt variation {variation} not found, using default (v1)")
            variation = 1
            
        return prompts[variation]
    
    @staticmethod
    def _build_foundation_info_section(foundation_data: dict) -> str:
        """
        Build the foundation information section for prompts.
        Only includes non-blank data fields.
        
        Args:
            foundation_data: Dictionary containing foundation information
            
        Returns:
            str: Formatted foundation information section
        """
        if not foundation_data:
            return ""
        
        info_lines = []
        
        # Check each field and add only if not blank
        if foundation_data.get('foundation_name') and foundation_data['foundation_name'].strip():
            info_lines.append(f"- Foundation Name: {foundation_data['foundation_name'].strip()}")
        
        if foundation_data.get('ein') and foundation_data['ein'].strip():
            info_lines.append(f"- EIN: {foundation_data['ein'].strip()}")
        
        if foundation_data.get('foundation_contact') and foundation_data['foundation_contact'].strip():
            info_lines.append(f"- Contact: {foundation_data['foundation_contact'].strip()}")
        
        if foundation_data.get('foundation_address') and foundation_data['foundation_address'].strip():
            info_lines.append(f"- Address: {foundation_data['foundation_address'].strip()}")
        
        if foundation_data.get('foundation_city') and foundation_data['foundation_city'].strip():
            info_lines.append(f"- City: {foundation_data['foundation_city'].strip()}")
        
        if foundation_data.get('foundation_website_text') and foundation_data['foundation_website_text'].strip():
            info_lines.append(f"- Known Website Info: {foundation_data['foundation_website_text'].strip()}")
        
        if info_lines:
            return f"""
AVAILABLE FOUNDATION DATA:
{chr(10).join(info_lines)}

Use this information to help validate and confirm the correct foundation website.
"""
        return ""
    
    @staticmethod
    def _get_prompt_v1(search_provider_name: str, foundation_data: dict = None) -> str:
        """Original prompt - Current working version."""
        foundation_info = PromptProvider._build_foundation_info_section(foundation_data)
        
        return f"""
You are a grant assistant that finds official foundation websites using {search_provider_name}. Given an organization name, you must:
{foundation_info}
SEARCH STRATEGY (try multiple approaches):
1. Start with search: "[Foundation Name] foundation/organization"
2. If no clear result, try: "[Foundation Name] official website"
3. If still unclear, try: "[Foundation Name] .org"
4. If still unclear, try: "[Foundation Name] foundation grants"
5. If needed, try variations of the name (e.g., with/without "The", abbreviations)
6. Try searching for "[Foundation Name] homepage" or "[Foundation Name] main site"

ANALYSIS CRITERIA:
- Look for URLs that end with .org, .com, or similar domains
- Prioritize results that clearly match the foundation name
- Use the validate_url tool to check if URLs contain foundation/grant content

OUTPUT: Return ONLY the most reliable URL you find, nothing else.

Focus on finding the main official website, not news articles or other pages about the foundation.
"""

    @staticmethod
    def _get_prompt_v2(search_provider_name: str, foundation_data: dict = None) -> str:
        """Enhanced prompt with more specific instructions."""
        foundation_info = PromptProvider._build_foundation_info_section(foundation_data)
        
        return f"""
You are an expert foundation research assistant using {search_provider_name} to find official foundation websites.
{foundation_info}
MISSION: Find the PRIMARY official website URL for the given organization.

SEARCH METHODOLOGY:
1. PRIMARY: "[Organization Name] official website"
2. SECONDARY: "[Organization Name] foundation .org"
3. TERTIARY: "[Organization Name] grants homepage"
4. ALTERNATIVE: Try name variations (remove "The", use acronyms, etc.)
5. VERIFICATION: "[Organization Name] contact information"

VALIDATION REQUIREMENTS:
- Must be the organization's primary domain (not subdirectories)
- Prefer .org domains for foundations
- Avoid news articles, Wikipedia, or third-party sites
- Use validate_url tool to confirm foundation/grant content exists

SUCCESS CRITERIA:
- URL loads successfully
- Contains foundation or grant-related content
- Matches the organization name clearly

OUTPUT FORMAT: Return ONLY the verified URL, no explanations or additional text.
"""

    @staticmethod
    def _get_prompt_v3(search_provider_name: str, foundation_data: dict = None) -> str:
        """Concise and focused prompt."""
        foundation_info = PromptProvider._build_foundation_info_section(foundation_data)
        
        return f"""
Foundation URL Finder using {search_provider_name}.
{foundation_info}
TASK: Find the official website URL for the given foundation/organization.

SEARCH STEPS:
1. "[Name] official website"
2. "[Name] .org site"
3. "[Name] foundation homepage"
4. Try name variants if needed

RULES:
- Return ONLY the main website URL
- Prefer .org domains
- Validate URLs contain "foundation" or "grant" content
- Avoid news/Wikipedia links

OUTPUT: URL only, nothing else.
"""

    @staticmethod
    def _get_prompt_v4(search_provider_name: str, foundation_data: dict = None) -> str:
        """Detailed prompt with step-by-step reasoning and database integration."""
        foundation_info = PromptProvider._build_foundation_info_section(foundation_data)
        
        return f"""
You are a professional foundation research specialist using {search_provider_name} to locate official foundation websites.
{foundation_info}
OBJECTIVE: Identify and return the primary official website URL for the specified foundation or organization.

SYSTEMATIC SEARCH APPROACH:
Phase 1 - Direct Search:
- "[Foundation Name] official website"
- "[Foundation Name] homepage"

Phase 2 - Domain-Specific Search:
- "[Foundation Name] .org"
- "[Foundation Name] foundation.org"

Phase 3 - Context-Based Search:
- "[Foundation Name] grants programs"
- "[Foundation Name] about foundation"

Phase 4 - Name Variations (if needed):
- Try without articles ("The", "A")
- Try common abbreviations
- Try full vs. shortened names

Phase 5 - Geographic and Contact Verification (if data available):
- Use city/address information to verify location-specific results
- Cross-reference with known contact information
- Validate against EIN if provided

QUALITY ASSURANCE:
1. URL must be the primary domain (not subpages)
2. Must validate using the validate_url tool
3. Content must contain foundation/grant-related terms
4. Avoid third-party sites, news articles, or directories
5. Cross-reference with available foundation data for accuracy

DECISION CRITERIA:
- Official domain ownership by the organization
- Professional website design and content
- Clear foundation mission and programs
- Contact information present
- Geographic consistency with known data
- EIN verification if possible

FINAL OUTPUT: Provide ONLY the verified primary website URL.
"""

    @staticmethod
    def get_available_variations() -> list:
        """Get list of available prompt variations."""
        return [1, 2, 3, 4]
    
    @staticmethod
    def get_variation_description(variation: int) -> str:
        """Get description of a specific prompt variation."""
        descriptions = {
            1: "Original working prompt - Balanced approach with clear instructions",
            2: "Enhanced prompt with more specific methodology and validation",
            3: "Concise and focused prompt - Minimal but effective",
            4: "Detailed systematic prompt with step-by-step reasoning"
        }
        return descriptions.get(variation, "Unknown variation")
    
    @staticmethod
    def list_all_variations():
        """Print all available prompt variations with descriptions."""
        print("Available Prompt Variations:")
        print("=" * 50)
        for var in PromptProvider.get_available_variations():
            desc = PromptProvider.get_variation_description(var)
            print(f"Variation {var}: {desc}")
        print("=" * 50)


# Example usage and testing
if __name__ == "__main__":
    # List all variations
    PromptProvider.list_all_variations()
    
    # Test getting a specific prompt
    print("\n" + "="*60)
    print("SAMPLE PROMPT (Variation 2):")
    print("="*60)
    sample_prompt = PromptProvider.get_prompt(2, "Google Search")
    print(sample_prompt)
