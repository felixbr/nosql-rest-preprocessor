from __future__ import unicode_literals


class ValidationError(Exception):
    pass


class ChangingImmutableAttributeError(Exception):
    pass


class ResolvedObjectNotFound(Exception):
    def __init__(self, message=''):
        self.message = message.capitalize() or 'Could not find object to resolve to'