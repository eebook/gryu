#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from flask import request, g, current_app

from . import url_metadata_bp
from .exceptions import UrlMetadataException
from ..common.utils import json, token_auth
from ..common.validation import schema
from ..common.clients import UrlMetadataClient


LOGGER = logging.getLogger(__name__)


@url_metadata_bp.route('', methods=['POST'])
@json
@schema('get_url_metadata.json')
@token_auth.login_required
def get_url_metadata():
    if request.method == "POST":
        LOGGER.info('Get url metadata')
        data = request.json
        return UrlMetadataClient.get_url_metadata(data)


@url_metadata_bp.route('/sync', methods=['PUT'])
@json
@token_auth.login_required
def sync_url_metadata():
    if request.method == "PUT":
        LOGGER.info('Sync url metadata')
        return UrlMetadataClient.sync_repo_metadata()
