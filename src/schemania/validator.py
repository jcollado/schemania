"""Schema validators.

Validators are the objects that are used to check if a given data matches the
expected structure.

"""
from schemania.error import (
    ValidationError,
    ValidationFunctionError,
    ValidationLengthError,
    ValidationLiteralError,
    ValidationMatchError,
    ValidationMissingKeyError,
    ValidationMultipleError,
    ValidationTypeError,
    ValidationUnknownKeyError,
)


class Validator(object):
    """Validator base class."""
    def __init__(self, schema, optional=False):
        self.schema = schema
        self.optional = optional


class LiteralValidator(Validator):
    """Validator that checks that data is equal to a given literal value.

    :param schema: Schema that created this validator
    :type schema: schemania.schema.Schema
    :param literal: Literal value that data should be equal to
    :type literal: object

    """
    def __init__(self, schema, literal, optional=False):
        super(LiteralValidator, self).__init__(schema, optional)
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
        :returns: Validated data
        :rtype: object

        """
        if not data == self.literal:
            raise ValidationLiteralError(self, data)

        return data


class TypeValidator(Validator):
    """Validator that checks data by its type.

    :param schema: Schema that created this validator
    :type schema: schemania.schema.Schema
    :param type_: Type that data should be an instance of
    :param type_: type

    """
    def __init__(self, schema, type_, optional=False):
        super(TypeValidator, self).__init__(schema, optional)
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
        :returns: Validated data
        :rtype: object


        """
        if not isinstance(data, self.type):
            raise ValidationTypeError(self, data)

        return data


class ListValidator(Validator):
    """Validator that checks elements in a list.

    :param schema: Schema that created this validator
    :type schema: schemania.schema.Schema
    :param element_validator: Validator used to check every list element
    :type element_validator: schemania.validator.Validator

    """

    def __init__(self, schema, element_validator):
        super(ListValidator, self).__init__(schema)
        self.type = list
        self.element_validator = element_validator

    def validate(self, data):
        """Check if each element in data validates against element validator.

        :param data: Data to validate
        :type data: object
        :returns: Validated data
        :rtype: object


        """
        if not isinstance(data, list):
            raise ValidationTypeError(self, data)

        new_data = []
        errors = []
        for index, element in enumerate(data):
            try:
                new_element = self.element_validator.validate(element)
                new_data.append(new_element)
            except ValidationError as error:
                error.path.appendleft(index)
                errors.append(error)

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise ValidationMultipleError(self, data, errors)

        return new_data


class DictValidator(Validator):
    """Validator that checks key-value pairs in a dictionary.

    :param schema: Schema that created this validator
    :type schema: schemania.schema.Schema
    :param validators: Dictionary of key-value validators
    :type validators:
        Dict[schemania.validator.Validator, schemania.validator.Validator]

    """
    def __init__(self, schema, validators):
        super(DictValidator, self).__init__(schema)
        self.type = dict
        self.validators = validators

    def validate(self, data):
        """Check if values in dictionary validate using their own validators.

        :param data: Data to validate
        :type data: object
        :returns: Validated data
        :rtype: object


        """
        if not isinstance(data, dict):
            raise ValidationTypeError(self, data)

        new_data = {}
        errors = []
        key_validators_not_matched = {
            key_validator
            for key_validator in self.validators.keys()
            # Optional validators are not tracked
            # because there's no missing key error when they are not matched
            if not key_validator.optional
        }
        for key, value in sorted(data.items()):
            for key_validator, value_validator in self.validators.items():
                try:
                    # TODO: handle situation in which key validates
                    # against multiple validators, but value doesn't
                    new_key = key_validator.validate(key)
                except ValidationError:
                    continue
                else:
                    if key_validator in key_validators_not_matched:
                        key_validators_not_matched.remove(key_validator)

                try:
                    new_value = value_validator.validate(value)
                except ValidationError as error:
                    error.path.appendleft(key)
                    errors.append(error)
                else:
                    new_data[new_key] = new_value

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
            raise ValidationMultipleError(self, data, errors)

        return new_data


class RegexValidator(Validator):
    """Validator that checks if data matches a regular expression.

    :param schema: Schema that created this validator
    :type schema: schemania.schema.Schema
    :param regex: Regular expression to match against data
    :type regex: re.RegexObject

    """

    def __init__(self, schema, regex, optional=False):
        super(RegexValidator, self).__init__(schema, optional)
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
        :returns: Validated data
        :rtype: object


        """
        if not isinstance(data, self.type):
            raise ValidationTypeError(self, data)

        if self.regex.match(data) is None:
            raise ValidationMatchError(self, data)

        return data


class SelfValidator(Validator):
    """Validator that checks data using the root validator recursively."""

    def validate(self, data):
        """Check if data validates using the root validator.

        :param data: Data to validate
        :type data: object
        :returns: Validated data
        :rtype: object

        """
        return self.schema.validator.validate(data)


class AllValidator(Validator):
    """Validator that checks data with multiple validators that must pass."""
    def __init__(self, schema, validators, optional=False):
        super(AllValidator, self).__init__(schema, optional)
        self.validators = validators

    def validate(self, data):
        """Check if data validates for all validators.

        :param data: Data to validate
        :type data: object
        :returns: Validated data
        :rtype: object

        """
        errors = []
        for validator in self.validators:
            try:
                data = validator.validate(data)
            except ValidationError as error:
                errors.append(error)

        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise ValidationMultipleError(self, data, errors)

        return data


class AnyValidator(Validator):
    """Validator that checks data with multiple validators.

    For the validation to be considered valid, at least one of the validators
    must pass.

    """
    def __init__(self, schema, validators, optional=False):
        super(AnyValidator, self).__init__(schema, optional)
        self.validators = validators

    def validate(self, data):
        """Check if data validates for at least one validator.

        :param data: Data to validate
        :type data: object
        :returns: Validated data
        :rtype: object

        """
        errors = []
        for validator in self.validators:
            try:
                data = validator.validate(data)
            except ValidationError as error:
                errors.append(error)

        if len(errors) == len(self.validators):
            raise ValidationMultipleError(self, data, errors)

        return data


class FunctionValidator(Validator):
    """Validator that runs a function on data.

    The function can be used to write a custom validator or to transform data.

    """
    def __init__(self, schema, func):
        super(FunctionValidator, self).__init__(schema)
        self.func = func

    def validate(self, data):
        """Use function to validate/transform data.

        :param data: Data to validate
        :type data: object
        :returns: Validated data
        :rtype: object

        """
        try:
            new_data = self.func(data)
        except Exception as exception:
            raise ValidationFunctionError(self, data, exception)

        return new_data


class LengthValidator(Validator):
    """Validator that check data length."""
    def __init__(self, schema, min_length=None, max_length=None):
        super(LengthValidator, self).__init__(schema)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, data):
        """Check if data length is between expected values."""
        data_length = len(data)
        if self.min_length is not None:
            if data_length < self.min_length:
                raise ValidationLengthError(self, data)

        if self.max_length is not None:
            if data_length > self.max_length:
                raise ValidationLengthError(self, data)

        return data
