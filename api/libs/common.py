#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Can be moved to a common package, Temporarily did not add a colored log
def get_log_config(component, handlers, level='DEBUG', path='/var/log/eebook'):
    """
    Return a log config.
    :param component: name of component
    :param handlers: debug, info, error
    :param level: the level of the log
    :param path: The path to the log
    :return: config for flask-logconfig
    """
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
            'werkzeug': {
                'handlers': handlers,
                'level': 'INFO',
                'propagate': False
            },
            # api can not be empty, not consistent with Django, if have time, maybe help fix this?
            'api': {
                'handlers': ['debug', 'info', 'error'],
                'level': level,
                'propagate': False
            },
        }
    }
    return config
