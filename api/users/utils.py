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
    # RedisCache().writer.expire(redis_key, 600)   # Ten minutes
    RedisCache().writer.expire(redis_key, 6000)   # Debug
    return code


def validate_verify_code(account, code):
    cache_key = 'captcha:' + account
    real_value = RedisCache().reader.get(cache_key)
    LOGGER.info("Get account %s's real_value: %s, cache key: %s", account, real_value, cache_key)
    if real_value is None:
        return False
    real_value = int(real_value)
    if real_value == code:
        LOGGER.info('Code %s is correct', code)
        # DEBUG
        # RedisCache().writer.expire('captcha:'+account, 1)
        return True
    LOGGER.info('Validate token failed')
    return False

