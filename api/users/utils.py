#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import random
from ..cache import RedisCache

LOGGER = logging.getLogger(__name__)


def generate_verication_code(account):
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    redis_key = 'captcha:' + account
    LOGGER.debug('Generating code %s for %s', code, redis_key)
    RedisCache().writer.set(redis_key, code)
    RedisCache().writer.expire(redis_key, 600)   # Ten minutes
    return code


def validate_verify_code(account, code):
    real_value = RedisCache().reader.get('captcha:' + account)
    LOGGER.info("Get account %s's real_value: %s", account, real_value)
    if real_value is None:
        return False
    if real_value == code:
        LOGGER.info('Code %s is correct', code)
        RedisCache().writer.expire('captcha:'+account, 1)
        return True
    LOGGER.info('Validate token failed')
    return False

