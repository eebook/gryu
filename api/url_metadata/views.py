#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from flask import request, g, current_app

from . import url_metadata_bp
from ..common.utils import json, token_auth

LOGGER = logging.getLogger(__name__)


@url_metadata_bp.route('', methods=['POST'])
@json
@token_auth.login_required
def get_url_metadata():
    user = g.user
    username = user.username
    if request.method == "POST":
        LOGGER.info('Get url metadata')
        data = request.json
        LOGGER.info('data???{}'.format(data))
        # TODO: add url metadata client
        result = dict()
        if data['url'] == 'http://www.ruanyifeng.com/blog/atom.xml':
            result['type'] = 'rss'
            result['info'] = 'TODO'
            result['github repo'] = 'TODO'
            result['config'] = {'type': 'int', 'attr_name': 'item_num', 'display_name': 'nums of item'}
        return result
