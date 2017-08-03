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
    # TODO: Remove it
    SECRET_KEY = 'alalalala'
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
