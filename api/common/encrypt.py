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
        logger.debug("xor text, text???{}".format(text))
        logger.debug("type of text???{}".format(type(text)))
        # logger.debug("type of text???{}".format(type(text.decode())))
        logger.debug("xor text, secret_key???{}".format(self.secret_key))
        # logger.debug("WTF is ord got: {}".format([(type(x), type(y)) for (x, y) in zip(text, cycle(self.secret_key))]))
        return ''.join(chr(x ^ ord(y)) for (x, y) in zip(text, cycle(self.secret_key)))

    def encrypt(self, text):
        test_type = self._xor_text(text).strip()
        logger.debug("encrypt, type of test_type???{}".format(test_type))
        return base64.encodebytes(self._xor_text(text)).strip()

    def decrypt(self, text):
        return self._xor_text(base64.decodebytes(text))


class EEBookCipher(XORCipher):
    secret_key = SECRET_KEY
    PREFIX = os.getenv('ENCRYPT_PREFIX', 'EEBook')

    def __init__(self):
        pass

    def is_encrypted_text(self, value):
        return bool(isinstance(value, string_types) and value.startswith(self.PREFIX))

    def encrypt(self, value):
        logger.debug("EEBookCipher, value???{}".format(value))
        test_value = self.PREFIX + super(EEBookCipher, self).encrypt(value).decode()
        logger.debug("EEBookCipher, returned value???{}".format(test_value))
        return self.PREFIX + super(EEBookCipher, self).encrypt(value).decode()

    def decrypt(self, value):
        assert self.is_encrypted_text(value), ('{} can not be decrypted by EEBookCipher, '
                                               'EEBookCipher can only decrypt string that '
                                               'starts with {}'.format(value, self.PREFIX))

        value = value[len(self.PREFIX):]
        logger.debug("value??? to decrypt{}".format(value))
        return super(EEBookCipher, self).decrypt(value)

    def safe_decrypt(self, value):
        if self.is_encrypted_text(value):
            logger.debug("decrpted value???{}".format(self.decrypt(value)))
            return self.decrypt(value)
        else:
            return value
