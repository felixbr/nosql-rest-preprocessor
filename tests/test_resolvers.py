from __future__ import absolute_import, unicode_literals, division, print_function

from nosql_rest_preprocessor.resolvers import resolve, ResolveWith
from nosql_rest_preprocessor.models import BaseModel
from nosql_rest_preprocessor import exceptions
from pytest import raises
import pytest


def find_address_by_key(key):
    db_mock = {
        'foreign_key_123': address_obj1,
        'foreign_key_456': address_obj2,
        'foreign_key_890': company_obj
    }
    return db_mock.get(key, {})


class MockDao(object):

    @staticmethod
    def find_address_by_key(key):
        return find_address_by_key(key)  # just delegate


class MockDBConnection(object):

    # noinspection PyMethodMayBeStatic
    def get(self, key):
        return find_address_by_key(key)  # just delegate


class MockDaoWithConnection(object):

    def __init__(self, connection):
        self.connection = connection

    def find_address_by_key(self, key):
        return self.connection.get(key)


class AddressModel(BaseModel):
    required_attributes = {'street', 'city', 'plz'}
    private_attributes = {'openWifi'}


class CompanyModel(BaseModel):
    required_attributes = {'address'}

    resolved_attributes = {
        'address': ResolveWith(find_address_by_key, model=AddressModel)
    }


class PersonModel1(BaseModel):
    required_attributes = {'name', 'email'}

    resolved_attributes = {
        'address': ResolveWith(find_address_by_key, model=AddressModel),
        'company': ResolveWith(MockDao.find_address_by_key, model=CompanyModel)
    }


class PersonModel2(BaseModel):
    required_attributes = {'name', 'email'}

    resolved_attributes = {
        'address': ResolveWith(lookup_func=MockDao.find_address_by_key, model=AddressModel),
        'company': ResolveWith(find_address_by_key)  # should use sub_model to find model as fallback
    }

    sub_models = {
        'company': CompanyModel
    }


class PersonModel3(BaseModel):
    connection = MockDBConnection()

    resolved_attributes = {
        'address': ResolveWith(MockDaoWithConnection.find_address_by_key, model=AddressModel,
                               lookup_class=MockDaoWithConnection, **{'connection': connection})
    }


class PersonModel4(BaseModel):
    dao = MockDaoWithConnection(MockDBConnection())

    resolved_attributes = {
        'address': ResolveWith(MockDaoWithConnection.find_address_by_key, model=AddressModel,
                               lookup_class=dao)
    }


person_obj = {
    'name': 'Sepp Huber',
    'email': 'sepp.huber@fancypants.com',
    'address': 'foreign_key_123',
    'company': 'foreign_key_890'
}

address_obj1 = {
    'street': 'Bakerstreet',
    'city': 'London',
    'plz': '12345'
}

address_obj2 = {
    'street': 'Brook St',
    'city': 'London',
    'plz': '98765'
}

company_obj = {
    'name': 'Continental',
    'address': 'foreign_key_456'
}


# noinspection PyMethodMayBeStatic
class TestResolve(object):

    def test_key_is_resolved(self):
        resolved_obj = resolve(PersonModel1, person_obj, depth=1)  # only depth=1
        assert resolved_obj['company']['address'] == company_obj['address']
        assert resolved_obj['company'] == company_obj

        resolved_obj = resolve(PersonModel1, person_obj, depth=2)
        assert resolved_obj['address'] == address_obj1
        assert resolved_obj['company']['address'] == address_obj2

        resolved_obj = resolve(PersonModel2, person_obj, depth=2)  # sub_models fallback
        assert resolved_obj['address'] == address_obj1
        assert resolved_obj['company']['address'] == address_obj2

    def test_response_is_prepared_when_resolving(self):
        address_obj1['openWifi'] = 'nopassword'
        address_obj2['openWifi'] = 'WEP-something'

        resolved_obj = resolve(PersonModel1, person_obj, depth=2)
        assert 'openWifi' not in resolved_obj['address']
        assert 'openWifi' not in resolved_obj['company']['address']

        # clean up
        del address_obj1['openWifi']
        del address_obj2['openWifi']

    @pytest.mark.randomize(person={
        'name': str, 'email': str, 'company': str
    })
    def test_failing_fast(self, person):
        resolved_obj = resolve(PersonModel1, person)
        assert resolved_obj['company'] == person['company']

        with raises(exceptions.ResolvedObjectNotFound):
            resolve(PersonModel1, person, fail_fast=True)

    def test_resolved_attributes_are_not_saved_on_update(self):
        resolved_obj = resolve(PersonModel1, person_obj, depth=2)

        merged_obj = PersonModel1.merge_updated(person_obj, resolved_obj)

        assert merged_obj['company'] == person_obj['company']
        assert merged_obj['address'] == person_obj['address']

    def test_lookup_class(self):
        resolved_obj = resolve(PersonModel3, person_obj)  # use a lookup_class
        assert resolved_obj['address'] == address_obj1

        resolved_obj = resolve(PersonModel4, person_obj)  # use an object of a class
        assert resolved_obj['address'] == address_obj1
