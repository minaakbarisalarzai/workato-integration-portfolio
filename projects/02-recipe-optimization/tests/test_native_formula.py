"""Offline test coverage for the baseline encoder and shared decoder."""
import base64
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(relative, label):
    spec = importlib.util.spec_from_file_location(label, ROOT / relative)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


encoder = module('02-native-formula/baseline_encoder.py', 'baseline_encoder')
decoder = module('02-native-formula/decoder.py', 'decoder')


class NativeFormulaTests(unittest.TestCase):
    def setUp(self):
        self.payload = {"customer_id": 12345, "name": "Sara Khan", "email": "sara@example.com", "status": "active"}

    def test_round_trip(self):
        encoded = encoder.main({"payload": self.payload})["encoded_payload"]
        result = decoder.main({"encoded_data": encoded})
        self.assertTrue(result["valid"])
        self.assertEqual(result["decoded_payload"], self.payload)
        self.assertEqual(result["customer_name"], "Sara Khan")

    def test_support_existing_input_name(self):
        encoded = encoder.main({"payload": self.payload})["encoded_payload"]
        self.assertEqual(decoder.main({"payload": encoded})["customer_id"], 12345)

    def test_missing_payload(self):
        with self.assertRaises(ValueError):
            encoder.main({"payload": "not an object"})

    def test_missing_field(self):
        payload = dict(self.payload)
        del payload["email"]
        with self.assertRaisesRegex(ValueError, "email"):
            encoder.main({"payload": payload})

    def test_invalid_base64(self):
        with self.assertRaises(ValueError):
            decoder.main({"encoded_data": "not-base64?"})

    def test_invalid_json(self):
        with self.assertRaises(ValueError):
            decoder.main({"encoded_data": base64.b64encode(b"not-json").decode()})

    def test_invalid_customer_id(self):
        payload = dict(self.payload)
        payload["customer_id"] = True
        encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        with self.assertRaisesRegex(ValueError, "Customer ID"):
            decoder.main({"encoded_data": encoded})

    def test_missing_email(self):
        payload = dict(self.payload)
        payload["email"] = ""
        encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        with self.assertRaisesRegex(ValueError, "Missing"):
            decoder.main({"encoded_data": encoded})

    def test_valid_unicode(self):
        payload = dict(self.payload)
        payload["name"] = "Sára خان"
        encoded = encoder.main({"payload": payload})["encoded_payload"]
        self.assertEqual(decoder.main({"encoded_data": encoded})["customer_name"], "Sára خان")


if __name__ == '__main__':
    unittest.main()
