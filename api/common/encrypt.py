import os
import base64
import itertools
from itertools import cycle

from flask import current_app
from six import string_types
from six.moves import zip

SECRET_KEY = os.getenv('SECRET_KEY', '1a62be118cd66c49c4070af5e6f6bd46cb679b38')
PREFIX = os.getenv('ENCRYPT_PREFIX', 'EEBook')


class XORCipher(object):
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def _xor_text(self, text):
        return ''.join(chr(ord(x) ^ ord(y)) for (x, y) in zip(text, cycle(self.secret_key)))

    def encrypt(self, text):
        return base64.encodestring(self._xor_text(text)).strip()

    def decrypt(self, text):
        return self._xor_text(base64.decodestring(text))


class EEBookCipher(XORCipher):
    secret_key = SECRET_KEY
    PREFIX = os.getenv('ENCRYPT_PREFIX', 'EEBook')

    def __init__(self):
        pass

    def is_encrypted_text(self, value):
        return bool(isinstance(value, string_types) and value.startswith(self.PREFIX))

    def encrypt(self, value):
        return self.PREFIX + super(EEBookCipher, self).encrypt(value)

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
