#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from .encrypt import EEBookCipher
logger = logging.getLogger(__name__)


class EncryptedCharField(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        result = EEBookCipher().encrypt(value.decode('utf-8'))
        return result

    def process_result_value(self, value, dialect):
        result = EEBookCipher().safe_decrypt(value)
        return result

