#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals


import logging
from flask import request, g, current_app

from ..common.utils import json, token_auth
from . import search_bp
from .clients import SearchClient

LOGGER = logging.getLogger(__name__)


@search_bp.route('/book', methods=["GET"])
@json
@token_auth.login_required
def search():
    if request.method == "GET":
        LOGGER.info('Search books')
        page = request.args.get('page')
        page_size = request.args.get('page_size')
        query_string= request.args.get('q')
        search_result = SearchClient.search_books(page=page,
                                                  page_size=page_size,
                                                  q=query_string)
        return search_result


@search_bp.route('/content', methods=["GET"])
@json
@token_auth.login_required
def content():
    if request.method == "GET":
        LOGGER.info('Search content')
        return {'data': 'Search content'}
