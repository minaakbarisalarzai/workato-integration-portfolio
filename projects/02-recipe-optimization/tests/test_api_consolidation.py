"""Offline tests for five-call API orchestration; no network is used."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('optimized', ROOT / '01-api-consolidation/optimized.py')
optimized = importlib.util.module_from_spec(spec)
spec.loader.exec_module(optimized)


class FakeResponse:
    def __init__(self, code, data):
        self.status_code = code
        self._data = data

    def json(self):
        if isinstance(self._data, Exception):
            raise self._data
        return self._data


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.urls = []

    def get(self, url, **kwargs):
        self.urls.append(url)
        return self.responses.pop(0)


class APITests(unittest.TestCase):
    def responses(self):
        return [FakeResponse(200, {"id": 1, "name": "Leanne Graham"}),
                FakeResponse(200, [{}] * 10),
                FakeResponse(200, [{}] * 5),
                FakeResponse(200, [{}] * 20),
                FakeResponse(200, [{}] * 10)]

    def test_happy_path(self):
        session = FakeSession(self.responses())
        result = optimized.run({"user_id": 1, "post_id": 1}, session)
        self.assertTrue(result["success"])
        self.assertEqual(result["completed_operations"], 5)
        self.assertEqual(result["posts_count"], 10)
        self.assertEqual(result["http_attempts_on_success"], 5)
        self.assertEqual(len(session.urls), 5)

    def test_name_mismatch_is_informational(self):
        result = optimized.run({"user_id": 1, "expected_name": "Other"}, FakeSession(self.responses()))
        self.assertTrue(result["success"])
        self.assertFalse(result["name_matches"])

    def test_invalid_id_rejected(self):
        for value in ("x", "1a", "0", -1, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                optimized.run({"user_id": value}, FakeSession([]))

    def test_404_stops_early(self):
        session = FakeSession([FakeResponse(404, {})])
        result = optimized.run({"user_id": 1}, session)
        self.assertFalse(result["success"])
        self.assertEqual(result["completed_operations"], 0)
        self.assertEqual(result["error_count"], 1)
        self.assertEqual(len(session.urls), 1)

    def test_bad_json_stops_early(self):
        session = FakeSession([FakeResponse(200, ValueError('bad json'))])
        result = optimized.run({"user_id": 1}, session)
        self.assertFalse(result["success"])
        self.assertIn('valid JSON', result["error_message"])

    def test_retry_503_then_succeed(self):
        session = FakeSession([FakeResponse(503, {}), *self.responses()])
        with patch.object(optimized.time, 'sleep'):
            result = optimized.run({"user_id": 1}, session)
        self.assertTrue(result["success"])
        self.assertEqual(len(session.urls), 6)
        self.assertEqual(result["http_attempts_on_success"], 6)

    def test_bad_response_type(self):
        session = FakeSession([FakeResponse(200, [])])
        result = optimized.run({"user_id": 1}, session)
        self.assertFalse(result["success"])
        self.assertIn('unexpected', result["error_message"])


if __name__ == '__main__':
    unittest.main()
