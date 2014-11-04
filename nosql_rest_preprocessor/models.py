from __future__ import absolute_import
from nosql_rest_preprocessor import exceptions
from nosql_rest_preprocessor.utils import non_mutating


class BaseModel(object):
    required_attributes = []

    immutable_attributes = []

    non_public_attributes = []

    @classmethod
    def validate(cls, obj):
        # check required attrs
        for attr in cls.required_attributes:
            if attr not in obj.keys():
                raise exceptions.ValidationError()

        return obj

    @classmethod
    @non_mutating
    def prepare_response(cls, obj):
        # remove non-public attrs
        for attr in cls.non_public_attributes:
            obj.pop(attr, None)

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

            merged_obj[key] = value

        return merged_obj

    @classmethod
    def _check_immutable_attrs_on_update(cls, key, value, db_obj):
        # check if immutable attributes should be changed
        if key in cls.immutable_attributes:
            if db_obj[key] != value:
                raise exceptions.ChangingImmutableAttributeError()