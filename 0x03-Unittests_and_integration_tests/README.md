# Unit Tests and Integration Tests

This project demonstrates unit testing and integration testing in Python using the `unittest` framework, `parameterized` for test parameterization, and `unittest.mock` for mocking.

## Project Structure
0x03-Unittests_and_integration_tests/
├── utils.py
├── client.py
├── fixtures.py
├── test_utils.py
├── test_client.py
├── init.py
├── requirements.txt
└── README.md


## Files Description

### `utils.py`
Contains utility functions:
- `access_nested_map`: Safely access nested dictionary values
- `get_json`: Fetch JSON from remote URLs
- `memoize`: Decorator to cache method results

### `client.py`
Contains `GithubOrgClient` class for interacting with GitHub organizations API.

### `fixtures.py`
Contains test data fixtures for integration testing.

### `test_utils.py`
Unit tests for the `utils` module functions.

### `test_client.py`
Unit and integration tests for the `GithubOrgClient` class.

## Testing Concepts Demonstrated

### 1. Unit Testing
- Testing individual functions in isolation
- Mocking external dependencies
- Testing both success and error cases

### 2. Integration Testing
- Testing how components work together
- Mocking only external HTTP calls
- Using real fixtures for test data

### 3. Test Patterns
- **Parameterization**: Using `@parameterized.expand` to run tests with multiple inputs
- **Mocking**: Using `unittest.mock.patch` to replace real objects with mocks
- **Property Mocking**: Mocking properties using `PropertyMock`
- **Fixture Setup/Teardown**: Using `setUpClass` and `tearDownClass` for integration tests

## Running the Tests

### Install Dependencies
```bash
pip install -r requirements.txt


Run All Tests
bash
python -m unittest discover
Run Specific Test File
bash
python -m unittest test_utils.py
python -m unittest test_client.py
Run Specific Test Class
bash
python -m unittest test_utils.TestAccessNestedMap
python -m unittest test_client.TestGithubOrgClient
Run Specific Test Method
bash
python -m unittest test_utils.TestAccessNestedMap.test_access_nested_map
Key Features
Test Coverage
Unit Tests: Test individual functions with various inputs

Exception Testing: Test error cases and exception messages

Mock Testing: Test without external dependencies

Integration Tests: Test complete workflows with real data

Best Practices
Each test is focused and tests one specific behavior

Tests are parameterized to cover multiple scenarios

Mocks are used appropriately to isolate code under test

Integration tests use realistic fixtures

Learning Objectives
By completing this project, you will understand:

The difference between unit tests and integration tests

How to use the unittest framework effectively

How to mock external dependencies using unittest.mock

How to parameterize tests to cover multiple scenarios

How to write integration tests that test component interactions

How to use fixtures for realistic test data

text

## Let me also create a simple test runner script:

```python
#!/usr/bin/env python3
"""
Test runner script for the project
"""

import unittest
import sys

def run_tests():
    """Run all tests and return the result"""
    loader = unittest.TestLoader()
    start_dir = '.'
    pattern = 'test_*.py'
    
    suite = loader.discover(start_dir, pattern)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
Installation and Setup Instructions:
Clone the repository (if applicable)

Install dependencies:

bash
pip install -r requirements.txt
Run the tests:

bash
# Run all tests
python -m unittest discover

# Or use the test runner
python test_runner.py
Key Testing Techniques Used:
Parameterized Tests: Using @parameterized.expand to test multiple inputs

Mocking HTTP Calls: Using patch to mock requests.get

Property Mocking: Using PropertyMock to mock properties

Integration Testing: Testing the complete flow with real fixtures

Exception Testing: Testing that correct exceptions are raised

This implementation provides comprehensive test coverage for both the utility functions and the GitHub client, demonstrating proper unit testing and integration testing practices.


