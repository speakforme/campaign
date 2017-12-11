# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

from __future__ import absolute_import
from flask import Flask
from flask_migrate import Migrate
from baseframe import baseframe, assets, Version
import coaster.app
from ._version import __version__

version = Version(__version__)

# First, make an app

app = Flask(__name__, instance_relative_config=True)

# Second, import the models and views

from . import models, views, extapi  # NOQA
from .models import db

# Third, setup baseframe and assets

assets['campaign.js'][version] = 'js/app.js'
assets['campaign.css'][version] = 'css/app.css'

# Configure the app
coaster.app.init_app(app)
db.init_app(app)
db.app = app
migrate = Migrate(app, db)
baseframe.init_app(app, requires=['baseframe-bs3', 'campaign'])
