#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy_utils import ChoiceType
from ..common.database import BaseModel
from ..common.serializers import ModelSerializerMixin

RES_JOB_CONFIG = 'JOB_CONFIG'
__all__ = ['Resources']


class Resources(BaseModel, ModelSerializerMixin):
    TYPES = [
        (RES_JOB_CONFIG, 'job config')
    ]
    __tablename__ = 'resources'
    name = Column(String(128))
    username = Column(String(15), unique=True)
    created_by = Column(String(15), ForeignKey('users.username'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    type = Column(ChoiceType(TYPES))

    def __repr__(self):
        return '<Resource:%s>' % self.name

    def __str__(self):
        return self.name
