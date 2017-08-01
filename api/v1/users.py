#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from flask import request

from ..libs.decorators import json
from . import api
from ..serializer.users import RegisterForm


@api.route("/auth/register", methods=["POST"])
@json
def user_register():
    """
    Register a new user.
    """
    print("request data???" + str(request.data))
    form = RegisterForm().create_api_form()
    user = form.create_user()

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


@api.route("/auth/activate/activate_key", methods=["put"])
def activate():
    """
    Activate user's email
    """
    return {
        "TODO": "activate"
    }


@api.route("/auth/generate-api-token", methods=["POST"])
def generate_api_token():
    """
    """
    return {
        "TODO": "API token"
    }
