#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Blueprint

books_bp = Blueprint('books', __name__)

from . import views
