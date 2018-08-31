#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from ..common.utils import DoRequest
from ..common import GRYU_HEADERS

LOGGER = logging.getLogger(__name__)


class VhfwRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('VHFW_ENDPOINT', 'http://192.168.199.121:18087'),
                              os.getenv('VHFW_API_PORT', 'v1'))
    headers = GRYU_HEADERS


class SearchClient(object):
    @classmethod
    def search_books(cls, **args):
        LOGGER.info('Search books, args: %s', args)
        return VhfwRequest.send('book', method='GET', params=args, target_source=18087)['data']

    @classmethod
    def get_book(cls, book_uuid):
        return VhfwRequest.send('book/' + book_uuid, method='GET', target_source=18087)['data']


    @classmethod
    def delete_book(cls, book_uuid):
        LOGGER.debug('SearchClient delete book, book id: %s', book_uuid)
        VhfwRequest.send("book/" + book_uuid, method="DELETE", target_source=18087)
