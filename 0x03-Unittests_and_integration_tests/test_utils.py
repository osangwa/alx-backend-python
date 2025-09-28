#!/usr/bin/env python3
"""
Unit tests for the utils module
"""

import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock, PropertyMock

from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for the access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test access_nested_map with valid paths"""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b'),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """Test access_nested_map raises KeyError for invalid paths"""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(f"'{expected_key}'", str(context.exception))


class TestGetJson(unittest.TestCase):
    """Test cases for the get_json function"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test get_json returns expected result without making actual HTTP calls"""
        # Configure the mock
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Call the function
        result = get_json(test_url)

        # Assertions
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test cases for the memoize decorator"""

    def test_memoize(self):
        """Test that memoize decorator caches method results"""

        class TestClass:
            """Test class for memoize testing"""

            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        # Create instance and mock a_method
        with patch.object(TestClass, 'a_method') as mock_method:
            mock_method.return_value = 42
            test_instance = TestClass()

            # Call the property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # Assertions
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            mock_method.assert_called_once()