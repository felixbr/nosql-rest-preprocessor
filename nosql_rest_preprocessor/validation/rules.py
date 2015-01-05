from __future__ import unicode_literals, absolute_import, division, print_function

from nosql_rest_preprocessor.exceptions import ValidationError
from nosql_rest_preprocessor.validation import rule_context
from nosql_rest_preprocessor.validation.contexts import *


@rule_context(VALIDATION)
def js_string(key, value, request):
    if not isinstance(value, (str, unicode)):
        raise ValidationError()


@rule_context(VALIDATION)
def min_length(length):
    def check_min_length(key, value, request):
        if len(value) < length:
            raise ValidationError()

    return check_min_length


def required(key, value, request):
    if key not in request.DATA:
        raise ValidationError()


@rule_context(VALIDATION)
def js_list(key, value, request):
    if not isinstance(value, list):
        raise ValidationError()


@rule_context(VALIDATION)
def js_list_of(list_type):
    def check_list_type(key, value, request):
        js_list(key, value, request)

        if not all(isinstance(inner_value, list_type) for inner_value in value):
            raise ValidationError()

    return check_list_type


@rule_context(VALIDATION)
def valid_email(key, value):
    if not '@' in value:
        raise ValidationError()


@rule_context(VALIDATION)
def disallow_in(*method_names):
    def check_disallow(key, value, request):
        if request and request.method in method_names:
            raise ValidationError()

    return check_disallow


@rule_context(MERGE_UPDATED)
def immutable(request):
    pass


@rule_context(PREPARE_RESPONSE)
def private(request):
    pass