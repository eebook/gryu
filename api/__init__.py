#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


def register_base(app):
    from flask import Request


def create_app(config=None):
    from .app import create_app
    app = create_app(config)
    return
