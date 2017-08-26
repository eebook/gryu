#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
from .models import Resources
from ..common.database import db
from .exceptions import ResourcesException


LOGGER = logging.getLogger(__name__)


def create_resource(resource):
    try:
        resource = Resources(**resource)
        db.session.add(resource)
        db.session.commit()
    except Exception as e:
        LOGGER.error('Creating resource, got error, traceback: %s', e)
        raise ResourcesException(code='unknown_issue')
    return resource


def delete_resource(resource_obj):
    try:
        db.session.delete(resource_obj)
        db.session.commit()
    except Exception as e:
        LOGGER.error('Deleting resource, got error, traceback: %s', e)
        raise ResourcesException(code='unknown_issue')