# -*- coding: utf-8 -*-

from flask import request, abort, url_for
import os
import json
from coaster.views import load_models
import requests
from campaign import app
from . import index
from campaign.models import db, IncomingMessage, OutgoingMessage, Subscriber, Subscription, Campaign, AutoResponder, RESPONDER_FREQUENCY
from campaign.extapi.ses import AmazonSES, EmailMessage


class SES(object):
    def send(self, options):
        amazonSes = AmazonSES(app.config['AWS_KEY_ID'], app.config['AWS_KEY'])
        message = EmailMessage()
        message.subject = options['subject']
        message.bodyText = options['body']
        result = amazonSes.sendEmail(options['from'], options['to'], message)
        return {
            'message_id': result.messageId
        }
        

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


def extract_campaign_name(email):
    return email.split('@')[0].split('-')[0]


@app.route('/api/1/inbox', methods=['POST'])
def inbox():
    mail_provider = Postal(key=app.config['POSTAL_API_KEY'], base_url=app.config['POSTAL_BASE_URL'])
    parsed_email = mail_provider.receive(request)

    campaign_name = extract_campaign_name(parsed_email['to_address'])
    campaign = Campaign.query.filter(Campaign.name == campaign_name).first()
    if campaign:
        msg = IncomingMessage(campaign=campaign,
            from_address=parsed_email['from_address'],
            subject=parsed_email['subject'],
            to_address=parsed_email['to_address'],
            messageid=parsed_email['message_id'],
            body=parsed_email['body'],
            headers=parsed_email['headers'])
        db.session.add(msg)

        subscriber = Subscriber.query.filter(Subscriber.email == parsed_email['from_address']).first()
        if not subscriber:
            subscriber = Subscriber(email=parsed_email['from_address'])
            db.session.add(subscriber)
            subscription = Subscription(subscriber=subscriber, campaign=campaign)
            db.session.add(subscription)
            
            mail_sender = SES()
            responders = AutoResponder.query.filter(AutoResponder.campaign == campaign,
                AutoResponder.frequency == RESPONDER_FREQUENCY.FIRST_TIME).all()
            for responder in responders:
                outgoing_body = responder.get_template(msg.body).body.format(unsubscribe=url_for('unsubscribe', token=subscription.token, _external=True))
                response_subject = u"Re: {sub}".format(sub=msg.subject)
                sent_details = mail_sender.send({
                    'from': campaign.contact_email,
                    'to': subscriber.email,
                    'subject': response_subject,
                    'body': outgoing_body})
                sent_msg = OutgoingMessage(
                    to_addresses=[subscriber.email],
                    subject=response_subject,
                    campaign=campaign,
                    messageid=sent_details['message_id'])
                db.session.add(sent_msg)
        db.session.commit()
        return "OK"
    abort(401)


@app.route('/api/1/subscription/<token>/unsubscribe')
@load_models(
    (Subscription, {'token': 'token'}, 'subscription')
    )
def unsubscribe(subscription):
    if subscription.active:
        subscription.active = False
    db.session.commit()
    return "You have been unsubscibed from `{campaign}` campaign.".format(campaign=subscription.campaign.title)
