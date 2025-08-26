# Prompt Variation System with Foundation Data Integration

The URL Agent now supports multiple prompt variations for experimentation and optimization, with optional foundation data integration to enhance search accuracy.

## Quick Start

```python
from modular_url_agent import ModularURLAgent

# Create agent with specific prompt variation
agent = ModularURLAgent(prompt_variation=2)

# Create agent with foundation data for enhanced accuracy
foundation_data = {
    'foundation_name': 'Ford Foundation',
    'ein': '13-1684331',
    'foundation_contact': 'info@fordfoundation.org',
    'foundation_address': '320 E 43rd St',
    'foundation_city': 'New York, NY',
    'foundation_website_text': 'fordfoundation.org'
}

agent = ModularURLAgent(
    prompt_variation=4,  # Best for data integration
    foundation_data=foundation_data
)

# Switch between variations on the fly
agent.switch_prompt_variation(3)

# Update foundation data dynamically
agent.update_foundation_data(new_foundation_data)
```

## Foundation Data Integration

### Supported Data Fields
- `foundation_name`: Foundation Name
- `ein`: EIN Tax ID Number
- `foundation_contact`: Foundation Contact Information
- `foundation_address`: Foundation Address
- `foundation_city`: Foundation City
- `foundation_website_text`: Known Website Information

### Smart Data Filtering
- Only non-blank fields are included in prompts
- Empty strings, whitespace-only, and None values are automatically filtered out
- Improves prompt clarity and reduces token usage

### Example with Database Data
```python
# Get data from your database
foundation_data = {
    'foundation_name': 'Robert Wood Johnson Foundation',
    'ein': '22-2250909',
    'foundation_contact': '',  # Empty - will be filtered out
    'foundation_address': '50 College Rd E',
    'foundation_city': 'Princeton, NJ',
    'foundation_website_text': 'rwjf.org'
}

agent = ModularURLAgent(prompt_variation=4, foundation_data=foundation_data)
url = agent.find_foundation_url("Robert Wood Johnson Foundation")
```

## Available Prompt Variations

1. **Variation 1** - Original working prompt (default)
   - Balanced approach with clear instructions
   - Proven to work well in most cases
   - Foundation data integrated if provided

2. **Variation 2** - Enhanced prompt
   - More specific methodology and validation steps
   - Better for complex foundation names
   - Foundation data integrated if provided

3. **Variation 3** - Concise prompt
   - Minimal but effective approach
   - Faster processing, good for bulk operations
   - Foundation data integrated if provided

4. **Variation 4** - Detailed systematic prompt ⭐ **RECOMMENDED FOR DATA**
   - Step-by-step reasoning approach
   - **Enhanced database integration with verification phases**
   - Best for difficult-to-find foundations
   - Geographic and contact verification when data available
   - EIN cross-referencing capabilities

## Usage Examples

### Basic Usage
```python
# List all available variations
from prompt_provider import PromptProvider
PromptProvider.list_all_variations()

# Create agent with specific variation
agent = ModularURLAgent(prompt_variation=1)

# Find foundation URL
url = agent.find_foundation_url("Ford Foundation")
```

### Experimenting with Variations
```python
agent = ModularURLAgent()

# Test different variations
for variation in [1, 2, 3, 4]:
    agent.switch_prompt_variation(variation)
    url = agent.find_foundation_url("Your Foundation Name")
    print(f"Variation {variation}: {url}")
```

### Getting Prompt Information
```python
# Current prompt details
info = agent.get_current_prompt_info()
print(f"Using variation {info['variation']}: {info['description']}")

# View all variations
agent.list_prompt_variations()
```

## Adding New Prompt Variations

To add new prompt variations, edit `prompt_provider.py`:

1. Add a new method `_get_prompt_v5()` (or next number)
2. Add the variation to the `prompts` dictionary in `get_prompt()`
3. Add description in `get_variation_description()`
4. Update `get_available_variations()`

## Files

- `prompt_provider.py` - Main prompt management system
- `demo_prompt_variations.py` - Usage examples
- `test_prompt_variations.py` - Test suite for prompt system

## Testing

Run the test suite:
```bash
python3 test_prompt_variations.py
```

Run the demo:
```bash
python3 demo_prompt_variations.py
```
