# -*- coding: utf-8 -*-

from flask import request, abort
import os
import json
from coaster.views import load_models
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail
import requests
from mail_server import app
from . import index, login
from mail_server.models import db, Organization, MailAccount, MailThread, MailMessage, Subscriber, Subscription, Campaign, AutoResponder, RESPONDER_FREQUENCY


class Postal(object):
    def __init__(self, key, base_url):
        self.key = key
        self.base_url = base_url

    def receive(self, request):
        email = json.loads(request.data)
        # TODO: store the name in email['from']
        # TODO: what if to is a list?
        # TODO: how do we store the other headers?
        return {
            'from_address': email['mail_from'],
            'to_address': email['to'],
            'subject': email['subject'],
            'body': email['plain_body'],
            'body_html': email['html_body'],
            'headers': ""
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
        return requests.post(url, data=payload, headers=headers)


class SendGrid(object):
    def receive(self, request):
        email = request.form.to_dict()
        envelope = json.loads(email['envelope'])
        return {
            'from_address': envelope['from'],
            'to_address': envelope['to'][0],
            'subject': email['subject'],
            'body': email['text'],
            'body_html': email['html'],
            'headers': email['headers']
        }

    def send(self, options):
        sg = sendgrid.SendGridAPIClient(apikey=app.config.get('SENDGRID_API_KEY'))
        from_email = Email(options['from'])
        to_email = Email(options['to'])
        subject = options['subject']
        content = Content("text/plain", options['body'])
        mail = Mail(from_email, subject, to_email, content)
        return sg.client.mail.send.post(request_body=mail.get())


def extract_campaign_account(email):
    return email.split('@')[0].split('-')

@app.route('/api/1/<org>/inbox', methods=['POST'])
@load_models(
    (Organization, {'name': 'org'}, 'org')
    )
def inbox(org):
    mail_provider = Postal(key=app.config['POSTAL_API_KEY'], base_url=app.config['POSTAL_BASE_URL'])
    parsed_email = mail_provider.receive(request)

    campaign_name, account_friendly_id = extract_campaign_account(parsed_email['to_address'])
    if campaign_name and account_friendly_id:
        campaign = Campaign.query.filter(Campaign.organization == org, Campaign.name == campaign_name).first()
        account = MailAccount.query.filter(MailAccount.organization == org, MailAccount.friendly_id == account_friendly_id).first()

        # TODO: Check reply-to
        thread = MailThread(account=account, subject=parsed_email['subject'])
        db.session.add(thread)
        msg = MailMessage(thread=thread, from_address=parsed_email['from_address'],
            body=parsed_email['body'],
            headers=parsed_email['headers'])
        db.session.add(msg)

        subscriber = Subscriber.query.filter(Subscriber.organization == org,
            Subscriber.email == parsed_email['from_address']).first()
        if not subscriber:
            subscriber = Subscriber(email=parsed_email['from_address'], organization=org)
            db.session.add(subscriber)
            subscription = Subscription(subscriber=subscriber, campaign=campaign)
            db.session.add(subscription)
            responders = AutoResponder.query.filter(AutoResponder.campaign == campaign,
                AutoResponder.frequency == RESPONDER_FREQUENCY.FIRST_TIME).all()
            for responder in responders:
                mail_provider.send({
                    'from': campaign.contact_email,
                    'to': subscriber.email,
                    'subject': responder.subject,
                    'body': responder.template})
        db.session.commit()
        return "OK"
    abort(401)


@app.route('/api/1/<org>/inbox', methods=['POST'])
@load_models(
    (Organization, {'name': 'org'}, 'org')
    )
def unsubscribe(org):
    pass
