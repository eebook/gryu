#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


from ..libs.decorators import json
from . import api


@api.route("/test", methods=["GET"])
@json
def test():
    return {}

@api.route("/auth/register", methods=["GET"])
def auth_register():
    return {}

# @api.route("/auth/exist", methods=["get"])
