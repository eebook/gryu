#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from . import infra
from ..common.exceptions import FieldValidateFaield
from ..common import status
from sqlalchemy import or_
from .models import Users, ActivationKeys, EncryptedTokens
from .exceptions import UserException

logger = logging.getLogger(__name__)


def _retrieve_user(_username, _email):
    logger.debug("Retrieving user with account {}/{}".format(_username, _email))
    if _username is None and _email is None:
        raise FieldValidateFaield(["Username or email is required"])
    if _username is not None:
        user = Users.query.filter_by(username=_username).first()
        if not user:
            raise UserException('user_not_exist', message_params=_username)
    if _email is not None:
        user = Users.query.filter_by(email=_email).first()
        if not user:
            raise UserException('user_not_exist', message_params=_email)
    return user


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
    logger.info("Successfully created user, user info: {}".format(user.to_dict(exclude=['_password'])))
    logger.debug("User\'s activation key: {}".format(user.activationkeys))
    # TODO: Send an email with an activation code
    return user.to_dict(exclude=['_password'])


def check_user_exist(request_args):
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


def generate_api_token(_user):
    # Check out whether the user has been activated, TODO: use serializer
    # TODO: active_tmp_password_users
    username = _user.get('username', None)
    email = _user.get('email', None)
    password = _user.get('password', None)

    user = _retrieve_user(_username=username, _email=email)
    if user.verify_password(password):
        logger.debug("WTF is user id???{}".format(user.id))
        # token = EncryptedTokens.get_or_create(defaults=None, user_id=user.id)[0]
        # token.delete()
        # TODO: timed to let token expire
        token = EncryptedTokens.get_or_create(defaults=None, user_id=user.id)[0]
        logger.debug("token: {}".format(token))
    else:
        logger.debug("login failed, user: {}".format(user))
        raise UserException('provided_credentials_not_correct')

    # TODO: ESClient add user_event
    result = {
        'token': token.key,
        'username': username,
        'email': email
    }

    return result
