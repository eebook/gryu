#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from ..users.models import Users
from .utils import Diagnoser

LOGGER = logging.getLogger(__name__)
status_ok = 'OK'
status_error = 'ERROR'


def db_check():
    detail = {'status': 'OK'}
    Users.query.count()
    return detail

Diagnoser().add_check('database', db_check)
