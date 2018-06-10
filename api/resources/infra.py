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
        db.session.rollback()
        raise ResourcesException(code='unknown_issue')
    return resource


def delete_resource(resource_obj):
    try:
        db.session.delete(resource_obj)
        db.session.commit()
    except Exception as e:
        LOGGER.error('Deleting resource, got error, traceback: %s', e)
        raise ResourcesException(code='unknown_issue')


def update_resource(_uuid, **_dict):
    try:
        Resources.query.filter_by(uuid=_uuid).update(_dict)
        db.session.commit()
    except Exception as e:
        LOGGER.error('Update resource, got error, traceback: %s', e)
        raise ResourcesException(code='unknown_issue')


def get_resource_obj(_resource_name, _username, _type, _uuid=None):
    if _uuid is None:
        resource_obj = Resources.query.filter_by(
            name=_resource_name,
            created_by=_username,
            type=_type
        ).all()
    else:
        resource_obj = Resources.query.filter_by(
            uuid=_uuid
        ).all()
    if len(resource_obj) != 0:
        resource_obj = resource_obj[0]
        return resource_obj
    else:
        raise ResourcesException('resource_not_exist')
