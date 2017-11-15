#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Blueprint

url_metadata_bp = Blueprint('url_metadata', __name__)

from . import views
