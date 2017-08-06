#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from .encrypt import EEBookCipher

class EncryptedCharField(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        result = EEBookCipher().encrypt(value)
        print("type???{}".format(type(result)))
        # return EEBookCipher().encrypt(value).encode()
        return result

    def process_result_value(self, value, dialect):
        return EEBookCipher().safe_decrypt(value)
        # return value + ":decrypted"

