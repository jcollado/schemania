"""Schemas.

Schemas are the description of a data structure using patterns. Those patterns
are compiled into validators that are used to check if some data matches the
expected structure later.

"""
from schemania.error import (
    ValidationMultipleError,
    ValidationTypeError,
)
from schemania.formatter import (
    default_multiple_formatter,
    default_type_formatter,
)
from schemania.validator import (
    DictValidator,
    ListValidator,
    TypeValidator,
)


DEFAULT_FORMATTERS = {
    ValidationTypeError: default_type_formatter,
    ValidationMultipleError: default_multiple_formatter,
}


class Schema(object):
    """Schema object to validate data structures.

    :param schema: Raw schema
    :param schema: object
    :param formatters: Error message formatters
    :type formatters: Dict[ValidationError, callable]

    """

    def __init__(self, raw_schema, formatters=DEFAULT_FORMATTERS):
        self.validator = self._compile(raw_schema)
        self.formatters = formatters

    def _compile(self, raw_schema):
        """Compile raw schema into validators.

        :param raw_schema: Raw schema
        :param raw_schema: object
        :returns: Validator that validates data structures
        :rtype: schemania.validator.Validator

        """
        if raw_schema in (str, int):
            return TypeValidator(self, raw_schema)

        if isinstance(raw_schema, list):
            assert len(raw_schema) == 1
            element_validator = self._compile(raw_schema[0])
            return ListValidator(self, element_validator)

        if isinstance(raw_schema, dict):
            values_validator = {
                key: self._compile(value)
                for key, value in raw_schema.items()
            }
            return DictValidator(self, values_validator)

        raise ValueError('Unexpected raw schema: {}'.format(raw_schema))

    def __call__(self, data):
        """Validate data structure.

        :param data: Data structure to validate.
        :type data: object
        :raises: schemania.error.ValidationError if some problem is found

        """
        self.validator.validate(data)
