#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import time
import os
import itertools
import logging
import redis
from redis.exceptions import ConnectionError
from ..common.utils import str2int
from ..common.decorators import singleton

__all__ = ['RedisCache']


class RedisConnectionPool(object):
    redis_connection_pool = None
    redis_write_pool = None
    read_settings = {
        'host': os.environ.get('REDIS_HOST'),
        'port': int(os.environ.get('REDIS_PORT', 6379)),
        'db': os.environ.get('REDIS_DB_NAME'),
        'password': os.environ.get('REDIS_DB_PASSWORD', '')
    }
    connection_timeout = str2int(os.environ.get('REDIS_CONN_TIMEOUT'), 20)

    write_settings = {
        'host': os.environ.get('REDIS_WRITE_HOST'),
        'port': int(os.environ.get('REDIS_WRITE_PORT', 6379)),
        'db': os.environ.get('REDIS_WRITE_DB_NAME'),
        'password': os.environ.get('REDIS_WRITE_DB_PASSWORD', '')
    }

    def __init__(self):
        if self.redis_connection_pool is not None:
            return

        self._recreate_read_pool()
        if self.has_write_config():
            self._recreate_wirte_pool()

    def _create_pool(self, timeout, **params):
        return redis.BlockingConnectionPool(
            timeout=timeout,
            **params
        )

    def _recreate_read_pool(self):
        self.redis_connection_pool = self._create_pool(
            self.connection_timeout,
            **self.read_settings
        )

    def _recreate_wirte_pool(self):
        self.redis_write_pool = self._create_pool(
            self.connection_timeout,
            **self.write_settings
        )

    def has_write_config(self):
        return os.environ.get('REDIS_WRITE_HOST') and os.environ.get('REDIS_WRITE_PORT')

    def recreate_pools(self):
        self._recreate_read_pool()
        if self.has_write_config():
            self._recreate_wirte_pool()

    @property
    def read_connection_pool(self):
        if self.redis_connection_pool is None:
            self.__init__()
        return self.redis_connection_pool

    @property
    def write_connection_pool(self):
        if not self.has_write_config():
            return self.read_connection_pool
        if self.redis_write_pool is None:
            self.__init__()
        return self.redis_write_pool

@singleton
class RedisCache(object):
    _write_client = None

    def __init__(self):
        self._create_clients()
        self._lock = False
        self._lock_timeout = None
        self._lock_timeout_limit = 5
        self._lock_max_attempts = 4
        self._lock_attempt_counts = itertools.count()

    def get_client(self):
        return self._client

    @property
    def writer(self):
        if self._write_client is None:
            return self._client
        return self._write_client

    @property
    def reader(self):
        return self._client

    def _create_clients(self):
        self._recreate_read_client()
        self._recreate_write_client()

    def _recreate_read_client(self):
        self._client = redis.Redis(connection_pool=RedisConnectionPool().redis_connection_pool)

    def _recreate_write_client(self):
        if not RedisConnectionPool().has_write_config():
            return
        self._write_client = redis.Redis(connection_pool=RedisConnectionPool().redis_connection_pool)

    def reconnect(self):
        RedisConnectionPool().redis_connection_pool.disconnect()
        RedisConnectionPool().redis_connection_pool.reset()
        if RedisConnectionPool().has_write_config():
            RedisConnectionPool().write_connection_pool.disconnect()
            RedisConnectionPool().write_connection_pool.reset()
        RedisConnectionPool().recreate_pools()
        self._create_clients()

    def lock_down(self):
        self._lock_timeout = time.time()
        self._lock = True

    def lock_date_gt_limit(self):
        return (self._lock_timeout and (self._lock_timeout + self._lock_timeout_limit < time.time()))

    def is_attempt_count_overflow(self):
        return self._lock_attempt_counts.next() >= self._lock_max_attempts

    def can_connect(self):
        if self._lock and self._lock_timeout and self.lock_date_gt_limit():
            self._lock = False
            self._lock_timeout = None
        return not self._lock

    def connection_success(self):
        if self._lock_attempt_counts.next() > 0:
            self._lock_attempt_counts = itertools.count()

    def handle_exception(self, exception):
        # Only handles connection exceptions
        if not isinstance(exception, ConnectionError):
            return

        if not self._lock and self.is_attempt_count_overflow():
            self.lock_down()

    def test_connection(self):
        return self.get_client().ping()

    def not_connected(self):
        try:
            return not self.get_client().ping()
        except:
            pass
        return True

    @classmethod
    def get_temp_read_client(cls):
        return redis.Redis(connection_pool=RedisConnectionPool().redis_connection_pool)

    @classmethod
    def get_temp_write_client(cls):
        if not RedisConnectionPool().has_write_config():
            return cls.get_temp_read_client()
        return redis.Redis(connection_pool=RedisConnectionPool().write_connection_pool)
