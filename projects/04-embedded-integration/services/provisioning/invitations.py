"""Optional invitation enqueue adapter; no business API tokens in queue payload."""
import json

class SqsInvitationQueue:
    def __init__(self, sqs_client, queue_url):
        if not queue_url.startswith('https://'):
            raise ValueError('queue_url must use HTTPS')
        self.sqs = sqs_client
        self.url = queue_url

    def enqueue(self, managed_user_id, collaborators):
        self.sqs.send_message(QueueUrl=self.url, MessageBody=json.dumps({
            'managed_user_id': str(managed_user_id), 'collaborators': collaborators,
        }))
