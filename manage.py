#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from api.models.models import db
from api import create_app

app = create_app(config_name='default')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    print("test")


if __name__ == "__main__":
    manager.run()
