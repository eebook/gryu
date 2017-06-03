#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'knarfeh@outlook.com'

from flask import Blueprint, g


api = Blueprint("api", __name__)


# do this last to avoid circular dependencies
from . import users
