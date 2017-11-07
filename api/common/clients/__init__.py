#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import os
from ..utils import DoRequest
from .. import GRYU_HEADERS

LOGGER = logging.getLogger(__name__)


class CcccRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('CCCC_ENDPOINT', 'http://cccc:80'),
                              os.getenv('CCCC_API_PORT', 'v1'))
    headers = GRYU_HEADERS

class VhfwRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('VHFW_ENDPOINT', 'http://192.168.199.121:18087'),
                              os.getenv('VHFW_API_PORT', 'v1'))
    headers = GRYU_HEADERS


class CourierClient(object):

    def send_message(self, data):
        pass
