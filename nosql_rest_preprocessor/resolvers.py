from __future__ import absolute_import, unicode_literals
from nosql_rest_preprocessor import exceptions
from inspect import isclass


class ResolveWith(object):

    def lookup(self, key):
        if self.lookup_class:
            if isclass(self.lookup_class):
                lookup_obj = self.lookup_class(**self.lookup_class_kwargs)
            else:
                lookup_obj = self.lookup_class

            return self.lookup_func(lookup_obj, key)  # uses the instantiated obj and its method to lookup by key
        else:
            return self.lookup_func(key)  # lookup directly

    def __init__(self, lookup_func, model=None, lookup_class=None, **lookup_class_kwargs):
        self.lookup_func = lookup_func
        self.model = model

        self.lookup_class = lookup_class
        self.lookup_class_kwargs = lookup_class_kwargs


def resolve(model, obj, depth=1, fail_fast=False):
    depth = min(depth, 3)  # don't resolve infinitely

    if depth <= 0:
        return obj

    new_obj = {}
    for attr, old_value in obj.items():
        if attr in model.resolved_attributes:

            attr_config = model.resolved_attributes[attr]  # config for attribute

            if isinstance(attr_config, ResolveWith):
                resolved_obj = attr_config.lookup(old_value)
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