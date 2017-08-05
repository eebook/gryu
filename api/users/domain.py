#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from . import infra
from ..common.exceptions import FieldValidateFaield
from ..common import status
from sqlalchemy import or_
from .models import Users, ActivationKeys
from .exceptions import UserException

logger = logging.getLogger(__name__)


def create_user(user):
    def _validate_signup(user):
        logger.debug("Validate signup, user info: {}".format(user))
        username = user.get('username', None)
        email = user.get('email', None)

        queryset = Users.query.filter(
            or_(Users.username == username,
                Users.email == email,
                )).all()
        if len(queryset) != 0:
            if username in [i.username for i in queryset]:
                raise UserException('username_already_exist')
            if email in [i.email for i in queryset]:
                raise UserException('email_already_exist')

    _validate_signup(user)
    user = infra.create_user(user)
    logger.debug("Successfully created user, user info: {}".format(user.to_dict(exclude=['_password'])))
    # TODO: Send an email with an activation code
    return user.to_dict(exclude=['_password'])


def check_user_exist(request_args):
    def _retrieve_user(_username, _email):
        logger.debug("Retrieving user with account {}/{}".format(_username, _email))
        if not _username and not _email:
            raise FieldValidateFaield(["Username or email is required"])
        if _username is not None:
            user = Users.query.filter_by(username=_username).first()
            if not user:
                raise UserException('user_not_exist', message_params=_username)
            return
        user = Users.query.filter_by(email=_email).first()
        if not user:
            raise UserException('user_not_exist', message_params=_username)

    username = request_args.get("username", None)
    email = request_args.get("email", None)

    _retrieve_user(username, email)
    return '', status.HTTP_204_NO_CONTENT


def activate_user(activate_key):
    key = ActivationKeys.query.filter_by(uuid=activate_key).all()
    if len(key) != 0:
        key = key[0]
        user = key.users
        if user.activate():
            key.delete()
    return '', status.HTTP_204_NO_CONTENT

