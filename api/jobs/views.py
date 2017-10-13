#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from flask import request, g, current_app

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


@jobs_bp.route('', methods=["GET"])
@jobs_bp.route('/', methods=["POST"])
@json
@schema('start_job.json')
@token_auth.login_required
def list_start_jobs():
    user = g.user
    username = user.username

    if request.method == "GET":
        LOGGER.info('List jobs')
        config_name  = request.args.get('config_name')
        page = request.args.get('page')
        page_size = request.args.get('page_size')
        if config_name is not None:
            config_name_list = config_name.split(',')
            resource_obj = Resources.query.filter(Resources.name.in_(config_name_list), Resources.created_by==username).all()
        else:
            resource_obj = Resources.query.filter(Resources.created_by==username).all()
        config_uuid_list = [i.uuid for i in resource_obj]
        LOGGER.info('List jobs, config uuid list: %s', config_uuid_list)
        job_list = JobClient.list_jobs(uuids=config_uuid_list, page=page, page_size=page_size)
        LOGGER.info('job_list: {}'.format(job_list))
        return job_list
    elif request.method == "POST":
        LOGGER.info('Start a job')
        data = request.json
        job_config_res = _get_resource_obj(data['config_name'], username)
        # from ..users.views import generate_api_token
        # TODO: to get token
        LOGGER.info('request header: {}'.format(request.headers))
        # LOGGER.info('user token: {}'.format(token))
        # return
        start_job_data = {
            'config_uuid': job_config_res.uuid,
            'created_by': username,
            'user_token': 'TODO: usertoken'
        }
        result = JobClient.start_job(data=start_job_data)
        return result


@jobs_bp.route('/<regex("{}"):job_uuid>/'.format(UUID_REGEX), methods=["GET", "PUT", "DELETE"])
@json
def retrieve_stop_delete_jobs(job_uuid):
    LOGGER.info('job_uuid: %s', job_uuid)
    if request.method == 'GET':
        result = JobClient.retrieve_job(job_uuid)
        LOGGER.info('Get job history: %s', result)
        if 'user_token' in result:
            result.pop('user_token')
        return result
    elif request.method == 'PUT':
        LOGGER.info('Stop a job, job uuid: %s', job_uuid)
        # result = JobClient.delete_job(job_uuid)
        result = JobClient.stop_job(job_uuid)
        LOGGER.info('Delete a job, result: %s', result)
        return {}, status.HTTP_204_NO_CONTENT
    elif request.method == 'DELETE':
        LOGGER.info('Delete a job, job uuid: %s', job_uuid)
        result = JobClient.delete_job(job_uuid)
        LOGGER.info('Delete a job, result: %s', result)
        return {}, status.HTTP_204_NO_CONTENT


@jobs_bp.route('/<regex("{}"):job_uuid>/logs/'.format(UUID_REGEX), methods=["GET", "PUT", "DELETE"])
@token_auth.login_required
def get_logs(job_uuid):
    LOGGER.info('Get logs, job_uuid: %s', job_uuid)
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 1000))
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    result = JobClient.get_job_logs(job_uuid, start_time, end_time, page_size, page)

    return result


@jobs_bp.route('/<regex("{}"):job_uuid>/status'.format(UUID_REGEX), methods=["GET", "PUT"])
@json
# @token_auth.login_required
def get_update_job_status(job_uuid):
    if request.method == 'GET':
        LOGGER.info('Get status, job_uuid: %s', job_uuid)
        result = JobClient.get_job_status(job_uuid)
        return result
    elif request.method == 'PUT':
        LOGGER.info('Update status, job_uuid: %s, data: %s', job_uuid, request.json)
        JobClient.update_job_status(job_uuid, request.json)
        return {}, status.HTTP_204_NO_CONTENT


@job_configs_bp.route('', methods=['GET'])
@job_configs_bp.route('/', methods=['POST'])
@json
@schema('create_job_config.json')
@token_auth.login_required
def list_create_job_config():
    def _validate_resource(_data):
        LOGGER.info('Validate resource, data: %s', _data)
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
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['PAGINATE_BY']))
        pagination_obj = Resources.query.filter_by(created_by=username).paginate(page, page_size, error_out=True)
        # TODO: pagination
        uuids = [item.uuid for item in pagination_obj.items]
        result = JobClient.list_job_configs(uuids=uuids)
        to_return = {"results": result, "count": pagination_obj.total, "page_num": pagination_obj.page, "page_size": pagination_obj.per_page, "page_total": pagination_obj.pages}
        return to_return
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


def _get_resource_obj(_config_name, _username):
    resource_obj = Resources.query.filter_by(name=_config_name, created_by=_username).all()
    if len(resource_obj) != 0:
        resource_obj = resource_obj[0]
        return resource_obj
    else:
        raise JobsException('job_config_not_exist')
