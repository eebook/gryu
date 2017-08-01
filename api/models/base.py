#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from contextlib import contextmanager

from flask import current_app, abort
from sqlalchemy import event, func
from flask_sqlalchemy import SQLAlchemy as _SQLAlchey


class SQLAlchemy(_SQLAlchey):
    @contextmanager
    def auto_commit(self, throw=True):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            current_app.logger.exception('%r' % e)
            if throw:
                raise e

db = SQLAlchemy(session_options={
    'expire_on_commit': False,
    'autoflush': False,
})
