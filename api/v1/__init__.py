#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint
from ..decorators import json

__author__ = 'knarfeh@outlook.com'

api = Blueprint("api", __name__)


@api.route("/ping", methods=["GET"])
@json
def ping():
    return []


# do this last to avoid circular dependencies
from . import users    # noqa
