#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals


import logging
from flask import request, g, current_app
from ..common.utils import json
from . import about_bp

UUID_REGEX = '[a-fA-F0-9-_.]{36}'
LOGGER = logging.getLogger(__name__)


@about_bp.route('/', methods=["GET"])
@json
def about():
    """
    Return about info in markdown format, TODO: add cache
    """
    with open('/src/api/about/about.md', 'r') as f:
        content = f.read()
    return {
        "title": "## 为服务器续一秒",
        "content": content
    }
