"""Schema validators.

Validators are the objects that are used to check if a given data matches the
expected structure.

"""
from schemania.error import (
    ValidationError,
    ValidationLiteralError,
    ValidationMatchError,
    ValidationMissingKeyError,
    ValidationMultipleError,
    ValidationTypeError,
    ValidationUnknownKeyError,
)


class Validator(object):
    """Validator base class."""


class LiteralValidator(Validator):
    """Validator that checks that data is equal to a given literal value.

    :param schema: Schema that created this validator
    :type schema: schemania.schema.Schema
    :param literal: Literal value that data should be equal to
    :type literal: object

    """
    def __init__(self, schema, literal):
        self.schema = schema
        self.literal = literal

    def __str__(self):
        """Return validator string representation.

        This is useful for some formatters that need to get access to the
        original value passed in the raw schema.

        """
        return repr(self.literal)

    def validate(self, data):
        """Check if data is equal to literal value.

        :param data: Data to validate
        :type data: object

        """
        if not data == self.literal:
            raise ValidationLiteralError(self, data)


class TypeValidator(Validator):
    """Validator that checks data by its type.

    :param schema: Schema that created this validator
    :type schema: schemania.schema.Schema
    :param type_: Type that data should be an instance of
    :param type_: type

    """
    def __init__(self, schema, type_):
        self.schema = schema
        self.type = type_

    def __str__(self):
        """Return validator string representation.

        This is useful for some formatters that need to get access to the
        original value passed in the raw schema.

        """
        return repr(self.type.__name__)

    def validate(self, data):
        """Check if data is of the expected type.

        :param data: Data to validate
        :type data: object

        """
        if not isinstance(data, self.type):
            raise ValidationTypeError(self, data)


class ListValidator(Validator):
    """Validator that checks elements in a list.

    :param schema: Schema that created this validator
    :type schema: schemania.schema.Schema
    :param element_validator: Validator used to check every list element
    :type element_validator: schemania.validator.Validator

    """

    def __init__(self, schema, element_validator):
        self.schema = schema
        self.type = list
        self.element_validator = element_validator

    def validate(self, data):
        """Check if each element in data validates against element validator.

        :param data: Data to validate
        :type data: object

        """
        if not isinstance(data, list):
            raise ValidationTypeError(self, data)

        errors = []
        for index, element in enumerate(data):
            try:
                self.element_validator.validate(element)
            except ValidationError as error:
                error.path.appendleft(index)
                errors.append(error)

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise ValidationMultipleError(self, errors, data)


class DictValidator(Validator):
    """Validator that checks key-value pairs in a dictionary.

    :param schema: Schema that created this validator
    :type schema: schemania.schema.Schema
    :param validators: Dictionary of key-value validators
    :type validators:
        Dict[schemania.validator.Validator, schemania.validator.Validator]

    """
    def __init__(self, schema, validators):
        self.schema = schema
        self.type = dict
        self.validators = validators

    def validate(self, data):
        """Check if values in dictionary validate using their own validators.

        :param data: Data to validate
        :type data: object

        """
        if not isinstance(data, dict):
            raise ValidationTypeError(self, data)

        errors = []
        key_validators_not_matched = set(self.validators.keys())
        for key, value in sorted(data.items()):
            for key_validator, value_validator in self.validators.items():
                try:
                    # TODO: handle situation in which key validates
                    # against multiple validators, but value doesn't
                    key_validator.validate(key)
                except ValidationError:
                    continue
                else:
                    if key_validator in key_validators_not_matched:
                        key_validators_not_matched.remove(key_validator)

                try:
                    value_validator.validate(value)
                except ValidationError as error:
                    error.path.appendleft(key)
                    errors.append(error)
                break
            else:
                errors.append(ValidationUnknownKeyError(self, key))

        if key_validators_not_matched:
            errors.extend([
                ValidationMissingKeyError(self, key_validator)
                for key_validator in key_validators_not_matched
            ])

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise ValidationMultipleError(self, errors, data)


class RegexValidator(Validator):
    """Validator that checks if data matches a regular expression.

    :param schema: Schema that created this validator
    :type schema: schemania.schema.Schema
    :param regex: Regular expression to match against data
    :type regex: re.RegexObject

    """

    def __init__(self, schema, regex):
        self.schema = schema
        self.type = str
        self.regex = regex

    def __str__(self):
        """Return validator string representation.

        This is useful for some formatters that need to get access to the
        original value passed in the raw schema.

        """
        return repr(self.regex.pattern)

    def validate(self, data):
        """Check if data matches regular expression.

        :param data: Data to validate
        :type data: object

        """
        if not isinstance(data, self.type):
            raise ValidationTypeError(self, data)

        if self.regex.match(data) is None:
            raise ValidationMatchError(self, data)
