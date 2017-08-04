#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, DateTime, Boolean, Integer

from ..common.database import BaseModel
from ..common.serializers import ModelSerializerMixin


__all__ = ["Users"]


class Users(BaseModel, ModelSerializerMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(24), unique=True)  # TODO: db_index?
    email = Column(String(254), unique=True)
    _password = Column('password', String(100))
    is_active = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, default=datetime.datetime.utcnow)


    def __repr__(self):
        return '<User:%s>' % self.username

    def __str__(self):
        return self.username

    # @property
    # def is_active(self):
    #     return self.is_active

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    def verify_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)
