from __future__ import absolute_import, unicode_literals
from nosql_rest_preprocessor.models import BaseModel
from nosql_rest_preprocessor import exceptions
from copy import deepcopy
from pytest import raises


class EmptyModel(BaseModel):
    pass


class ModelA(BaseModel):
    required_attributes = {'A'}
    immutable_attributes = {'A'}
    private_attributes = {'A'}


class ModelB(BaseModel):
    immutable_attributes = {'A'}


class AddressModel(BaseModel):
    required_attributes = {'street', 'city', 'plz'}
    private_attributes = {'wifiPassword'}
    immutable_attributes = {'planet'}


class PersonModel(BaseModel):
    required_attributes = {'name', 'email'}

    sub_models = {
        'address': AddressModel
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


