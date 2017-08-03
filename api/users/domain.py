#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from . import infra

logger = logging.getLogger(__name__)


def create_user(user):
    """
    TODO
    """
    logger.debug("creating user, user???{}".format(user))
    user = infra.create_user(user)
    print("domain create_user")
    logger.debug("domain creating user: {}".format(user))
    return {"dict": "dict"}
