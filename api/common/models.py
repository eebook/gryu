#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy import Integer

db = SQLAlchemy()

__all__ = ["User"]


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(24), unique=True)
    email = Column(String(254), unique=True)
    is_active = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    password_hash = None

    def __repr__(self):
        return '<User:%s>' % self.username

    def __str__(self):
        return self.username

    @property
    def is_active(self):
        return self.is_active

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, raw):
        return check_password_hash(self.password_hash, raw)

