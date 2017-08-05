#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr


db = SQLAlchemy()


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
        self._flush()
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        self._flush()
        db.session.commit()
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
