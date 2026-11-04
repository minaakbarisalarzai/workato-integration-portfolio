"""Orchestration logic with explicit dependencies and no hardcoded credentials."""
import re

EMAIL = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
EXT_ID = re.compile(r'^[A-Za-z0-9_-]{1,64}$')


class InvalidEvent(ValueError):
    pass


def parse_tenant_event(event):
    """Parse data AFTER the event has been authenticated by the gateway."""
    if not isinstance(event, dict):
        raise InvalidEvent('event_must_be_object')
    customer = event.get('customer')
    if not isinstance(customer, dict):
        raise InvalidEvent('customer_missing')
    primary = customer.get('primary')
    if not isinstance(primary, dict):
        raise InvalidEvent('customer_primary_missing')
    name = primary.get('company-name')
    email = primary.get('email')
    external_id = str(primary.get('id', ''))
    if not isinstance(name, str) or not (1 <= len(name.strip()) <= 120):
        raise InvalidEvent('invalid_company_name')
    if not isinstance(email, str) or not EMAIL.fullmatch(email):
        raise InvalidEvent('invalid_contact_email')
    if not EXT_ID.fullmatch(external_id):
        raise InvalidEvent('invalid_external_id')
    users = event.get('users') or {}
    if not isinstance(users, dict) or len(users) > 100:
        raise InvalidEvent('invalid_collaborators')
    collaborators = []
    for item in users.values():
        if not isinstance(item, dict) or not EMAIL.fullmatch(str(item.get('email', ''))):
            raise InvalidEvent('invalid_collaborator_email')
        role = item.get('role')
        if role not in ('editor', 'viewer'):
            raise InvalidEvent('unsupported_role')
        collaborators.append({'email': item['email'], 'role': role})
    return {'name': name.strip(), 'email': email, 'external_id': external_id, 'collaborators': collaborators}


def ensure_folder_tree(client, managed_id, roots=('Sandbox', 'Production'), categories=('Sample Solution',)):
    """Idempotent-ish folder creation keyed by (parent_id, name), not name alone.

    No concurrency guarantees; use workflow locking/idempotency in production.
    """
    response = client.list_folders(managed_id)
    folders = response.get('result', []) if isinstance(response, dict) else response
    if not isinstance(folders, list):
        raise ValueError('unexpected_folder_response')
    existing = {(f.get('parent_id'), f.get('name')): f.get('id') for f in folders}
    output = {}
    for root_name in roots:
        root_id = existing.get((None, root_name))
        if root_id is None:
            root_id = client.create_folder(managed_id, root_name)['id']
        for category in categories:
            child_id = existing.get((root_id, category))
            if child_id is None:
                child_id = client.create_folder(managed_id, category, parent_id=root_id)['id']
            output[(root_name, category)] = child_id
    return output


def provision_tenant(payload, client, invite_queue=None, categories=('Sample Solution',)):
    parsed = parse_tenant_event(payload)
    managed = client.create_managed_user({
        'name': parsed['name'], 'notification_email': parsed['email'],
        'external_id': parsed['external_id'], 'auth_settings': {'type': 'workato_auth'},
    })
    managed_id = managed.get('id') or managed.get('external_id')
    if managed_id is None:
        raise ValueError('missing_managed_user_identifier')
    folders = ensure_folder_tree(client, managed_id, categories=categories)
    if invite_queue is not None and parsed['collaborators']:
        invite_queue.enqueue(managed_id, parsed['collaborators'])
    return {'managed_user_id': str(managed_id), 'folders_initialized': len(folders), 'invites_queued': bool(invite_queue and parsed['collaborators'])}
