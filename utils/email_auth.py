#!/usr/bin/env python
# coding=utf-8

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.core.validators import validate_email
from django.forms import forms


class EmailOrUsernameModelBackend(ModelBackend):
    """
    This is a ModelBacked that allows authentication with either a username or
    an email address.

    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            validate_email(username)
            kwargs = {'email': username}
        except forms.ValidationError:
            kwargs = {'username': username}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return None

    def get_user(self, username):
        try:
            return User.objects.get(pk=username)
        except User.DoesNotExist:
            return None
