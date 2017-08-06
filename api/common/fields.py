from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from .encrypt import EEBookCipher

class EncryptedCharField(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return bytes(EEBookCipher().encrypt(value))
        # return "encrypted: " + value

    def process_result_value(self, value, dialect):
        return EEBookCipher().safy_decrypt(value)
        # return value + ":decrypted"

