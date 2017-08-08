#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import base64
import itertools
import logging
from itertools import cycle

from flask import current_app
from six import string_types
from six.moves import zip   # noqa

SECRET_KEY = os.getenv('SECRET_KEY', '1a62be118cd66c49c4070af5e6f6bd46cb679b38')
PREFIX = os.getenv('ENCRYPT_PREFIX', 'EEBook')
logger = logging.getLogger(__name__)


class XORCipher(object):
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def _xor_text(self, text):
        result = ''.join(chr(ord(x) ^ ord(y)) for (x, y) in zip(text, cycle(self.secret_key)))
        return result

    def encrypt(self, text):
        result = base64.encodebytes(self._xor_text(text).encode()).decode()
        return result

    def decrypt(self, text):
        result = self._xor_text(base64.decodebytes(text.encode()).decode())
        return result


class EEBookCipher(XORCipher):
    secret_key = SECRET_KEY
    PREFIX = os.getenv('ENCRYPT_PREFIX', 'EEBook')

    def __init__(self):
        pass

    def is_encrypted_text(self, value):
        return bool(isinstance(value, string_types) and value.startswith(self.PREFIX))

    def encrypt(self, value):
        encrypted_bytes = self.PREFIX + super(EEBookCipher, self).encrypt(value)
        return encrypted_bytes

    def decrypt(self, value):
        assert self.is_encrypted_text(value), ('{} can not be decrypted by EEBookCipher, '
                                               'EEBookCipher can only decrypt string that '
                                               'starts with {}'.format(value, self.PREFIX))

        value = value[len(self.PREFIX):]
        return super(EEBookCipher, self).decrypt(value)

    def safe_decrypt(self, value):
        if self.is_encrypted_text(value):
            return self.decrypt(value)
        else:
            return value
