from __future__ import absolute_import, unicode_literals
from collections import namedtuple
from nosql_rest_preprocessor import exceptions


class ResolveWith(object):

    def __init__(self, lookup_func, lookup_class=None, model=None):
        self.lookup_class = lookup_class
        self.lookup_func = lookup_func
        self.model = model


def resolve(model, obj, depth=1, fail_fast=False):
    depth = min(depth, 3)  # don't resolve infinitely

    if depth <= 0:
        return obj

    new_obj = {}
    for attr, old_value in obj.items():
        if attr in model.resolved_attributes:

            attr_config = model.resolved_attributes[attr]  # config for attribute

            if isinstance(attr_config, ResolveWith):
                if attr_config.lookup_class is not None:
                    lookup_obj = attr_config.lookup_class()
                    resolved_obj = getattr(lookup_obj, attr_config.lookup_func.__name__)(old_value)
                else:
                    resolved_obj = attr_config.lookup_func(old_value)

            else:
                resolved_obj = attr_config(old_value)  # in case a function was passed directly

            if not resolved_obj:
                if fail_fast:
                    raise exceptions.ResolvedObjectNotFound(message='Could not find object with id %s for attribute %s' % (old_value, attr))
                else:
                    new_obj[attr] = old_value
                    continue  # leave id unresolved and go on

            resolving_model = attr_config.model or model.sub_models[attr]
            # remove private attributes
            resolved_obj = resolving_model.prepare_response(resolved_obj)

            # resolveception
            resolved_obj = resolve(resolving_model, resolved_obj, depth - 1)

            # save resolved attribute
            new_obj[attr] = resolved_obj
        else:
            new_obj[attr] = old_value

    return new_obj