"""Validation errors.

Error classes are used by validators to signal when a problem is found. The
text description of the error they represent can be customized using
formatters.

"""
from collections import deque


class ValidationError(Exception):
    """Validation error that uses custom error formatter from schema."""

    def __str__(self):
        formatter = self.validator.schema.formatters[self.__class__]
        return formatter(self)


class ValidationTypeError(ValidationError):
    """Type error.

    This happens when data doesn't match the expected type.

    :param validator: Validator that found the type error
    :type validator: schemania.validator.Validator
    :param data: Data that failed to validate
    :type data: object

    """

    def __init__(self, validator, data):
        self.validator = validator
        self.data = data
        self.path = deque()


class ValidationMultipleError(ValidationError):
    """Multiple error.

    This is a container when multiple errors are detected for the same data
    structure.

    :param validator: Validator that found the type error
    :type validator: schemania.validator.Validator
    :param errors: Errors that were found in the data structure
    :type errors: schemania.error.ValidationError
    :param data: Data that failed to validate
    :type data: object

    """

    def __init__(self, validator, errors, data):
        self.validator = validator
        self.errors = errors
        self.data = data
        self.path = deque()
