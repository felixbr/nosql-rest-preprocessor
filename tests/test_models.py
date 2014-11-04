from __future__ import absolute_import, unicode_literals
from nosql_rest_preprocessor.models import BaseModel
from nosql_rest_preprocessor import exceptions
import pytest


class EmptyModel(BaseModel):
    pass


class ModelA(BaseModel):
    required_attributes = {'A'}

    immutable_attributes = {'A'}

    non_public_attributes = {'A'}


class ModelB(BaseModel):
    immutable_attributes = {'A'}


# noinspection PyMethodMayBeStatic
class TestValidate(object):

    def test_empty_obj(self):
        with pytest.raises(exceptions.ValidationError):
            ModelA.validate({})

    def test_objs(self):
        some_obj = {'A': 'Something'}
        assert ModelA.validate(some_obj) == some_obj

        some_obj['B'] = 'Something Else'
        assert ModelA.validate(some_obj) == some_obj

        del some_obj['A']
        with pytest.raises(exceptions.ValidationError):
            ModelA.validate(some_obj)


# noinspection PyMethodMayBeStatic
class TestPrepareResponse(object):

    def test_empty_obj(self):
        assert ModelA.prepare_response({}) == {}

    def test_objs(self):
        some_obj = {'A': 'Something'}
        assert ModelA.prepare_response(some_obj) == {}
        assert 'A' in some_obj


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

        with pytest.raises(exceptions.ChangingImmutableAttributeError):
            ModelA.merge_updated(db_obj, new_obj)

    def test_adding_attrs(self):
        db_obj = {'A': 'something'}
        new_obj = {'A': 'something', 'B': 'else'}

        merged_obj = ModelA.merge_updated(db_obj, new_obj)
        assert 'A' in merged_obj
        assert 'B' in merged_obj

        new_obj = {'B': 'else'}
        with pytest.raises(exceptions.ValidationError):
            ModelA.merge_updated({}, new_obj)

    def test_deleting_attrs(self):
        db_obj = {'A': 'something', 'B': 'else'}
        new_obj = {'A': 'something'}

        merged_obj = ModelA.merge_updated(db_obj, new_obj)
        assert merged_obj == new_obj

        new_obj = {'B': 'else'}  # deleting immutable attribute!
        with pytest.raises(exceptions.ChangingImmutableAttributeError):
            ModelB.merge_updated(db_obj, new_obj)



