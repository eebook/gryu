#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy

from api.common.database import db
from api import create_app

CURRENT_CONFIG_ENV = os.getenv('CURRENT_CONFIG_ENV', 'dev')

app = create_app(config_name=CURRENT_CONFIG_ENV)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)



if __name__ == "__main__":
    manager.run()
