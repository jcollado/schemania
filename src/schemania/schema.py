"""Schemas.

Schemas are the description of a data structure using patterns. Those patterns
are compiled into validators that are used to check if some data matches the
expected structure later.

"""

import re
import types

from schemania.error import (
    ValidationExclusiveError,
    ValidationFunctionError,
    ValidationLengthError,
    ValidationLiteralError,
    ValidationMatchError,
    ValidationMissingKeyError,
    ValidationMultipleError,
    ValidationTypeError,
    ValidationUnknownKeyError,
)
from schemania.formatter import (
    default_exclusive_formatter,
    default_function_formatter,
    default_length_formatter,
    default_literal_formatter,
    default_match_formatter,
    default_missing_key_formatter,
    default_multiple_formatter,
    default_type_formatter,
    default_unknown_key_formatter,
)
from schemania.validator import (
    AllValidator,
    AnyValidator,
    DictValidator,
    FunctionValidator,
    LengthValidator,
    ListValidator,
    LiteralValidator,
    RegexValidator,
    SelfValidator,
    TypeValidator,
)


DEFAULT_FORMATTERS = {
    ValidationExclusiveError: default_exclusive_formatter,
    ValidationFunctionError: default_function_formatter,
    ValidationLengthError: default_length_formatter,
    ValidationLiteralError: default_literal_formatter,
    ValidationMatchError: default_match_formatter,
    ValidationMissingKeyError: default_missing_key_formatter,
    ValidationMultipleError: default_multiple_formatter,
    ValidationTypeError: default_type_formatter,
    ValidationUnknownKeyError: default_unknown_key_formatter,
}

# Get _sre.SRE_Pattern to use it below with isinstance function
RegexObject = type(re.compile(''))


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
        if isinstance(raw_schema, (str, int)):
            return LiteralValidator(self, raw_schema)

        if raw_schema in (str, int):
            return TypeValidator(self, raw_schema)

        if isinstance(raw_schema, list):
            assert len(raw_schema) == 1
            element_validator = self._compile(raw_schema[0])
            return ListValidator(self, element_validator)

        if isinstance(raw_schema, dict):
            values_validator = {
                self._compile(key): self._compile(value)
                for key, value in raw_schema.items()
            }
            return DictValidator(self, values_validator)

        if isinstance(raw_schema, RegexObject):
            return RegexValidator(self, raw_schema)

        if isinstance(raw_schema, types.FunctionType):
            return FunctionValidator(self, raw_schema)

        if isinstance(raw_schema, Length):
            return LengthValidator(
                self, raw_schema.min_length, raw_schema.max_length)

        if isinstance(raw_schema, Optional):
            validator = self._compile(raw_schema.raw_schema)
            validator.attributes['optional'] = True
            return validator

        if isinstance(raw_schema, Exclusive):
            validator = self._compile(raw_schema.raw_schema)
            validator.attributes['exclusion_group'] = (
                raw_schema.exclusion_group
            )
            return validator

        if isinstance(raw_schema, All):
            validators = [
                self._compile(sub_schema)
                for sub_schema in raw_schema.raw_schemas
            ]
            return AllValidator(self, validators)

        if isinstance(raw_schema, Any):
            validators = [
                self._compile(sub_schema)
                for sub_schema in raw_schema.raw_schemas
            ]
            return AnyValidator(self, validators)

        if raw_schema is Self:
            return SelfValidator(self)

        raise ValueError('Unexpected raw schema: {}'.format(raw_schema))

    def __call__(self, data):
        """Validate data structure.

        :param data: Data structure to validate.
        :type data: object
        :raises: schemania.error.ValidationError if some problem is found

        """
        return self.validator.validate(data)


class Optional(object):
    """Optional marker for validators.

    The use case for this marker is to use it around keys in dictionaries in
    raw schemas, so that they are not required on validation.

    """
    def __init__(self, raw_schema):
        self.raw_schema = raw_schema


class Exclusive(object):
    """Exclusive marker for validators.

    The use case for this marker is to use it around keys in dictionaries in
    raw schemas, so that exactly one key is required for each exclusion group.

    """
    def __init__(self, raw_schema, exclusion_group):
        self.raw_schema = raw_schema
        self.exclusion_group = exclusion_group


class Self(object):
    """Recursive schema.

    This class is used to mark the location at which the schema validates
    recursively. This is useful for data structures such as linked lists and
    trees.

    """


class All(object):
    """All schema.

    The use case for this wrapper is to use multiple schemas instead of just
    one.

    The validation passes if all validators pass.

    """
    def __init__(self, *raw_schemas):
        self.raw_schemas = raw_schemas


class Any(object):
    """Any schema.

    The use case for this wrapper is to use multiple schemas instead of just
    one.

    The validation passes if any validator passes.

    """
    def __init__(self, *raw_schemas):
        self.raw_schemas = raw_schemas


class Length(object):
    """Length schema.

    The use case for this is to use the `len` built-in to check the length of a
    string or a collection.

    """

    def __init__(self, min_length=None, max_length=None):
        self.min_length = min_length
        self.max_length = max_length
