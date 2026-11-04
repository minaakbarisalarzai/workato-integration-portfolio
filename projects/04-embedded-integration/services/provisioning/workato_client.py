"""Small, injectable Workato API client for a sanitized portfolio reference.

Never log authorization headers or full upstream response bodies.
"""
import json
import time
import urllib.error
import urllib.request


class WorkatoError(Exception):
    """A safe error type that omits response bodies and credentials."""


class WorkatoClient:
    def __init__(self, base_url, token, opener=None, sleep=time.sleep, attempts=3):
        if not base_url.startswith('https://') or not token:
            raise ValueError('Workato URL must be HTTPS and token must be configured')
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.opener = opener or urllib.request.urlopen
        self.sleep = sleep
        self.attempts = attempts

    def request(self, method, path, payload=None):
        if not path.startswith('/') or path.startswith('//') or '://' in path:
            raise ValueError('Invalid relative Workato API path')
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {'Authorization': f'Bearer {self.token}', 'Accept': 'application/json'}
        if data is not None:
            headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(self.base_url + path, data=data, headers=headers, method=method)
        for attempt in range(self.attempts):
            try:
                with self.opener(req, timeout=8) as response:
                    body = response.read(1_000_001)
                    if len(body) > 1_000_000:
                        raise WorkatoError('response_too_large')
                    return json.loads(body) if body else {}
            except urllib.error.HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt + 1 == self.attempts:
                    raise WorkatoError(f'workato_http_{exc.code}') from None
            except (urllib.error.URLError, TimeoutError):
                if attempt + 1 == self.attempts:
                    raise WorkatoError('workato_network_error') from None
            self.sleep(min(2 ** attempt, 4))
        raise WorkatoError('retry_exhausted')

    def create_managed_user(self, payload):
        return self.request('POST', '/managed_users', payload)

    def list_folders(self, managed_user_id):
        from urllib.parse import quote
        return self.request('GET', f'/managed_users/{quote(str(managed_user_id), safe="")}/folders')

    def create_folder(self, managed_user_id, name, parent_id=None):
        from urllib.parse import quote
        data = {'name': name}
        if parent_id is not None:
            data['parent_id'] = parent_id
        return self.request('POST', f'/managed_users/{quote(str(managed_user_id), safe="")}/folders', data)
