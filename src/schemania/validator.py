"""Schema validators.

Validators are the objects that are used to check if a given data matches the
expected structure.

"""
from schemania.error import (
    ValidationError,
    ValidationMultipleError,
    ValidationTypeError,
)


class Validator(object):
    """Validator base class."""


class TypeValidator(Validator):
    """Validator that checks data by its type.

    :param schema: Schema that created this validator
    :type schema: schemania.schema.Schema

    """
    def __init__(self, schema, type_):
        self.schema = schema
        self.type = type_

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
    :param value_validators: Dictionary of value validators
    :type value_validators: Dict[str, schemania.validator.Validator]

    """
    def __init__(self, schema, value_validators):
        self.schema = schema
        self.type = dict
        self.value_validators = value_validators

    def validate(self, data):
        if not isinstance(data, dict):
            raise ValidationTypeError(self, data)

        errors = []
        for key, value in data.items():
            try:
                self.value_validators[key].validate(value)
            except ValidationError as error:
                error.path.appendleft(key)
                errors.append(error)

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise ValidationMultipleError(self, errors, data)
