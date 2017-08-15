#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from .models import Users, ActivationKeys, EncryptedTokens
from ..common.database import db
from .exceptions import UserException

logger = logging.getLogger(__name__)


def create_user(user):
    try:
        user = Users(**user)
        ak = ActivationKeys(users=user)
        db.session.add(user)
        db.session.add(ak)
        db.session.commit()
    except Exception as e:
        logger.error("Creating user, got error, traceback: {}".format(e))
        raise UserException(code='unknown_issue')
    return user
