#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy_utils import ChoiceType
from sqlalchemy.orm import relationship

from ..common.database import BaseModel
from ..common.serializers import ModelSerializerMixin

RES_JOB_CONFIG = 'JOB_CONFIG'
RES_BOOK = 'BOOK_BOOK'
__all__ = ['Resources']


class Resources(BaseModel, ModelSerializerMixin):
    # Not working?
    # TYPES = [
    #     (RES_JOB_CONFIG, 'job config'),
    #     (RES_BOOK, 'book')
    # ]
    __tablename__ = 'resources'
    name = Column(String(128))
    created_by = Column(String(15), ForeignKey('users.username'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    uuid = Column(String(36), unique=True, primary_key=True)
    type = Column(String(40), )
    is_public = Column(Boolean, default=False)

    users = relationship("Users", back_populates='resources')

    __table_args__ = (UniqueConstraint('name', 'type', 'created_by', name='_resource_unique'), )

    def __repr__(self):
        return '<Resource:%s>' % self.name

    def __str__(self):
        return self.name
