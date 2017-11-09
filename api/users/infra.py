#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from .models import Users, ActivationKeys, EncryptedTokens
from ..common.database import db
from .exceptions import UserException

LOGGER = logging.getLogger(__name__)


def create_user(user):
    try:
        user = Users(**user)
        activation_key = ActivationKeys(users=user)
        db.session.add(user)
        db.session.add(activation_key)
        db.session.commit()
    except Exception as e:
        LOGGER.error("Creating user, got error, traceback: %s", e)
        raise UserException(code='unknown_issue')
    return user


def update_user_password(_user_obj, _password):
    try:
        _user_obj.password = _password
        delete_num = EncryptedTokens.query.filter_by(user_id=_user_obj.id).delete()
        LOGGER.debug('[Update password] Delete tokens of %s, deleted number: %s', _user_obj.username, delete_num)
        db.session.add(_user_obj)
        db.session.commit()
    except Exception as e:
        LOGGER.error("Update user password, got error, traceback: %s", e)
        raise UserException(code='unknown_issue')
    return
