# Prompt Variation System

The URL Agent now supports multiple prompt variations for experimentation and optimization.

## Quick Start

```python
from modular_url_agent import ModularURLAgent

# Create agent with specific prompt variation
agent = ModularURLAgent(prompt_variation=2)

# Switch between variations on the fly
agent.switch_prompt_variation(3)

# Get current prompt info
info = agent.get_current_prompt_info()
print(info)
```

## Available Prompt Variations

1. **Variation 1** - Original working prompt (default)
   - Balanced approach with clear instructions
   - Proven to work well in most cases

2. **Variation 2** - Enhanced prompt
   - More specific methodology and validation steps
   - Better for complex foundation names

3. **Variation 3** - Concise prompt
   - Minimal but effective approach
   - Faster processing, good for bulk operations

4. **Variation 4** - Detailed systematic prompt
   - Step-by-step reasoning approach
   - Best for difficult-to-find foundations

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
