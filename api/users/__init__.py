#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Blueprint

USERS_BP_NAME = 'users'
USER_BP_NAME = 'user'
users_bp = Blueprint(USERS_BP_NAME, __name__)
user_bp = Blueprint(USER_BP_NAME, __name__)


from . import views  # noqa
