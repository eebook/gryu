#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..common.database import BaseModel
from ..common.serializers import ModelSerializerMixin


__all__ = ["Users"]


class Users(BaseModel, ModelSerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(10), unique=True)  # TODO: db_index?
    email = Column(String(254), unique=True)
    _password = Column('password', String(100))
    is_active = Column(Boolean, default=False)
    test = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, default=datetime.datetime.utcnow)

    activationkeys = relationship('ActivationKeys', uselist=False, back_populates='users')

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

    def activate(self):
        if not self.is_active:
            self.is_active = True
            self.save()
            return True
        return False


class ActivationKeys(BaseModel, ModelSerializerMixin):
    __tablename__ = 'activationkeys'

    uuid = Column(String(36), primary_key=True, default=uuid4)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship("Users", back_populates='activationkeys')

    def __repr__(self):
        return '<ActivationKeys:%s>' % self.uuid

    def __str__(self):
        return self.uuid


# class EncryptedToken(BaseModel, ModelSerializerMixin):
#     key = 
