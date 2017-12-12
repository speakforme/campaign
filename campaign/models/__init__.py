# -*- coding: utf-8 -*-

from coaster.sqlalchemy import IdMixin, TimestampMixin, BaseMixin, BaseNameMixin
from sqlalchemy.dialects import postgresql
from coaster.db import db
from coaster.utils import LabeledEnum, buid
from baseframe import __
import langid


class Campaign(BaseNameMixin, db.Model):
    __tablename__ = 'campaign'
    __uuid_primary_key__ = True

    contact_email = db.Column(db.Unicode(254), nullable=False)
    unsubscribe_msg = db.Column(db.UnicodeText(), nullable=True)


class Subscriber(BaseMixin, db.Model):
    __tablename__ = 'subscriber'

    email = db.Column(db.Unicode(254), nullable=False, unique=True)
    first_name = db.Column(db.Unicode(255), nullable=True)


class Subscription(BaseMixin, db.Model):
    __tablename__ = 'subscription'

    token = db.Column(db.Unicode(22), nullable=False, default=buid, unique=True)
    campaign_id = db.Column(None, db.ForeignKey('campaign.id'), nullable=False)
    campaign = db.relationship(Campaign, backref=db.backref('subscriptions', cascade='all, delete-orphan'))
    subscriber_id = db.Column(None, db.ForeignKey('subscriber.id'), nullable=False)
    subscriber = db.relationship(Subscriber, backref=db.backref('subscriptions', cascade='all, delete-orphan'))
    active = db.Column(db.Boolean, nullable=False, default=True)
    unsubscribed_at = db.Column(db.DateTime, nullable=True)


class IncomingMessage(BaseMixin, db.Model):
    __tablename__ = 'incoming_message'
    __uuid_primary_key__ = True

    from_address = db.Column(db.Unicode(254), nullable=False)
    to_address = db.Column(db.Unicode(254), nullable=False)
    subject = db.Column(db.Unicode(255), nullable=False)
    headers = db.Column(db.UnicodeText(), nullable=False)
    messageid = db.Column(db.Unicode(255), nullable=False)
    body = db.Column(db.UnicodeText(), nullable=True)
    campaign_id = db.Column(None, db.ForeignKey('campaign.id'), nullable=False)
    campaign = db.relationship(Campaign, backref=db.backref('incoming_messages', cascade='all, delete-orphan'))


class OutgoingMessage(BaseMixin, db.Model):
    __tablename__ = 'outgoing_message'
    __uuid_primary_key__ = True

    to_addresses = db.Column(postgresql.ARRAY(db.Unicode(), dimensions=1), nullable=False)
    cc_list = db.Column(postgresql.ARRAY(db.Unicode(), dimensions=1), nullable=True)
    bcc_list = db.Column(postgresql.ARRAY(db.Unicode(), dimensions=1), nullable=True)
    subject = db.Column(db.Unicode(255), nullable=False)
    headers = db.Column(db.UnicodeText(), nullable=True)
    messageid = db.Column(db.Unicode(255), nullable=False)
    campaign_id = db.Column(None, db.ForeignKey('campaign.id'), nullable=False)
    campaign = db.relationship(Campaign, backref=db.backref('outgoing_messages', cascade='all, delete-orphan'))


class RESPONDER_FREQUENCY(LabeledEnum):
    FIRST_TIME = (0, __("First time"))
    EVERY_TIME = (1, __("Every time"))


class AutoResponder(BaseMixin, db.Model):
    __tablename__ = 'auto_responder'

    campaign_id = db.Column(None, db.ForeignKey('campaign.id'), nullable=False)
    campaign = db.relationship(Campaign, backref=db.backref('responders', cascade='all, delete-orphan'))
    subject = db.Column(db.Unicode(255), nullable=False)
    frequency = db.Column(db.Integer, default=RESPONDER_FREQUENCY.FIRST_TIME, nullable=False)

    def get_template(self, txt):
        lang_code, score = langid.classify(txt)
        template = ResponseTemplate.query.filter(ResponseTemplate.lang_code == lang_code).first()
        if not template:
            template = ResponseTemplate.query.filter(ResponseTemplate.lang_code == 'en').first()
        return template


class ResponseTemplate(BaseNameMixin, db.Model):
    __tablename__ = 'response_template'
    
    auto_responder_id = db.Column(None, db.ForeignKey('auto_responder.id'), nullable=False)
    auto_responder = db.relationship(AutoResponder, backref=db.backref('templates', cascade='all, delete-orphan'))
    lang_code = db.Column(db.Unicode(3), nullable=False, default='en')
    body = db.Column(db.UnicodeText(), nullable=True)
