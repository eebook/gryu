#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from flask import request
from flask_wtf import FlaskForm as BaseForm
from werkzeug.datastructures import MultiDict


class Form(BaseForm):
    @classmethod
    def create_api_form(cls, obj=None):
        form_data = MultiDict(request.get_json())
        form = cls(formdata=form_data, obj=obj, csrf_enabled=False)
        form._obj = obj
        # if not form.validate():
        #     raise Exception    # TODO: can ben better handled
        return form

    def _validate_obj(self, key, value):
        obj = getattr(self, '_obj', None)
        return obj and getattr(obj, key) == value
