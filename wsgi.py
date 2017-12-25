#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import os
from api import create_app

CURRENT_CONFIG_ENV = os.getenv('CURRENT_CONFIG_ENV', 'dev')

app = create_app(config_name=CURRENT_CONFIG_ENV)
