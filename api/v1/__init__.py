#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint
from ..libs.decorators import json

import logging
logger = logging.getLogger(__name__)

__author__ = 'knarfeh@outlook.com'

api = Blueprint("api", __name__)


@api.route("/ping", methods=["GET"])
def ping():
    return "pong"

@api.route("/about", methods=["GET"])
@json
def about():
    logger.error("sdfasdfsd")
    return {
        "title": "Why ee-book.org exsits",
        "content": "TODO",
    }


# do this last to avoid circular dependencies
from . import users    # noqa
