#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from flask import request

from ..common.utils import json
from . import jobs_bp, job_configs_bp


UUID_REGEX = '[a-fA-F0-9-_.]{36}'
APP_URL_REGEX = '[A-Za-z0-9-_.]+'
LOGGER = logging.getLogger(__name__)


@jobs_bp.route('/<regex("{}"):username>'.format(APP_URL_REGEX), methods=["GET", "POST"])
@json
def list_start_jobs(username):
    if request.method == "GET":
        LOGGER.info('List jobs ')
    elif request.method == "POST":
        LOGGER.info('Start a job')
    return {'asd': 'adsf'}


@jobs_bp.route('/<regex("{}"):username>/<regex("{}"):job_uuid>'.format(
    APP_URL_REGEX, UUID_REGEX), methods=["GET", "PUT", "DELETE"])
@json
def retrieve_stop_delete_jobs(username, job_uuid):
    LOGGER.info('username: %s, job_uuid: %s', username, job_uuid)
    return {'todo': 'todo'}


@jobs_bp.route('/<regex("{}"):username>/<regex("{}"):job_uuid>/logs'.format(
    APP_URL_REGEX, UUID_REGEX), methods=["GET", "PUT", "DELETE"])
@json
def get_logs(username, job_uuid):
    LOGGER.info('Get logs, username: %s, job_uuid: %s', username, job_uuid)
    return {'todo': 'todo'}


@jobs_bp.route('/<regex("{}"):username>/<regex("{}"):job_uuid>/status'.format(
    APP_URL_REGEX, UUID_REGEX), methods=["GET", "PUT", "DELETE"])
@json
def get_update_job_status(username, job_uuid):
    LOGGER.info('status, username: {}, job_uuid: {}'.format(username, job_uuid))
    return {'todo': 'todo'}


@job_configs_bp.route('/<regex("{}"):username>'.format(APP_URL_REGEX), methods=['GET', 'POST'])
@json
def list_create_job_config(username):
    LOGGER.info('list, create job config: %s', username)
    if request.method == 'GET':
        LOGGER.info('Get job config list')
    elif request.method == 'POST':
        LOGGER.info('Create a job config with data: %s', request.json)

    return {'TODO': 'TODO'}


@job_configs_bp.route('/<regex("{}"):username>/<regex("{}"):config_name>'.format(
    APP_URL_REGEX, APP_URL_REGEX), methods=["GET", "PUT", "DELETE"])
@json
def get_put_delete_job_config(username, config_name):
    LOGGER.info('get put delete job config, username: %s, config_name: %s', username, config_name)
    return {'TODO': 'TODO'}
