#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from api.common.utils import get_log_config


class Config:
    LOG_HANDLER = os.getenv('LOG_HANDLER', 'debug,info,error').split(',')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_PATH = os.getenv('LOG_PATH', '/var/log/eebook/')
    LOGCONFIG = get_log_config(component='eebookorg', handlers=LOG_HANDLER, level=LOG_LEVEL, path=LOG_PATH)
    LOGCONFIG_QUEUE = ['eebook']

    DB_USER = os.getenv("DB_USER", 'postgres')
    DB_PASSWORD = os.getenv("DB_PASSWORD", None)
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_ENGINE = os.getenv("DB_ENGINE", "postgresql")
    SQLALCHEMY_DATABASE_URI = '{db_engine}://{user_name}:{password}@{hostname}/{database}'.\
                              format_map({
                                  'db_engine': DB_ENGINE,
                                  'user_name': DB_USER,
                                  'password': DB_PASSWORD,
                                  'hostname': DB_HOST,
                                  'database': DB_NAME
                              })
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.getenv('SECRET_KEY', '1a62be118cd66c49c4070af5e6f6bd46cb679b38')
    ENCRYPT_EEBook = os.getenv('ENCRYPT_PREFIX', 'EEBook')
    PAGINATE_BY = os.getenv('PAGINATE_BY', 10)

    CCCC_CLIENT = {
        'name': 'cccc',
        'endpoint': os.getenv('CCCC_ENDPOINT', 'http://cccc:80'),
        'version': os.getenv('CCCC_API_PORT', 'v1')
    }

    GRYU_HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'gryu/v1.0'
    }

    # TODO: Delete
    WTF_CSRF_SECRET_KEY = 'alasdf'
    WTF_CSRF_CHECK_DEFAULT = False

    @staticmethod
    def init_app(app):
       pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    pass


config = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig,
}
