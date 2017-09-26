#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Blueprint

search_bp = Blueprint('search', __name__)

from . import views
