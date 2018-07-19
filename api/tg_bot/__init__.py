#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Blueprint

tg_bot_bp = Blueprint('tg_bot', __name__)

from . import views
