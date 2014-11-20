from __future__ import absolute_import, unicode_literals, print_function, division

from nosql_rest_preprocessor import exceptions
from nosql_rest_preprocessor.utils import non_mutating


class BaseModel(object):
    required_attributes = set()

    optional_attributes = None

    immutable_attributes = set()

    private_attributes = set()

    sub_models = {}

    resolved_attributes = {}

    @classmethod
    def validate(cls, obj):
        # check required attrs
        for attr in cls.required_attributes:
            if attr not in obj.keys():
                raise exceptions.ValidationError()

        # check allowed attributes
        if cls.optional_attributes is not None:
            whitelist = set(cls.required_attributes).union(cls.optional_attributes)
            for attr in obj.keys():
                if attr not in whitelist:
                    raise exceptions.ValidationError()

        # recurse for sub models
        for attr, sub_model in cls.sub_models.items():
            if attr in obj.keys():
                sub_model.validate(obj[attr])

        return obj

    @classmethod
    @non_mutating
    def prepare_response(cls, obj):
        # remove non-public attrs
        for attr in cls.private_attributes:
            obj.pop(attr, None)

        # recurse for sub models
        for attr, sub_model in cls.sub_models.items():
            if attr in obj.keys():
                obj[attr] = sub_model.prepare_response(obj[attr])

        return obj

    @classmethod
    def merge_updated(cls, db_obj, new_obj):
        cls.validate(new_obj)

        merged_obj = {}

        # check if previously present immutable attributes should be deleted
        for key in cls.immutable_attributes:
            if key in db_obj and key not in new_obj:
                raise exceptions.ChangingImmutableAttributeError()

        # copy attributes into merged_obj
        for key, value in new_obj.items():
            cls._check_immutable_attrs_on_update(key, value, db_obj)

            if key in cls.resolved_attributes and isinstance(value, dict):  # ignore resolved attributes in update
                merged_obj[key] = db_obj[key]
            else:
                merged_obj[key] = value

        # recurse for sub models
        for attr, sub_model in cls.sub_models.items():
            merged_obj[attr] = sub_model.merge_updated(db_obj[attr], new_obj[attr])

        return merged_obj

    @classmethod
    def _check_immutable_attrs_on_update(cls, key, value, db_obj):
        # check if immutable attributes should be changed
        if key in cls.immutable_attributes:
            if db_obj[key] != value:
                raise exceptions.ChangingImmutableAttributeError()