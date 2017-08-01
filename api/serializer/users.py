#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import hashlib

from wtforms.fields import (StringField, PasswordField, TextAreaField, IntegerField)
from wtforms.validators import (DataRequired, Optional, Email, URL, Length, Regexp, StopValidation)
from werkzeug.datastructures import MultiDict
# TODO, serializer can return errors like django-rest-framework
from api.models.models import User
from .base import Form
from ..models import db


class UserForm(Form):
    username = StringField(validators=[
        DataRequired(),
        Length(min=3, max=20),
        Regexp(r'^[a-z0-9]+$'),
    ])
    password = PasswordField(validators=[DataRequired()])


class PasswordForm(Form):
    password = PasswordField(validators=[DataRequired()])


class LoginForm(PasswordForm):
    # TODO: more clearly?
    username = StringField('Username or Email', validators=[DataRequired()])

    def validate_password(self, field):
        username = self.username.data
        if '@' in username:
            pass
        else:
            pass

        if not user or not user.check_password(field.data):
            raise StopValidation('Invalid account or password')

        self.user = user


class EmailForm(Form):
    email = StringField(validators=[DataRequired])


class RegisterForm(UserForm, EmailForm):
    def validate_username(self, field):
        # TODO: raise StopValidation if user already exist
        pass

    def create_user(self):
        print("create_user, WTF???")
        user = User(
            username=self.username.data,
            email=self.email.data
        )
        user.password = self.password.data
        with db.auto_commit():
            db.session.add(user)
        return user
