#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import os
from ..utils import DoRequest
from .. import GRYU_HEADERS

LOGGER = logging.getLogger(__name__)


class CcccRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('CCCC_ENDPOINT', 'http://cccc:80'),
                              os.getenv('CCCC_API_VERSION', 'v1'))
    headers = GRYU_HEADERS
    target_source = os.getenv('CCCC_SOURCE', 18085)


class VhfwRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('VHFW_ENDPOINT', 'http://192.168.199.121:18087'),
                              os.getenv('VHFW_API_VERSION', 'v1'))
    headers = GRYU_HEADERS
    target_source = os.getenv('VHFW_SOURCE', 18087)


class HlvsRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('HLVS_ENDPOINT', 'http://192.168.199.121:18086'),
                              os.getenv('HLVS_API_VERSION', 'v1')
    )
    headers = GRYU_HEADERS
    target_source = os.getenv('HLVS_SOURCE', 18086)


class HlgdRequest(DoRequest):
    endpoint = '{}/{}'.format(os.getenv('HLGD_ENDPOINT', 'http://hlgd:80'),
                              os.getenv('HLGD_API_VERSION', 'v1'))
    headers = GRYU_HEADERS
    target_source = os.getenv('HLGD_SOURCE', 18089)

class GryuRequest(DoRequest):

    endpoint = "http://localhost:80/v1"

    target_source = 18083


class CourierClient(object):

    def email(self, _data):
        return HlvsRequest.send('email', method='POST', data=_data)['data']


class UrlMetadataClient(object):

    @classmethod
    def get_url_metadata(cls, _data):
        result = HlgdRequest.send('url_metadata', method='POST', data=_data)['data']
        LOGGER.info('Get url_metadata, result: {}'.format(result))
        return result

    @classmethod
    def sync_repo_metadata(cls):
        return HlgdRequest.send('url_metadata/sync', method='PUT')['data']


class EEBookClient(object):
    def __init__(self, token):
        self._token = token
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'gryu/v1.0',
            'Authorization': "token {}".format(self._token)
        }

    def get_job_config_list(self, page_size, page):
        result = GryuRequest.send("job_configs?page_size={}&page={}".format(page_size, page), headers=self.headers)['data']
        return result

    def create_job_config(self, _data):
        result = GryuRequest.send("job_configs/", method='POST', data=_data, headers=self.headers)['data']
        LOGGER.info('Create job config, result: {}'.format(result))
        return result

    def get_job_config_detail(self, config_name):
        result = GryuRequest.send("job_configs/{}/".format(config_name), method='GET', headers=self.headers)['data']
        LOGGER.info('Get job config {}, result: {}'.format(config_name, result))
        return result

    def delete_job_config(self, config_name):
        LOGGER.info("Delete config: %s", config_name)
        result = GryuRequest.send("job_configs/{}/".format(config_name), method='DELETE', headers=self.headers)['data']
        return result

    def start_job(self, _data):
        result = GryuRequest.send('jobs/', method='POST', data=_data, headers=self.headers)['data']
        LOGGER.info("Start job, result: {}".format(result))
        return result

    def get_job_detail(self, job_id):
        result = GryuRequest.send('jobs/{}/'.format(job_id), method='GET', headers=self.headers)['data']
        LOGGER.info("Get job {}'s detail, result: {}".format(job_id, result))
        return result

    def delete_job(self, job_id):
        result = GryuRequest.send('jobs/{}/'.format(job_id), method='DELETE', headers=self.headers)['data']
        LOGGER.info("Delete job {}, result: {}".format(job_id, result))
        return result

    def get_job_list(self, page_size, page, job_config_name=None):
        query_str = "jobs?page_size={}&page={}".format(page_size, page)
        if job_config_name is not None:
            query_str = query_str + "&config_name={}".format(job_config_name)
        result = GryuRequest.send(query_str, method='GET', headers=self.headers)['data']
        return result

    def get_book_list(self, page_size, page):
        query_str = "books/?page_size={}&page={}".format(page_size, page)
        result = GryuRequest.send(query_str, method='GET', headers=self.headers)['data']
        return result

    def delete_book(self, book_id):
        result = GryuRequest.send("books/{}/".format(book_id), method="DELETE", headers=self.headers)['data']
        return result

    def get_book_detail(self, book_id):
        result = GryuRequest.send('books/{}/'.format(book_id), method='GET', headers=self.headers)['data']
        LOGGER.info("Get book {}'s detail, result: {}".format(book_id, result))
        return result
