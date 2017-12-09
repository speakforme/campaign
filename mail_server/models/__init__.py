# -*- coding: utf-8 -*-

from coaster.sqlalchemy import IdMixin, TimestampMixin, BaseMixin, BaseNameMixin, JsonDict
from coaster.db import db
from coaster.utils import LabeledEnum
from flask_lastuser.sqlalchemy import UserBase2, ProfileBase
from .user import *
from baseframe import __


class Organization(ProfileBase, db.Model):
    __tablename__ = 'organization'


class Campaign(BaseNameMixin, db.Model):
    __tablename__ = 'campaign'
    __uuid_primary_key__ = True

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=True)
    organization = db.relationship(Organization, backref=db.backref('campaigns', cascade='all, delete-orphan'))
    contact_email = db.Column(db.Unicode(254), nullable=False, unique=True)


class MailAccount(BaseMixin, db.Model):
    __tablename__ = 'mail_account'
    __table_args__ = (db.UniqueConstraint('organization_id', 'friendly_id'),)

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=True)
    organization = db.relationship(Organization, backref=db.backref('accounts', cascade='all, delete-orphan'))

    friendly_id = db.Column(db.Unicode(255), nullable=False)
    email = db.Column(db.Unicode(254), nullable=False, unique=True)
 

class Subscriber(BaseMixin, db.Model):
    __tablename__ = 'subscriber'

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=True)
    organization = db.relationship(Organization, backref=db.backref('subscribers', cascade='all, delete-orphan'))
    email = db.Column(db.Unicode(254), nullable=False, unique=True)
    first_name = db.Column(db.Unicode(255), nullable=True)


class Subscription(BaseMixin, db.Model):
    __tablename__ = 'subscription'

    campaign_id = db.Column(None, db.ForeignKey('campaign.id'), nullable=False)
    campaign = db.relationship(Campaign, backref=db.backref('subscriptions', cascade='all, delete-orphan'))
    subscriber_id = db.Column(None, db.ForeignKey('subscriber.id'), nullable=False)
    subscriber = db.relationship(Subscriber, backref=db.backref('subscriptions', cascade='all, delete-orphan'))
    active = db.Column(db.Boolean, nullable=False, default=True)
    unsubscribed_at = db.Column(db.DateTime, nullable=True)


class MailThread(BaseMixin, db.Model):
    __tablename__ = 'mail_thread'
    __uuid_primary_key__ = True
    
    account_id = db.Column(None, db.ForeignKey('mail_account.id'), nullable=False)
    account = db.relationship(MailAccount, backref=db.backref('threads', cascade='all, delete-orphan'))
    subject = db.Column(db.Unicode(255), nullable=False)


class MailMessage(BaseMixin, db.Model):
    __tablename__ = 'mail_message'
    __uuid_primary_key__ = True

    from_address = db.Column(db.Unicode(254), nullable=False)
    headers = db.Column(db.UnicodeText(), nullable=False)
    body = db.Column(db.UnicodeText(), nullable=True)
    thread_id = db.Column(None, db.ForeignKey('mail_thread.id'), nullable=False)
    thread = db.relationship(MailThread, backref=db.backref('messages', cascade='all, delete-orphan'))


class RESPONDER_FREQUENCY(LabeledEnum):
    FIRST_TIME = (0, __("First time"))
    EVERY_TIME = (1, __("Every time"))


class AutoResponder(BaseMixin, db.Model):
    __tablename__ = 'auto_responder'

    campaign_id = db.Column(None, db.ForeignKey('campaign.id'), nullable=False)
    campaign = db.relationship(Campaign, backref=db.backref('responders', cascade='all, delete-orphan'))
    subject = db.Column(db.Unicode(255), nullable=False)
    template = db.Column(db.UnicodeText(), nullable=True)
    frequency = db.Column(db.Integer, default=RESPONDER_FREQUENCY.FIRST_TIME, nullable=False)
