#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import uuid
from functools import singledispatch


@singledispatch
def serialize(rv):
    """
    Define a generic serializable funtion.
    """
    return rv
