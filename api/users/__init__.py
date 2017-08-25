#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Blueprint

BP_NAME = 'users'
auth_bp = Blueprint(BP_NAME, __name__)

from . import views  # noqa
