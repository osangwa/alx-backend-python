#!/usr/bin/env python3
"""
Unit tests for the client module
"""

import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock, Mock

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for the GithubOrgClient class"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that org property returns correct data"""
        expected_data = {"login": org_name, "id": 123}
        mock_get_json.return_value = expected_data

        client = GithubOrgClient(org_name)
        result = client.org

        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, expected_data)

    def test_public_repos_url(self):
        """Test _public_repos_url property"""
        expected_payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }

        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = expected_payload
            client = GithubOrgClient("testorg")

            result = client._public_repos_url

            self.assertEqual(result, expected_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos method"""
        test_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        mock_get_json.return_value = test_payload

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = (
                "https://api.github.com/orgs/testorg/repos"
            )

            client = GithubOrgClient("testorg")
            result = client.public_repos()

            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)

            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once()

    @patch('client.get_json')
    def test_public_repos_with_license(self, mock_get_json):
        """Test public_repos method with license filter"""
        test_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": {"key": "gpl"}},
        ]
        mock_get_json.return_value = test_payload

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = (
                "https://api.github.com/orgs/testorg/repos"
            )

            client = GithubOrgClient("testorg")
            result = client.public_repos(license="apache-2.0")

            expected_repos = ["repo2"]
            self.assertEqual(result, expected_repos)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({}, "my_license", False),
        ({"license": None}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license static method"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        'org_payload': TEST_PAYLOAD[0][0],
        'repos_payload': TEST_PAYLOAD[0][1],
        'expected_repos': TEST_PAYLOAD[0][2],
        'apache2_repos': TEST_PAYLOAD[0][3],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run"""
        cls.get_patcher = patch('client.requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Side effect function for different URLs"""
            class MockResponse:
                def __init__(self, json_data):
                    self.json_data = json_data

                def json(self):
                    return self.json_data

            if "orgs/google" in url:
                return MockResponse(cls.org_payload)
            elif "repos" in url:
                return MockResponse(cls.repos_payload)
            return MockResponse({})

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are run"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test for public_repos method"""
        client = GithubOrgClient("google")
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration test for public_repos with license filter"""
        client = GithubOrgClient("google")
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)
