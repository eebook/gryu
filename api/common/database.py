#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from flask import current_app

from config import config


engine = create_engine(
    config[os.getenv('CURRENT_CONFIG_ENV', 'dev')].SQLALCHEMY_DATABASE_URI,
    convert_unicode=True
)
db_session = scoped_session(sessionmaker(autocommit=True,
                                         autoflush=False,
                                         bind=engine))

logger = logging.getLogger(__name__)

class CustomBase(object):
    """This overrides the default
    `_declarative_constructor` constructor.
    It skips the attributes that are not present
    for the model, thus if a dict is passed with some
    unknown attributes for the model on creation,
    it won't complain for `unkwnown field`s.
    """
    def __init__(self, **kwargs):
        cls_ = type(self)
        for k in kwargs:
            if hasattr(cls_, k):
                setattr(self, k, kwargs[k])
            else:
                continue

    """
    Set default tablename
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    """
    Add and try to flush.
    """
    def save(self):
        db_session.add(self)
        self._flush()
        return self

    """
    Update and try to flush.
    """
    def update(self, **kwargs):
        for attr, value in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, value)
        return self.save()

    """
    Delete and try to flush.
    """
    def delete(self):
        db_session.delete(self)
        self._flush()

    """
    Try to flush. If an error is raised,
    the session is rollbacked.
    """
    def _flush(self):
        try:
            db_session.flush()
        except Exception as e:
            db_session.rollback()
            logger.error('%r' % e)
            if current_app.config['DEBUG']:
                raise e



BaseModel = declarative_base(cls=CustomBase, constructor=None)
BaseModel.query = db_session.query_property()


def init_db():
    """
    Create database if doesn't exist and create all tables.
    """
    if not database_exists(engine.url):
        create_database(engine.url)
    BaseModel.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all of the record from tables and the tables themselves. Drop the database as well.
    """
    BaseModel.metadata.drop_all(bind=engine)
    drop_database(engine.url)


db = _SQLAlchemy(session_options={
    'expire_on_commit': False,
    'autoflush': False,
})
