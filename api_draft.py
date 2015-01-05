from __future__ import unicode_literals, absolute_import, division, print_function

from nosql_rest_preprocessor.models import BaseModel
from nosql_rest_preprocessor.exceptions import ValidationError


def js_string(key, value, request):
    if not isinstance(value, (str, unicode)):
        raise ValidationError()


def min_length(length):
    def check_min_length(key, value, request):
        if len(value) < length:
            raise ValidationError()

    return check_min_length


def required(key, value, request):
    if key not in request.DATA:
        raise ValidationError()


def js_list(key, value, request):
    if not isinstance(value, list):
        raise ValidationError()


def js_list_of(list_type):
    def check_list_type(key, value, request):
        js_list(key, value, request)

        if not all(isinstance(inner_value, list_type) for inner_value in value):
            raise ValidationError()

    return check_list_type


def valid_email(key, value):
    if '@' not in value:
        raise ValidationError()


def disallow_in(*http_method_names):
    def check_disallow(key, value, request):
        if key not in request.DATA or request.method in http_method_names:
            raise ValidationError()

    return check_disallow


class UserModel(BaseModel):
    default_policies = {
        'firstName': [js_string, required, min_length],
        'lastName': [js_string, required],
        'email': [js_string, required, valid_email],
        'password': [js_string, disallow_in('PUT')]
    }