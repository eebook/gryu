#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from . import infra
from ..common.database import db_session
from ..common.exceptions import FieldValidateFaield
from sqlalchemy import or_
from .models import Users
from .exceptions import UserException

logger = logging.getLogger(__name__)


def create_user(user):
    def _validate_signup(user):
        logger.debug("Validate signup, user info: {}".format(user))
        username = user.get('username', None)
        email = user.get('email', None)
        queryset = db_session.query(Users).filter(
            or_(Users.username==username,
                Users.email==email,
            )).all()
        if len(queryset) != 0:
            if username in [i.username for i in queryset]:
                raise UserException('username_already_exist')
            if email in [i.email for i in queryset]:
                raise UserException('email_already_exist')

    _validate_signup(user)
    user = infra.create_user(user)
    logger.debug("Successfully created user, user info: {}".format(user.to_dict(exclude=['_password'])))
    return user.to_dict(exclude=['_password'])


def check_user_exist(request_args):
    def _retrieve_user(username, email):
        logger.debug("Retrieving user with account {}/{}".format(username, email))
        if not username and not email:
            raise FieldValidateFaield("Username or email is required")

    username = request_args.get("username", None)
    email = request_args.get("email", None)

    _retrieve_user(username, email)
    return ''
