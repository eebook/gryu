#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Blueprint

about_bp = Blueprint('about', __name__)

from . import views
