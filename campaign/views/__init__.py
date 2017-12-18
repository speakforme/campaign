# -*- coding: utf-8 -*-

from flask import request, abort, url_for, Response
import os
import json
from coaster.views import load_models
import requests
from campaign import app
from redis import Redis
from rq import Queue
from campaign.models import db, IncomingMessage, OutgoingMessage, Subscriber, Subscription, Campaign, AutoResponder, RESPONDER_FREQUENCY
from campaign.extapi.ses import SES
from campaign.extapi.postal import Postal
from .utils import check_api_access, requires_auth, csv_response

queue = Queue('campaign', connection=Redis())


def extract_campaign_name(email):
    return email.split('@')[0].split('-')[0]

def process_outgoing_message(options):
    mail_sender = SES()
    response_subject = u"Re: {sub}".format(sub=options['incoming_subject'])
    responder = AutoResponder.query.get(options['responder_id'])
    outgoing_body = responder.get_template(options['incoming_body']).body.format(unsubscribe=options['unsubscribe_url'])

    sent_details = mail_sender.send({
        'from': options['from'],
        'to': options['to'],
        'subject': response_subject,
        'body': outgoing_body})
    sent_msg = OutgoingMessage(
        to_addresses=[options['to']],
        subject=response_subject,
        campaign_id=options['campaign_id'],
        messageid=sent_details['message_id'])
    db.session.add(sent_msg)
    db.session.commit()


@app.route('/')
def index():
    return "<a href='https://speakforme.in'>Speak For Me</a>"


@app.route('/api/1/inbox/<api_token>', methods=['POST'])
def inbox(api_token):
    check_api_access(app.config['API_TOKEN'], api_token)

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

        subscription = Subscription.query.filter(Subscription.subscriber == subscriber, Subscription.campaign == campaign).first()
        active_subscription = False
        if not subscription:
            subscription = Subscription(subscriber=subscriber, campaign=campaign)
            db.session.add(subscription)
        else:
            if not subscription.active:
                subscription.active = True
            else:
                active_subscription = True

        # TODO: check and update subscription on sendy
        if not active_subscription:
            responders = AutoResponder.query.filter(AutoResponder.campaign == campaign,
                AutoResponder.frequency == RESPONDER_FREQUENCY.FIRST_TIME).all()
            for responder in responders:
                queue.enqueue(process_outgoing_message, {
                    'from': campaign.contact_email,
                    'to': subscriber.email,
                    'incoming_subject': msg.subject,
                    'incoming_body': msg.body,
                    'campaign_id': campaign.id,
                    'responder_id': responder.id,
                    'unsubscribe_url': url_for('unsubscribe', token=subscription.token, _external=True)
                })
        db.session.commit()
        return "OK"
    abort(401)


@app.route('/subscription/<token>/unsubscribe')
@load_models(
    (Subscription, {'token': 'token'}, 'subscription')
    )
def unsubscribe(subscription):
    if subscription.active:
        subscription.active = False
    db.session.commit()
    # TODO: update subscription on sendy
    campaign = subscription.campaign
    if campaign.unsubscribe_msg:
        return campaign.unsubscribe_msg
    return "You have been unsubscibed from `{campaign}` campaign.".format(campaign=subscription.campaign.title)


@app.route('/api/1/subscribers')
@requires_auth
def subscribers():
    subs = Subscriber.query.join(Subscription).filter(Subscription.active == True)
    headers = ['email']
    rows = []
    for sub in subs:
        rows.append({'email': sub.email})
    return csv_response(headers, rows, row_type='dict')
