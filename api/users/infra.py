#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .models import Users
from .exceptions import UserException


def create_user(user):
    try:
        user = Users(**user)
        user.save()
    except Exception:
        # just for test
        raise UserException(code='unknown_issue')

    return user
