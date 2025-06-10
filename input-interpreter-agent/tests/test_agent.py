import unittest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import InputInterpreterAgent


class TestInputInterpreterAgent(unittest.TestCase):

    def setUp(self):
        self.agent = InputInterpreterAgent()

    def test_petstore_api(self):
        """Test with Swagger Petstore API"""
        swagger_url = "https://petstore.swagger.io/v2/swagger.json"

        analysis = self.agent.process_swagger_url(swagger_url)

        self.assertIsNotNone(analysis)
        self.assertTrue(len(analysis.endpoints) > 0)
        self.assertEqual(analysis.title, "Swagger Petstore")

        # Check if endpoints have required JMeter details
        for endpoint in analysis.endpoints:
            self.assertIsNotNone(endpoint.expected_response_codes)
            self.assertIsInstance(endpoint.headers_required, dict)
            self.assertIsInstance(endpoint.response_assertions, list)

    def test_endpoint_summary(self):
        """Test endpoint summary generation"""
        swagger_url = "https://petstore.swagger.io/v2/swagger.json"

        self.agent.process_swagger_url(swagger_url)
        summary = self.agent.get_endpoint_summary()

        self.assertIn('api_info', summary)
        self.assertIn('endpoints', summary)
        self.assertTrue(len(summary['endpoints']) > 0)


if __name__ == '__main__':
    unittest.main()