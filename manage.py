#!/usr/bin/env python

from coaster.manage import init_manager

import campaign
import campaign.models as models
import campaign.forms as forms
import campaign.views as views
from campaign.models import db
from campaign import app


if __name__ == '__main__':
    db.init_app(app)
    manager = init_manager(app, db, campaign=campaign, models=models, forms=forms, views=views)
    manager.run()
