#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Blueprint

jobs_bp = Blueprint('jobs', __name__)
job_configs_bp = Blueprint('job_configs', __name__)

from . import views
