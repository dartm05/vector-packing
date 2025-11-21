# Tests Directory

This directory contains test scripts for validating system functionality.

## Running Tests

All tests should be run from the project root directory:

```bash
# From project root
python tests/test_simple_ga.py
python tests/test_azure_loader.py
python tests/test_production_scenario.py
```

Or run all tests using pytest:

```bash
pytest tests/
```

## Test Files

- `test_models.py` - Unit tests for core data models (VM, Server, Solution)
- `test_utils.py` - Tests for utility functions
- `test_simple_ga.py` - Tests for basic GA functionality
- `test_ga_convergence.py` - Validates GA convergence behavior
- `test_azure_loader.py` - Tests Azure dataset loader functionality and provides data statistics
- `test_production_scenario.py` - Integration tests for production-scale scenarios
- `test_woc.py` - Tests for Wisdom of Crowds implementation
- `test_woc_behavior.py` - Validates WoC behavior and diversity mechanisms

## Coverage

To run tests with coverage reporting:

```bash
pytest tests/ --cov=src --cov-report=html
```
