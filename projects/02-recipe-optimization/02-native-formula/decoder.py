"""Workato Recipe Optimization — shared Base64 decoder and customer validation.
Author: Mina Akbari | Use identical code in BOTH recipes for a fair comparison.
Input: encoded_data (string), or payload (string) for an existing Workato schema.
Output: valid, customer_id, customer_name, email, status, decoded_payload, message.
"""
import base64
import binascii
import json


def main(input):
    encoded_data = input.get("encoded_data")
    if encoded_data is None:
        encoded_data = input.get("payload")
    if not isinstance(encoded_data, str) or not encoded_data.strip():
        raise ValueError("Base64 encoded data is required.")
    try:
        decoded = base64.b64decode(encoded_data.strip(), validate=True)
        customer = json.loads(decoded.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid Base64-encoded JSON payload.") from exc
    if not isinstance(customer, dict):
        raise ValueError("Decoded payload must be a JSON object.")
    missing = [name for name in ("customer_id", "name", "email", "status")
               if customer.get(name) is None or
               (isinstance(customer.get(name), str) and not customer[name].strip())]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))
    customer_id = customer["customer_id"]
    if type(customer_id) is not int or customer_id <= 0:
        raise ValueError("Customer ID must be a positive integer.")
    if not all(isinstance(customer[key], str) for key in ("name", "email", "status")):
        raise ValueError("Name, email, and status must be strings.")
    if "@" not in customer["email"]:  # minimal demo validation, not full email validation
        raise ValueError("Customer email format is invalid.")
    return {
        "valid": True,
        "customer_id": customer_id,
        "customer_name": customer["name"],
        "email": customer["email"],
        "status": customer["status"],
        "decoded_payload": customer,
        "message": "Payload decoded and validated successfully.",
    }
