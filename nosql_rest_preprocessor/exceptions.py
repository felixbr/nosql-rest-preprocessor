from __future__ import unicode_literals


class ValidationError(Exception):
    pass


class ChangingImmutableAttributeError(Exception):
    pass