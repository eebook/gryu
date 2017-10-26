#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals


import logging
import time
from datetime import datetime
from dateutil import tz
from flask import request, g, current_app

from ..common.utils import json, token_auth
from ..common import status
from ..common.validation import schema
from . import books_bp
from ..resources import infra
from ..resources.models import Resources
from ..search.clients import SearchClient
from .exceptions import BooksException

UUID_REGEX = '[a-fA-F0-9-_.]{36}'
LOGGER = logging.getLogger(__name__)


@books_bp.route('/', methods=["GET"])
@books_bp.route('/', methods=["POST"])
@json
@schema('create_book.json')
@token_auth.login_required
def list_create_book():
    # To refactor with job
    def _validate_resource(_data):
        LOGGER.info('Validate for creating books, data: %s', _data)
        book_name = _data.get('book_name')
        queryset = Resources.query.filter_by(
            name=book_name,
            type='BOOK',
            created_by=username
        ).all()
        if len(queryset) != 0:
            raise BooksException('book_name_conflict')

    user = g.user
    username = user.username
    if request.method == "GET":
        LOGGER.info('List books')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['PAGINATE_BY']))
        pagination_obj = Resources.query.filter_by(created_by=username, type='BOOK').paginate(page, page_size, error_out=True)
        result = [
            {
                'name': item.name,
                'created_at': str(item.created_at),
                'uuid': item.uuid
            } for item in pagination_obj.items
        ]
        to_return = {
            "results": result,
            "count": pagination_obj.total,
            "page_num": pagination_obj.page,
            "page_size": pagination_obj.per_page,
            "page_total": pagination_obj.pages
        }
        return to_return
    elif request.method == "POST":
        data = request.json.copy()
        LOGGER.info('Create a book with data: %s', data)
        _validate_resource(data)

        resource_data = {
            'name': data['book_name'],
            'type': 'BOOK',
            'created_by': username,
            'uuid': data['uuid'],
            'is_public': data['is_public']
        }
        try:
            infra.create_resource(resource_data)
        except Exception as e:
            LOGGER.error('Got unknow error: %s', e.message)
            raise BooksException('unknown_issue')

        return {"book_uuid": data['uuid']}, status.HTTP_201_CREATED

@books_bp.route('/detail/<regex("{}"):book_uuid>/'.format(UUID_REGEX), methods=["GET", "DELETE"])
@json
@token_auth.login_required
def get_delete_book(book_uuid):
    if request.method == "GET":
        LOGGER.info('Get book, book id: %s', book_uuid)
        book_res = infra.get_resource_obj(None, None, None, _uuid=book_uuid)
        book_result = SearchClient.get_book(book_uuid)
        book_result["result"]["is_public"] = book_res.is_public
        return book_result
    elif request.method == "DELETE":
        # TODO, SearchClient should add this method, epub file should be deleted
        LOGGER.info('Delete book, book id: %s', book_uuid)
        return {}, status.HTTP_204_NO_CONTENT
    elif request.method == "PUT":
        LOGGER.info('Change books permission')
        return

@books_bp.route('/detail/<regex("{}"):book_uuid>/'.format(UUID_REGEX), methods=["PUT"])
@json
@schema('update_book_permission.json')
@token_auth.login_required
def update_book_permission(book_uuid):
    LOGGER.info("Update book's permission, book_id: %s, with data: %s", book_uuid, request.json)
    infra.update_resource(_uuid=book_uuid, **request.json)
    return {}, status.HTTP_204_NO_CONTENT
