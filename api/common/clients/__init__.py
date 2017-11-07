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

class CourierClient(object):

    def email(self, _data):
        return HlvsRequest.send('email', method='POST', data=_data)['data']
