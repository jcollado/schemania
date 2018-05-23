"""Validation errors.

Error classes are used by validators to signal when a problem is found. The
text description of the error they represent can be customized using
formatters.

"""
from collections import deque


class ValidationError(Exception):
    """Validation error that uses custom error formatter from schema.

    :param validator: The validator that created this error
    :type validator: schemania.validator.Validator
    :param data: The data that failed to validate
    :type data: object

    """

    def __init__(self, validator, data):
        self.validator = validator
        self.data = data
        self.path = deque()

    def __str__(self):
        formatter = self.validator.schema.formatters[self.__class__]
        return formatter(self)


class ValidationLiteralError(ValidationError):
    """Literal error.

    This happens when data is not equal to the expected literal value.

    """


class ValidationTypeError(ValidationError):
    """Type error.

    This happens when data doesn't match the expected type.

    """


class ValidationUnknownKeyError(ValidationError):
    """Unknown key error.

    This happens when key in a dictionary doesn't match against any validator.

    :param validator: Validator that found the type error
    :type validator: schemania.validator.Validator
    :param key: Unknown key
    :type key: object

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
    :param key_validator: Validator for the key that is missing
    :type key_validator: schemania.validator.Validator

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
    :param data: Data that failed to validate
    :type data: object
    :param errors: Errors that were found in the data structure
    :type errors: schemania.error.ValidationError

    """

    def __init__(self, validator, data, errors):
        super(ValidationMultipleError, self).__init__(validator, data)
        self.errors = errors


class ValidationMatchError(ValidationError):
    """Match error.

    This happens when a regular expression doesn't match with data.

    """


class ValidationFunctionError(ValidationError):
    """Function error.

    This happens when a function used as validator in the schema fails with an
    exception.

    :param validator: The validator that created this error
    :type validator: schemania.validator.Validator
    :param data: The data that failed to validate
    :type data: object
    :param exception: Exception raised during function execution
    :type exception: Exception

    """
    def __init__(self, validator, data, exception):
        super(ValidationFunctionError, self).__init__(validator, data)
        self.exception = exception


class ValidationLengthError(ValidationError):
    """Length error.

    This happens when data length is not within the expected range.

    """


class ValidationExclusiveError(ValidationError):
    """Exclusive error.

    This happens when more than one key in the a dictionary within the same
    exclusive group have matched.

    :param validator: The validator that created this error
    :type validator: schemania.validator.Validator
    :param exclusion_group: Exclusion group metadata
    :type exclusion_group: Dict[str, object]

    """
    def __init__(self, validator, exclusion_group):
        self.validator = validator
        self.exclusion_group = exclusion_group
        self.path = deque()
