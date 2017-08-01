#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

class Config:
    # Can be moved to a common package, Temporarily did not add a colored log
    def get_log_config(component, handlers, level='DEBUG', path='/var/log/eebook'):
        """Return a log config."""
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s][%(threadName)s]' +
                            '[%(name)s.%(funcName)s():%(lineno)d] %(message)s'
                },
            },
            'handlers': {
                'debug': {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': path + component + '.debug.log',
                    'maxBytes': 1024 * 1024 * 1024,
                    'backupCount': 5,
                    'formatter': 'standard',
                },
                'info': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': path + component + '.info.log',
                    'maxBytes': 1024 * 1024 * 1024,
                    'backupCount': 5,
                    'formatter': 'standard',
                },
                'error': {
                    'level': 'ERROR',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': path + component + '.error.log',
                    'maxBytes': 1024 * 1024 * 100,
                    'backupCount': 5,
                    'formatter': 'standard',
                },
                'console': {
                    'level': level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'
                },
            },
            'loggers': {
                'django': {
                    'handlers': handlers,
                    'level': 'INFO',
                    'propagate': False
                },
                'django.request': {
                    'handlers': handlers,
                    'level': 'INFO',
                    'propagate': False,
                },
                '': {
                    'handlers': handlers,
                    'level': level,
                    'propagate': False
                },
            }
        }
        return config
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
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,

    "default": DevelopmentConfig
}
