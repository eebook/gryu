#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import os
from ..common.utils import DoRequest
from ..common import GRYU_HEADERS

LOGGER = logging.getLogger(__name__)

JOB_CONFIGS = 'job_configs'
JOBS = 'jobs'


class CcccRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('CCCC_ENDPOINT', 'http://cccc:80'),
                              os.getenv('CCCC_API_PORT', 'v1'))
    headers = GRYU_HEADERS
    target_source = os.getenv('CCCC_SOURCE', 18085)

class VhfwRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('VHFW_ENDPOINT', 'http://192.168.199.121:18087'),
                              os.getenv('VHFW_API_PORT', 'v1'))
    headers = GRYU_HEADERS
    target_source = os.getenv('VHFW_SOURCE', 18087)

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
        result = CcccRequest.send(JOB_CONFIGS, method='POST', data=data)['data']
        LOGGER.info('Create job config, result: {}'.format(result))
        return result

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
    def get_job_status(cls, job_uuid):
        return CcccRequest.send('{}/{}/status'.format(JOBS, job_uuid), method='GET')['data']

    @classmethod
    def update_job_status(cls, job_uuid, data):
        return CcccRequest.send('{}/{}/status/'.format(JOBS, job_uuid), method='PUT', data=data)['data']

    @classmethod
    def get_job_logs(cls, job_uuid, start_time, end_time, page_size, page):
        query_dict = {
            'start_time': start_time,
            'end_time': end_time,
            'page_size': page_size,
            'page': page,
        }
        return VhfwRequest.send('logs/{}/'.format(job_uuid),
                                method='GET',
                                params=query_dict)['data']
