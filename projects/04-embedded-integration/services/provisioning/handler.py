"""AWS Lambda entrypoint. The API Gateway must authenticate and authorize webhooks.

A trusted authorizer must set `webhookAuthorized=True`. The application-level
protection should additionally validate signatures / replay protection at edge.
"""
import json
import os

from core import InvalidEvent, provision_tenant
from workato_client import WorkatoClient, WorkatoError


def lambda_handler(event, context, client=None, invite_queue=None):
    authorizer = (event.get('requestContext') or {}).get('authorizer') or {}
    trusted = authorizer.get('lambda', authorizer)
    if trusted.get('webhookAuthorized') is not True:
        return _reply(401, {'error': 'unauthorized'})
    try:
        raw = event.get('body')
        if not isinstance(raw, str) or len(raw) > 100_000:
            raise InvalidEvent('invalid_body')
        body = json.loads(raw)
        workato = client or WorkatoClient(os.environ['WORKATO_API_BASE_URL'], os.environ['WORKATO_API_TOKEN'])
        result = provision_tenant(body, workato, invite_queue=invite_queue)
        return _reply(200, result)
    except (InvalidEvent, ValueError, json.JSONDecodeError) as exc:
        return _reply(400, {'error': str(exc)})
    except (WorkatoError, KeyError):
        return _reply(502, {'error': 'upstream_service_error'})
    except Exception:
        return _reply(500, {'error': 'internal_server_error'})


def _reply(status, body):
    return {'statusCode': status, 'headers': {'Content-Type': 'application/json', 'Cache-Control': 'no-store'}, 'body': json.dumps(body)}
