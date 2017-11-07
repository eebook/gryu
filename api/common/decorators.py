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

__all__ = ['RedisCache']

def singleton(cls):
    obj = cls()
    # Always return the same object
    cls.__new__ = staticmethod(lambda cls: obj)
    try:
        del cls.__init__
    except AttributeError:
        pass
    return cls


@singleton
class Poc(object):
    def printfff(self):
        print("asdfs")


if __name__ == '__main__':
    p1 = Poc()
    p2 = Poc()
    p1.printfff()
    print('p1.id: {}'.format(id(p1)))
    print('p2.id: {}'.format(id(p2)))
