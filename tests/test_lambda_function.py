"""Lokale Funktionstests: keine AWS-Verbindung erforderlich."""

import json
import unittest
from datetime import date, datetime, timedelta, timezone
from html import escape
from unittest.mock import patch

from src.lambda_function import FACTS, fact_of_the_day, handle_request, lambda_handler


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

    def test_home_displays_daily_fact_as_html(self):
        with patch("src.lambda_function.fact_of_the_day", return_value=FACTS[0]):
            response = handle_request("GET", "/")
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(response["headers"]["Cache-Control"], "no-store")
        self.assertIs(response["isBase64Encoded"], False)
        self.assertIn("<h1>Fun Fact of the Day:</h1>", response["body"])
        self.assertIn(f"<p>{FACTS[0]['text']}</p>", response["body"])

    def test_home_escapes_fact_text(self):
        text = '<script>alert("test")</script> & ein Fact'
        with patch("src.lambda_function.fact_of_the_day", return_value={"text": text}):
            response = handle_request("GET", "/")
        self.assertIn(f"<p>{escape(text)}</p>", response["body"])
        self.assertNotIn("<script>", response["body"])

    def test_collection_has_365_distinct_nonempty_facts(self):
        self.assertEqual(len(FACTS), 365)
        self.assertEqual(len({fact["text"] for fact in FACTS}), 365)
        self.assertTrue(all(fact["text"].strip() for fact in FACTS))

    def test_every_calendar_day_has_a_different_fact(self):
        start = date(2025, 1, 1)
        ids = {fact_of_the_day(start + timedelta(days=i))["id"] for i in range(365)}
        self.assertEqual(len(ids), 365)

    def test_calendar_assignment_repeats_each_year(self):
        start = date(2025, 1, 1)
        for offset in range(365):
            day = start + timedelta(days=offset)
            with self.subTest(day=day):
                self.assertEqual(fact_of_the_day(day), fact_of_the_day(day.replace(year=2024)))

    def test_leap_day_reuses_february_28(self):
        self.assertEqual(fact_of_the_day(date(2024, 2, 29)), fact_of_the_day(date(2024, 2, 28)))
        self.assertNotEqual(fact_of_the_day(date(2024, 2, 29)), fact_of_the_day(date(2024, 3, 1)))

    def test_year_boundary(self):
        self.assertEqual(fact_of_the_day(date(2025, 12, 31)), FACTS[-1])
        self.assertEqual(fact_of_the_day(date(2026, 1, 1)), FACTS[0])

    def test_default_date_is_current_utc_date(self):
        with patch("src.lambda_function.datetime") as clock:
            clock.now.return_value = datetime(2026, 10, 3, 23, 59, tzinfo=timezone.utc)
            actual = fact_of_the_day()
        clock.now.assert_called_once_with(timezone.utc)
        self.assertEqual(actual, fact_of_the_day(date(2026, 10, 3)))

    def test_handler_returns_home_as_html(self):
        event = {"rawPath": "/", "requestContext": {"http": {"method": "GET"}}}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["Content-Type"], "text/html; charset=utf-8")

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

    def test_home_rejects_post(self):
        response = handle_request("POST", "/")
        self.assert_json_response(response, 405)
        self.assertEqual(response["headers"]["Allow"], "GET")

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
