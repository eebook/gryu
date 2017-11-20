#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import os
from ..utils import DoRequest
from .. import GRYU_HEADERS

LOGGER = logging.getLogger(__name__)


class CcccRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('CCCC_ENDPOINT', 'http://cccc:80'),
                              os.getenv('CCCC_API_VERSION', 'v1'))
    headers = GRYU_HEADERS
    target_source = os.getenv('CCCC_SOURCE', 18085)


class VhfwRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('VHFW_ENDPOINT', 'http://192.168.199.121:18087'),
                              os.getenv('VHFW_API_VERSION', 'v1'))
    headers = GRYU_HEADERS
    target_source = os.getenv('VHFW_SOURCE', 18087)


class HlvsRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('HLVS_ENDPOINT', 'http://192.168.199.121:18086'),
                              os.getenv('HLVS_API_VERSION', 'v1')
    )
    headers = GRYU_HEADERS
    target_source = os.getenv('HLVS_SOURCE', 18086)


class HlgdRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('HLGD_ENDPOINT', 'http://hlgd:80'),
                              os.getenv('HLGD_API_VERSION', 'v1'))
    headers = GRYU_HEADERS
    target_source = os.getenv('HLGD_SOURCE', 18089)


class CourierClient(object):

    def email(self, _data):
        return HlvsRequest.send('email', method='POST', data=_data)['data']


class UrlMetadataClient(object):

    @classmethod
    def get_url_metadata(cls, _data):
        result = HlgdRequest.send('url_metadata', method='POST', data=_data)['data']
        LOGGER.info('Get url_metadata, result: {}'.format(result))
        return result

    @classmethod
    def sync_repo_metadata(cls):
        return HlgdRequest.send('url_metadata/sync', method='PUT')['data']

