#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import os
# from flask import current_app
from ..common.utils import DoRequest

LOGGER = logging.getLogger(__name__)

GRYU_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'gryu/v1.0'
}

JOB_CONFIGS = 'job_configs'
JOBS = 'jobs'


class CcccRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('CCCC_ENDPOINT', 'http://cccc:80'),
                              os.getenv('CCCC_API_PORT', 'v1'))
    headers = GRYU_HEADERS


class JobClient(object):

    @classmethod
    def list_job_configs(cls, uuids):
        if not uuids:
            return []
        query_dict = {
            'uuids': ','.join(uuids)
        }
        LOGGER.debug(query_dict)
        return CcccRequest.send(JOB_CONFIGS, method='GET', data=query_dict)['data']

    @classmethod
    def create_job_configs(cls, data):
        data = CcccRequest.send(JOB_CONFIGS, method='POST', data=data)['data']
        LOGGER.info('data: {}'.format(data))
        return data

    @classmethod
    def retrieve_job_configs(cls, config_uuid):
        return CcccRequest.send('{}/{}'.format(JOB_CONFIGS, config_uuid), method='GET')['data']

    @classmethod
    def update_job_configs(cls, data, config_uuid):
        return CcccRequest.send('{}/{}'.format(JOB_CONFIGS, config_uuid),
                                method='PUT', data=data)['data']

    @classmethod
    def delete_job_configs(cls, config_uuid):
        return CcccRequest.send('{}/{}'.format(JOB_CONFIGS, config_uuid),
                                method='DELETE')['data']

    @classmethod
    def list_jobs(cls, uuids, page, page_size):
        query_dict = {
            'page': page,
            'page_size': page_size,
            'uuids': ','.join(uuids)
        }
        return CcccRequest.send(JOBS, method='GET', data=query_dict)['data']

    @classmethod
    def start_job(cls, data):
        return CcccRequest.send(JOBS, method='POST', data=data)['data']

    @classmethod
    def retrieve_job(cls, job_uuid):
        return CcccRequest.send('{}/{}'.format(JOBS, job_uuid), method='GET')['data']

    @classmethod
    def stop_job(cls, job_uuid):
        return CcccRequest.send('{}/{}'.format(JOBS, job_uuid), method='PUT')['data']

    @classmethod
    def delete_job(cls, job_uuid):
        return CcccRequest.send('{}/{}'.format(JOBS, job_uuid), method='DELETE')['data']

    @classmethod
    def get_job_logs(cls, job_uuid, start_time, end_time, limit):
        query_dict = {
            'start_time': start_time,
            'end_time': end_time,
            'limit': limit
        }
        return CcccRequest.send('{}/{}/logs'.format(JOBS, job_uuid),
                                method='GET',
                                params=query_dict)['data']