import json
import unittest
from unittest.mock import MagicMock

from core import InvalidEvent, ensure_folder_tree, parse_tenant_event, provision_tenant
from handler import lambda_handler
from templates import FeatureNotVerified, copy_template_assets

SAMPLE = {'customer': {'primary': {'company-name': 'Sample Company', 'email': 'team@example.test', 'id': 'tenant-123'}}, 'users': {'first': {'email': 'editor@example.test', 'role': 'editor'}}}

class ProvisioningTests(unittest.TestCase):
    def test_valid_payload(self):
        self.assertEqual(parse_tenant_event(SAMPLE)['external_id'], 'tenant-123')

    def test_missing_customer(self):
        with self.assertRaises(InvalidEvent): parse_tenant_event({})

    def test_rejects_invalid_email(self):
        bad = json.loads(json.dumps(SAMPLE)); bad['customer']['primary']['email'] = 'invalid'
        with self.assertRaises(InvalidEvent): parse_tenant_event(bad)

    def test_rejects_unsupported_role(self):
        bad = json.loads(json.dumps(SAMPLE)); bad['users']['first']['role'] = 'administrator'
        with self.assertRaises(InvalidEvent): parse_tenant_event(bad)

    def test_folders_are_scoped_by_parent(self):
        client = MagicMock()
        client.list_folders.return_value = {'result': [
            {'id': 10, 'name': 'Sandbox', 'parent_id': None},
            {'id': 20, 'name': 'Production', 'parent_id': None},
            {'id': 101, 'name': 'Sample Solution', 'parent_id': 10},
            {'id': 201, 'name': 'Sample Solution', 'parent_id': 20},
        ]}
        result = ensure_folder_tree(client, 'tenant')
        self.assertEqual(result[('Sandbox', 'Sample Solution')], 101)
        self.assertEqual(result[('Production', 'Sample Solution')], 201)
        client.create_folder.assert_not_called()

    def test_provision_and_queue(self):
        client = MagicMock()
        client.create_managed_user.return_value = {'id': 'Etenant-123'}
        client.list_folders.return_value = {'result': []}
        client.create_folder.side_effect = [{'id': 1}, {'id': 11}, {'id': 2}, {'id': 22}]
        queue = MagicMock()
        out = provision_tenant(SAMPLE, client, queue)
        self.assertEqual(out['folders_initialized'], 2)
        self.assertTrue(out['invites_queued'])
        queue.enqueue.assert_called_once()

    def test_rejects_unverified_webhook(self):
        self.assertEqual(lambda_handler({'body': json.dumps(SAMPLE)}, None)['statusCode'], 401)

    def test_authenticated_handler(self):
        client = MagicMock()
        client.create_managed_user.return_value = {'id': 1}
        client.list_folders.return_value = {'result': []}
        client.create_folder.side_effect = [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}]
        event = {'requestContext': {'authorizer': {'lambda': {'webhookAuthorized': True}}}, 'body': json.dumps(SAMPLE)}
        self.assertEqual(lambda_handler(event, None, client=client)['statusCode'], 200)

    def test_template_copy_disabled(self):
        with self.assertRaises(FeatureNotVerified): copy_template_assets()

if __name__ == '__main__': unittest.main()
