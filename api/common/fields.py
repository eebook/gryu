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
        # print("process bind param, type of value???{}".format(type(value.decode())))
        result = EEBookCipher().encrypt(value)
        print("type???{}".format(type(result)))
        return result

    def process_result_value(self, value, dialect):
        return EEBookCipher().safe_decrypt(value)

