from __future__ import absolute_import
from functools import wraps
from copy import deepcopy


def map_if_list(func, potential_list):

    if isinstance(potential_list, list):
        return map(func, potential_list)
    elif isinstance(potential_list, dict):
        return func(potential_list)


def non_mutating(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        copied_args = deepcopy(args)
        copied_kwargs = deepcopy(kwargs)

        return f(*copied_args, **copied_kwargs)

    return wrapper