#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
from flask_script import Manager
from flask import Flask


CONFIG = os.path.abspath("./local_config.py")

# app = create_app(CONFIG)
app = Flask(__name__)
manager = Manager(app)


@manager.command
def hello():
    print("test")


if __name__ == "__main__":
    manager.run()
