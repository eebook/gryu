#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from ..libs.decorators import json
from . import api


@api.route("/auth/register", methods=["POST"])
@json
def user_register():
    """
    Register a new user.
    """
    return {
        "TODO": "user registration"
    }


@api.route("/auth/mobile/exist", methods=["GET"])
@json
def check_mobile_exist():
    """
    Check if the phone number already exists.
    """
    return {
        "TODO": "check, check mobile phone"
    }

@api.route("/auth/exist", methods=["GET"])
@json
def check_user_exist():
    """
    Check whether the user already exsits.
    """
    return {
        "TODO": "check, check, check"
    }


@api.route("/auth/profile", methods=["GET", "POST"])
@json
def get_user_profile():
    """
    Get the user's basic information
    """
    return {
        "TODO": "auth profile"
    }
