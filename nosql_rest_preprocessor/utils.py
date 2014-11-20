from __future__ import absolute_import, unicode_literals, print_function, division

from functools import wraps
from copy import deepcopy


def map_if_list(func, potential_list):

    if isinstance(potential_list, list):
        return list(map(func, potential_list))  # list() is needed in Python3.x as it returns an iterator
    elif isinstance(potential_list, dict):
        return func(potential_list)


def non_mutating(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        copied_args = deepcopy(args)
        copied_kwargs = deepcopy(kwargs)

        return f(*copied_args, **copied_kwargs)

    return wrapper


def all_of(*attributes):
    return 'all_of', attributes


def one_of(*attributes):
    return 'one_of', attributes


def either_of(*attributes):
    return 'either_of', attributes