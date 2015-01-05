from __future__ import absolute_import, unicode_literals
from nosql_rest_preprocessor.models import BaseModel
from nosql_rest_preprocessor.utils import *
from nosql_rest_preprocessor import exceptions
from nosql_rest_preprocessor.validation.rules import *
from copy import deepcopy
from pytest import raises


class EmptyModel(BaseModel):
    pass


class ModelA(BaseModel):
    attribute_policies = {
        'A': [required, immutable, private]
    }


class ModelB(BaseModel):
    attribute_policies = {
        'A': [immutable]
    }


class ModelC(BaseModel):
    required_attributes = {
        one_of('A', 'B'),
        either_of('C', 'D')
    }

    optional_attributes = {
        all_of('E', 'F'),
        either_of('G', 'H')
    }


class AddressModel(BaseModel):
    attribute_policies = {
        'street': [required],
        'city': [required],
        'plz': [required],
        'wifiPassword': [private],
        'planet': [immutable]
    }


class PersonModel(BaseModel):
    attribute_policies = {
        'name': [required],
        'email': [required, valid_email],
        'address': []
    }

    sub_models = {
        'address': AddressModel
    }


class CompanyModel(BaseModel):
    required_attributes = {'name'}
    optional_attributes = {'address'}

    attribute_policies = {
        'name': [required],
        'address': []
    }


# noinspection PyMethodMayBeStatic
class TestValidate(object):

    def test_empty_obj(self):
        with raises(exceptions.ValidationError):
            ModelA.validate({})

    def test_objs(self):
        some_obj = {'A': 'Something'}
        assert ModelA.validate(some_obj) == some_obj

        some_obj['B'] = 'Something Else'
        assert ModelA.validate(some_obj) == some_obj

        del some_obj['A']
        with raises(exceptions.ValidationError):
            ModelA.validate(some_obj)

    def test_nested_parsing(self):
        person_obj = {
            'name': 'Sepp Huber',
            'email': 'sepp.huber@fancypants.com',
            'address': {
                'street': 'Bakerstreet',
                'city': 'London'
            }
        }
        with raises(exceptions.ValidationError):
            PersonModel.validate(person_obj)

    def test_whitelisting(self):
        company_obj = {
            'name': 'Continental',
            'address': 'foreign_key_123'
        }
        CompanyModel.validate(company_obj)

        company_obj['city'] = 'Ratisbon'
        with raises(exceptions.ValidationError):
            CompanyModel.validate(company_obj)

    def test_one_of(self):
        some_obj = {
            'C': 'more'
        }
        with raises(exceptions.ValidationError):  # one_of('A', 'B')
            ModelC.validate(some_obj)

        some_obj['A'] = 'something'  # one_of('A', 'B')
        ModelC.validate(some_obj)

        some_obj['B'] = 'something else'  # one_of('A', 'B')
        ModelC.validate(some_obj)         # still fine

        some_obj['D'] = 'even more'  # either_of('C', 'D'), now we have both!
        with raises(exceptions.ValidationError):
            ModelC.validate(some_obj)
        del some_obj['D']

        some_obj['E'] = 'one of two'  # all_of('E', 'F')
        with raises(exceptions.ValidationError):
            ModelC.validate(some_obj)

        some_obj['F'] = 'two of two'  # all_of('E', 'F')
        ModelC.validate(some_obj)

        some_obj['G'] = 'one of either'  # either_of('G', 'H')
        ModelC.validate(some_obj)

        some_obj['H'] = 'two of either'  # either_of('G', 'H')
        with raises(exceptions.ValidationError):
            ModelC.validate(some_obj)

        del some_obj['G']  # either_of('G', 'H'), works again
        ModelC.validate(some_obj)

    def test_config_error(self):
        class ErrorModel(BaseModel):
            required_attributes = {
                ('many_of', ('apple', 'pie'))
            }
        with raises(exceptions.ConfigurationError):
            ErrorModel.validate({})

        class ErrorModel2(BaseModel):
            optional_attributes = {
                ('many_of', ('apple', 'pie'))
            }
        with raises(exceptions.ConfigurationError):
            ErrorModel2.validate({'apple': 'red'})


# noinspection PyMethodMayBeStatic
class TestPrepareResponse(object):

    def test_empty_obj(self):
        assert ModelA.prepare_response({}) == {}

    def test_objs(self):
        some_obj = {'A': 'Something'}
        assert ModelA.prepare_response(some_obj) == {}
        assert 'A' in some_obj

    def test_nested_responses(self):
        person_obj = {
            'name': 'Sepp Huber',
            'email': 'sepp.huber@fancypants.com',
            'address': {
                'street': 'Bakerstreet',
                'city': 'London',
                'plz': '12345',
                'wifiPassword': 'thecakeisalie'
            }
        }
        assert 'wifiPassword' not in PersonModel.prepare_response(person_obj)['address']


# noinspection PyMethodMayBeStatic
class TestMergeUpdated(object):

    def test_empty_objs(self):
        db_obj, new_obj = {}, {}

        assert EmptyModel.merge_updated(db_obj, new_obj) == {}
        assert EmptyModel.merge_updated(db_obj, new_obj) is not db_obj
        assert EmptyModel.merge_updated(db_obj, new_obj) is not new_obj

    def test_immutability(self):
        db_obj = {'A': 'something'}
        new_obj = {'A': 'SOMETHING'}

        with raises(exceptions.ChangingImmutableAttributeError):
            ModelA.merge_updated(db_obj, new_obj)

    def test_adding_attrs(self):
        db_obj = {'A': 'something'}
        new_obj = {'A': 'something', 'B': 'else'}

        merged_obj = ModelA.merge_updated(db_obj, new_obj)
        assert 'A' in merged_obj
        assert 'B' in merged_obj

        new_obj = {'B': 'else'}
        with raises(exceptions.ValidationError):
            ModelA.merge_updated({}, new_obj)

    def test_deleting_attrs(self):
        db_obj = {'A': 'something', 'B': 'else'}
        new_obj = {'A': 'something'}

        merged_obj = ModelA.merge_updated(db_obj, new_obj)
        assert merged_obj == new_obj

        new_obj = {'B': 'else'}  # deleting immutable attribute!
        with raises(exceptions.ChangingImmutableAttributeError):
            ModelB.merge_updated(db_obj, new_obj)

    def test_nested_immutability(self):
        person_obj = {
            'name': 'Sepp Huber',
            'email': 'sepp.huber@fancypants.com',
            'address': {
                'street': 'Bakerstreet',
                'city': 'London',
                'plz': '12345',
                'planet': 'Earth'
            }
        }
        new_obj = deepcopy(person_obj)
        assert person_obj is not new_obj
        new_obj['address']['planet'] = 'Mars'

        assert person_obj != new_obj
        with raises(exceptions.ChangingImmutableAttributeError):
            PersonModel.merge_updated(person_obj, new_obj)

        new_obj['address'].pop('planet', None)

        assert person_obj != new_obj
        with raises(exceptions.ChangingImmutableAttributeError):
            PersonModel.merge_updated(person_obj, new_obj)