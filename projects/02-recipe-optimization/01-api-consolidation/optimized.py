"""Workato recipe optimization: consolidate five public REST requests.

Author: Mina Akbari | Portfolio demonstration (synthetic/public data)
Workato action: Fetch and Validate Related API Resources
Input fields: user_id (integer), post_id (integer), expected_name (string)
Output: see docs/WORKATO_SETUP.md

This is a read-only demonstration. Five logical HTTP operations remain five
external requests; combining them can reduce Workato action-task consumption.
"""

import time
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"
TIMEOUT_SECONDS = 8
MAX_ATTEMPTS = 2
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}
RESOURCES = (
    ("user", "/users/{user_id}"),
    ("posts", "/posts?userId={user_id}"),
    ("comments", "/posts/{post_id}/comments"),
    ("todos", "/users/{user_id}/todos"),
    ("albums", "/users/{user_id}/albums"),
)


def _positive_int(value, name):
    if isinstance(value, bool) or not str(value).strip().isdigit():
        raise ValueError(f"{name} must be a positive integer")
    number = int(str(value).strip())
    if number <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return number


def _fetch(session, name, path):
    """Get JSON with a bounded retry policy; return (data, request attempts)."""
    attempts = 0
    for attempt in range(1, MAX_ATTEMPTS + 1):
        attempts += 1
        try:
            response = session.get(
                BASE_URL + path,
                headers={"Accept": "application/json"},
                timeout=TIMEOUT_SECONDS,
            )
            status = response.status_code
            if status in RETRYABLE_STATUSES:
                if attempt < MAX_ATTEMPTS:
                    print(f"[RETRY] {name}: HTTP {status} attempt {attempt}")
                    time.sleep(1)
                    continue
                raise RuntimeError(f"{name}: HTTP {status} after {attempts} attempts")
            if status >= 400:
                raise RuntimeError(f"{name}: non-retryable HTTP {status}")
            try:
                return response.json(), attempts
            except ValueError as exc:
                raise RuntimeError(f"{name}: response is not valid JSON") from exc
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt < MAX_ATTEMPTS:
                print(f"[RETRY] {name}: {type(exc).__name__} attempt {attempt}")
                time.sleep(1)
                continue
            raise RuntimeError(f"{name}: network failure after {attempts} attempts") from exc
    raise RuntimeError(f"{name}: request attempts exhausted")


def run(input_data, session):
    """Orchestrate the five read-only requests; return a Workato-ready dictionary.

    Errors are returned as structured data instead of automatically failing the
    Workato job. Add a Workato IF action to raise/escalate if success=false.
    """
    if not isinstance(input_data, dict):
        raise ValueError("Input must be a dictionary")
    user_id = _positive_int(input_data.get("user_id", 1), "user_id")
    post_id = _positive_int(input_data.get("post_id", 1), "post_id")
    expected_name = str(input_data.get("expected_name") or "Leanne Graham").strip()

    results = {}
    errors = []
    completed = 0
    request_attempts = 0
    print(f"[START] Fetching public demo resources for user {user_id}")

    for name, template in RESOURCES:
        path = template.format(user_id=user_id, post_id=post_id)
        try:
            # _fetch counts successful calls as well as HTTP retries. On failures,
            # number of attempts cannot be reconstructed from the exception alone;
            # request_attempts is consequently only reported for success paths.
            value, attempts = _fetch(session, name, path)
            request_attempts += attempts
            if name == "user":
                if not isinstance(value, dict) or value.get("id") != user_id:
                    raise ValueError("user: unexpected user response or ID")
            elif not isinstance(value, list):
                raise ValueError(f"{name}: expected a JSON array")
            results[name] = value
            completed += 1
            print(f"[SUCCESS] {name}")
        except (ValueError, RuntimeError) as exc:
            errors.append(str(exc))
            print(f"[ERROR] {name}: {exc}")
            break  # match the baseline's sequential, fail-fast behavior

    user = results.get("user", {})
    actual_name = user.get("name", "") if isinstance(user, dict) else ""
    name_matches = bool(actual_name) and actual_name == expected_name
    # The original HTTP recipe logs its IF result rather than failing when false.
    # Keep this as an informational check in both comparisons.
    success = not errors and completed == len(RESOURCES)
    summary = {
        "user_id": user_id,
        "user_name": actual_name,
        "name_matches": name_matches,
        "posts_count": len(results.get("posts", [])),
        "comments_count": len(results.get("comments", [])),
        "todos_count": len(results.get("todos", [])),
        "albums_count": len(results.get("albums", [])),
        "completed_operations": completed,
        "success": success,
        "errors": errors,
    }
    return {
        "success": success,
        "name_matches": name_matches,
        "user_name": actual_name,
        "posts_count": summary["posts_count"],
        "comments_count": summary["comments_count"],
        "todos_count": summary["todos_count"],
        "albums_count": summary["albums_count"],
        "completed_operations": completed,
        "http_attempts_on_success": request_attempts if success else None,
        "error_count": len(errors),
        "error_message": "; ".join(errors),
        "summary": summary,
    }


def main(input):
    """Workato Python snippets entry point."""
    with requests.Session() as session:
        return run(input, session)
