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


class ValidationLiteralError(ValidationError):
    """Literal error.

    This happens when data is not equal to the expected literal value.

    """

    def __init__(self, validator, data):
        self.validator = validator
        self.data = data
        self.path = deque()


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


class ValidationUnknownKeyError(ValidationError):
    """Unknown key error.

    This happens when key in a dictionary doesn't match against any validator.

    :param validator: Validator that found the type error
    :type validator: schemania.validator.Validator
    :param data: Data that failed to validate
    :type data: object

    """

    def __init__(self, validator, key):
        self.validator = validator
        self.key = key
        self.path = deque()


class ValidationMissingKeyError(ValidationError):
    """Missing key error.

    This happens when key validator hasn't matched against any key in a
    dictionary.

    :param validator: Validator that found the type error
    :type validator: schemania.validator.Validator
    :param data: Data that failed to validate
    :type data: object

    """

    def __init__(self, validator, key_validator):
        self.validator = validator
        self.key_validator = key_validator
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


class ValidationMatchError(ValidationError):
    """Match error.

    This happens when a regular expression doesn't match with data.

    :param validator: Validator that found the type error
    :type validator: schemania.validator.Validator
    :param data: Data that failed to validate
    :type data: object

    """
    def __init__(self, validator, data):
        self.validator = validator
        self.data = data
        self.path = deque()


class ValidationFunctionError(ValidationError):
    """Function error.

    This happens when a function used as validator in the schema fails with an
    exception.

    """
    def __init__(self, validator, exception, data):
        self.validator = validator
        self.exception = exception
        self.data = data
        self.path = deque()
