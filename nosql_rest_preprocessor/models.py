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
        cls._check_required_attributes(obj)

        cls._check_allowed_attributes(obj)

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

    @classmethod
    def _check_required_attributes(cls, obj):
        for attr in cls.required_attributes:
            if isinstance(attr, tuple):
                set_wanted = set(attr[1])
                set_contained = set(obj.keys())

                if attr[0] == 'one_of':
                    if len(set_wanted & set_contained) < 1:
                        raise exceptions.ValidationError()

                elif attr[0] == 'either_of':
                    if len(set_wanted & set_contained) != 1:
                        raise exceptions.ValidationError()

                else:
                    raise exceptions.ConfigurationError()

            else:
                if attr not in obj.keys():
                    raise exceptions.ValidationError()

    @classmethod
    def _check_allowed_attributes(cls, obj):
        if cls.optional_attributes is not None:
            required = cls._required_attributes()

            for attr in obj.keys():
                if attr in required:
                    continue

                allowed = False
                for opt_attr in cls.optional_attributes:
                    if attr == opt_attr:
                        allowed = True
                        break

                    elif isinstance(opt_attr, tuple):

                        if opt_attr[0] == 'all_of':
                            if attr in opt_attr[1]:  # if one of these is in obj.keys()...
                                if not set(opt_attr[1]).issubset(obj.keys()):  # ...all of them have to be there
                                    raise exceptions.ValidationError()
                                else:
                                    allowed = True
                                    break

                        elif opt_attr[0] == 'either_of':
                            if attr in opt_attr[1]:  # if one of these is in obj.keys()...
                                if next((key for key in opt_attr[1] if key != attr and key in obj.keys()), None):  # ...no other key may be present in obj.keys()
                                    raise exceptions.ValidationError()
                                else:
                                    allowed = True
                                    break

                        else:
                            raise exceptions.ConfigurationError()

                if not allowed:  # if we haven't found attr anywhere in cls.optional_attributes
                    raise exceptions.ValidationError()

    @classmethod
    def _required_attributes(cls):
        required = set()
        for attr in cls.required_attributes:
            if isinstance(attr, tuple):
                required = required | set(attr[1])
            else:
                required.add(attr)

        return required