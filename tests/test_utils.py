from __future__ import absolute_import, unicode_literals
from nosql_rest_preprocessor.utils import *


class TestMapIfList(object):

    @staticmethod
    def upper_case_values(obj):  # pure function on a dict
        obj_copy = obj.copy()
        for key in obj_copy.keys():
            obj_copy[key] = obj_copy[key].upper()
        return obj_copy

    def test_single_obj(self):
        a = {'A': 'something'}
        b = map_if_list(self.upper_case_values, a)

        assert b['A'] == 'SOMETHING'
        assert a['A'] == 'something'
        assert a is not b

    def test_list_with_objs(self):
        a = [
            {'A': 'something'},
            {'B': 'else'}
        ]
        b = map_if_list(self.upper_case_values, a)

        assert b[0]['A'] == 'SOMETHING'
        assert b[1]['B'] == 'ELSE'
        assert a[0]['A'] == 'something'
        assert a[1]['B'] == 'else'


class TestNonMutating(object):

    @non_mutating
    def upper_case_values(self, obj):  # mutating function on a dict
        for key in obj.keys():
            obj[key] = obj[key].upper()

        return obj

    def test_decorator(self):
        a = {'A': 'something'}
        b = self.upper_case_values(a)

        assert a is not b
        assert a['A'] == 'something'
        assert b['A'] == 'SOMETHING'


# noinspection PyMethodMayBeStatic
class TestTuples(object):

    def test_all_of(self):
        assert all_of('phoneCarrier', 'phoneModel') == ('all_of', ('phoneCarrier', 'phoneModel'))

    def test_one_of(self):
        assert one_of('backgroundImg', 'backgroundUrl') == ('one_of', ('backgroundImg', 'backgroundUrl'))

    def test_either_of(self):
        assert either_of('sweets', 'bacon') == ('either_of', ('sweets', 'bacon'))