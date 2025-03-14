# Archon Agent Tester

An AI agent testing system built for Archon that uses OpenRouter to test AI agents for functionality, performance, reliability, and safety.

## Features

- Seamless integration with Archon's agent building system
- OpenRouter integration for accessing various AI models
- Comprehensive test case generation
- Robust test execution engine
- Detailed evaluation metrics
- Rich reporting and visualization
- Modular, extensible architecture (MCP-compliant)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from archon_agent_tester import ArchonTester

# Initialize the tester
tester = ArchonTester(archon_api_key="your-archon-key", openrouter_api_key="your-openrouter-key")

# Test an Archon agent
test_results = tester.test_agent(
    agent_id="your-agent-id",
    test_suite="functional"
)

# Generate a report
tester.generate_report(test_results, format="html")
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT