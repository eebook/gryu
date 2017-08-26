#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from flask import request, g

from ..common.utils import json, token_auth
from ..common.validation import schema
from ..common import status
from ..common.exceptions import ServiceException
from . import jobs_bp, job_configs_bp
from .clients import JobClient
from ..resources import infra
from ..resources.models import Resources
from ..resources.exceptions import ResourcesException
from .exceptions import JobsException


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


@job_configs_bp.route('', methods=['GET', 'POST'])
@json
@schema('create_job_config.json')
@token_auth.login_required
def list_create_job_config():
    def _validate_resource(_data):
        LOGGER.info('Validate resource, data: {}'.format(_data))
        config_name = _data.get('config_name')
        LOGGER.info('Validate resource, config_name: %s', config_name)

        queryset = Resources.query.filter(
            Resources.name == _data['config_name']
        ).all()
        if len(queryset) != 0:
            raise ResourcesException('resource_name_conflict')
        # TODO: query config name to verify config_name

    user = g.user
    username = user.username
    LOGGER.info('list, create job config: %s', username)
    if request.method == 'GET':
        LOGGER.info('Get job config list')
        LOGGER.info('TODO')
        return {'todo': 'todo'}
    elif request.method == 'POST':
        data = request.json.copy()
        LOGGER.info('Create a job config with data: %s', data)
        _validate_resource(data)

        config = JobClient.create_job_configs(data=data)
        LOGGER.info('config: %s', config)

        resource_data = {
            'name': data['config_name'],
            'type': 'JOB_CONFIG',
            'created_by': username,
            'uuid': config['config_uuid']
        }
        try:
            infra.create_resource(resource_data)
        except Exception as e:
            JobClient.delete_job_configs(config_uuid=config['config_uuid'])

        return config, status.HTTP_201_CREATED


@job_configs_bp.route('/<regex("{}"):config_name>'.format(APP_URL_REGEX),
                      methods=["GET", "PUT", "DELETE"])
@json
@schema('update_job_config.json')
@token_auth.login_required
def get_put_delete_job_config(config_name):
    def _get_resource_obj(_config_name, _username):
        resource_obj = Resources.query.filter_by(name=_config_name, created_by=_username).all()
        if len(resource_obj) != 0:
            resource_obj = resource_obj[0]
            return resource_obj
        else:
            raise JobsException('job_config_not_exist')
    user = g.user
    username = user.username
    LOGGER.info('get put delete job config, username: %s, config_name: %s', username, config_name)

    if request.method == 'GET':
        LOGGER.info('Get job config, ')
        job_config_res = _get_resource_obj(config_name, username)
        job_config = JobClient.retrieve_job_configs(config_uuid=job_config_res.uuid)
        LOGGER.info('Got job_config from cccc: %s', job_config)
        return job_config

    elif request.method == 'PUT':
        LOGGER.info('Update job config, config_name: %s, with data: %s', config_name, request.json)
        job_config_res = _get_resource_obj(config_name, username)
        job_config = JobClient.update_job_configs(data=request.json,
                                                  config_uuid=job_config_res.uuid)
        LOGGER.debug('Update job config, result: %s', job_config)
        return {}, status.HTTP_204_NO_CONTENT

    elif request.method == 'DELETE':
        LOGGER.info('Delete job config, config_name: %s', config_name)
        job_config_resource = _get_resource_obj(config_name, username)
        LOGGER.info('job_config_resource to delete: %s', job_config_resource)

        try:
            JobClient.delete_job_configs(job_config_resource.uuid)
            infra.delete_resource(job_config_resource)
        except ServiceException as e:
            LOGGER.error('Removing job_config, got error, code: %s, message: %s', e.code, e.message)
            if e.status_code == status.HTTP_404_NOT_FOUND:
                infra.delete_resource(job_config_resource)
            else:
                raise e
        return {}, status.HTTP_204_NO_CONTENT


