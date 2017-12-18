import json
import requests

class Postal(object):
    def __init__(self, key, base_url):
        self.key = key
        self.base_url = base_url

    def receive(self, request):
        email = json.loads(request.data)
        return {
            'from_address': email['mail_from'],
            'to_address': email['rcpt_to'],
            'subject': email['subject'],
            'body': email['plain_body'],
            'body_html': email['html_body'],
            'headers': "",
            'message_id': email['message_id']
        }

    def send(self, options):
        url = "{base_url}/api/v1/send/message".format(base_url=self.base_url)
        payload = {
            'to': [options['to']],
            'from': options['from'],
            'subject': options['subject'],
            'plain_body': options['body'],
            'headers': options.get('headers', {}),
            'cc': options.get('cc', []),
            'bcc': options.get('bcc', []),
            'reply_to': options.get('reply_to', '')
        }
        headers = {
            'X-Server-API-Key': "{key}".format(key=self.key),
            'content-type': "application/json"
        }
        resp = requests.post(url, data=payload, headers=headers)
        return {
            'message_id': resp.messageId
        }
