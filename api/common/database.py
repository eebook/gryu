#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.expression import ClauseElement


db = SQLAlchemy()
logger = logging.getLogger(__name__)


class BaseModel(db.Model):
    __abstract__ = True

    # @declared_attr
    # def __tablename__(cls):
    #     return cls.__name__.lower()

    """
    Add and try to flush.
    """
    def save(self):
        db.session.add(self)
        db.session.commit()
        self._flush()
        return self

    def delete(self):
        print("WTF is self???{}".format(self))
        num = db.session.delete(self)
        print("delete num???{}".format(num))
        self._flush()
        db.session.commit()
        self._flush()
        print("delete???")
        return self

    """
    Try to flush. If an error is raised,
    the session is rollbacked.
    """
    def _flush(self):
        # try:
        #     db.session.flush()
        # except DatabaseError:
        #     db.session.rollback()
        db.session.flush()

    @classmethod
    def get_or_create(cls, defaults=None, **kwargs):
        logger.debug("cls: {}".format(cls.__dict__))
        logger.debug("defaults??? {}, kwargs??? {}".format(defaults, kwargs))
        instance = db.session.query(cls.__mapper__).filter_by(**kwargs).first()
        if instance:
            print("have instance, instance???: {}".format(instance))
            return instance, False
        else:
            params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
            params.update(defaults or {})
            instance = cls(**params)
            instance.save()
            print("creating.....instance???: {}".format(instance))
            return instance, True
