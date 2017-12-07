# -*- coding: utf-8 -*-

from coaster.sqlalchemy import IdMixin, TimestampMixin, BaseMixin, BaseNameMixin, JsonDict
from coaster.db import db
from coaster.utils import LabeledEnum

from .user import *

from baseframe import __


class MailAccount(BaseMixin, db.Model):
    __tablename__ = 'mail_account'

    email = db.Column(db.Unicode(254), nullable=False, unique=True)
    user_id = db.Column(None, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(User, backref=db.backref('orders', cascade='all, delete-orphan'))
 

class Subscriber(BaseMixin, db.Model):
    __tablename__ = 'subscriber'

    account_id = db.Column(None, db.ForeignKey('mail_account.id'), nullable=False)
    account = db.relationship(MailAccount, backref=db.backref('subscriptions', cascade='all, delete-orphan'))

    email = db.Column(db.Unicode(254), nullable=False, unique=True)

class Subscription(BaseMixin, db.Model):
    __tablename__ = 'subscription'

    account_id = db.Column(None, db.ForeignKey('mail_account.id'), nullable=False)
    account = db.relationship(MailAccount, backref=db.backref('subscriptions', cascade='all, delete-orphan'))
    subscriber_id = db.Column(None, db.ForeignKey('mail_account.id'), nullable=False)
    subscriber = db.relationship(Subscriber, backref=db.backref('subscriptions', cascade='all, delete-orphan'))

    active = db.Column(db.Boolean, nullable=False, default=True)
    unsubscribed_at = db.Column(db.DateTime, nullable=True)
    resubscribed_at = db.Column(db.DateTime, nullable=True)


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
    headers = db.Column(JsonDict, nullable=False, default={})

    thread_id = db.Column(None, db.ForeignKey('mail_thread.id'), nullable=False)
    thread = db.relationship(MailThread, backref=db.backref('messages', cascade='all, delete-orphan'))


class RESPONDER_FREQUENCY(LabeledEnum):
    FIRST_TIME = (0, __("First time"))
    EVERY_TIME = (1, __("Every time"))


class AutoResponder(BaseMixin, db.Model):
    __tablename__ = 'auto_responder'

    account_id = db.Column(None, db.ForeignKey('mail_account.id'), nullable=False)
    account = db.relationship(MailAccount, backref=db.backref('responders', cascade='all, delete-orphan'))
    template = db.Column(db.UnicodeText(), nullable=True)

    # Eg: equals, contains.
    pattern_rel = db.Column(db.Unicode(255), nullable=False)
    # Eg: text to be compared against
    pattern_text = db.Column(db.Unicode(255), nullable=False)
    frequency = db.Column(db.Integer, default=RESPONDER_FREQUENCY.FIRST_TIME, nullable=False)
