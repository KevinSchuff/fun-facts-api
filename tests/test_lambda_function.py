"""Lokale Funktionstests: keine AWS-Verbindung erforderlich."""

import json
import unittest

from src.lambda_function import FACTS, handle_request, lambda_handler


class FunFactApiTests(unittest.TestCase):
    def assert_json_response(self, response, expected_status):
        self.assertEqual(response["statusCode"], expected_status)
        self.assertEqual(
            response["headers"]["Content-Type"],
            "application/json; charset=utf-8",
        )
        self.assertIs(response["isBase64Encoded"], False)
        self.assertIsInstance(response["body"], str)
        return json.loads(response["body"])

    def test_home_lists_endpoints(self):
        data = self.assert_json_response(handle_request("GET", "/"), 200)
        self.assertEqual(data["endpoints"], ["GET /fact", "GET /facts"])

    def test_random_fact_is_from_static_collection(self):
        data = self.assert_json_response(handle_request("GET", "/fact"), 200)
        self.assertIn(data, FACTS)

    def test_all_facts_and_count(self):
        data = self.assert_json_response(handle_request("GET", "/facts"), 200)
        self.assertEqual(data["facts"], list(FACTS))
        self.assertEqual(data["count"], len(data["facts"]))

    def test_unknown_path_returns_404(self):
        data = self.assert_json_response(handle_request("GET", "/unknown"), 404)
        self.assertIn("error", data)

    def test_other_methods_return_405(self):
        for method in ("POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"):
            with self.subTest(method=method):
                response = handle_request(method, "/fact")
                data = self.assert_json_response(response, 405)
                self.assertEqual(response["headers"]["Allow"], "GET")
                self.assertIn("error", data)

    def test_handler_reads_function_url_event(self):
        event = {
            "version": "2.0",
            "rawPath": "/facts",
            "requestContext": {
                "http": {"method": "GET", "path": "/facts"},
            },
            "isBase64Encoded": False,
        }
        data = self.assert_json_response(lambda_handler(event, None), 200)
        self.assertEqual(data["facts"], list(FACTS))

    def test_handler_preserves_request_method(self):
        event = {
            "rawPath": "/fact",
            "requestContext": {"http": {"method": "POST"}},
        }
        self.assert_json_response(lambda_handler(event, None), 405)

    def test_json_preserves_umlauts(self):
        response = handle_request("GET", "/facts")
        data = self.assert_json_response(response, 200)
        self.assertIn("Würfel", response["body"])
        self.assertIn("Würfel", data["facts"][2]["text"])


if __name__ == "__main__":
    unittest.main()
