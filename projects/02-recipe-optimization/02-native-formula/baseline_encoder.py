"""Workato Recipe Optimization — baseline JSON-to-Base64 Python action.
Author: Mina Akbari | Input: payload (object) | Output: encoded_payload (string)
The optimized recipe replaces this *entire action* with a Workato formula:
    Payload.to_json.encode_base64
Base64 is encoding, not encryption.
"""
import base64
import json


def main(input):
    payload = input.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a JSON object.")
    required = ("customer_id", "name", "email", "status")
    for field in required:
        if field not in payload or payload[field] is None:
            raise ValueError(f"Missing required field: {field}")
    # Compact UTF-8 JSON encoding; do not log customer data.
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return {"encoded_payload": base64.b64encode(serialized.encode("utf-8")).decode("ascii")}
