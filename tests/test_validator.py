"""Schema validator tests."""
import re

import pytest

from schemania.error import (
    ValidationError,
    ValidationLiteralError,
    ValidationMatchError,
    ValidationMissingKeyError,
    ValidationMultipleError,
    ValidationTypeError,
    ValidationUnknownKeyError,
)
from schemania.schema import DEFAULT_FORMATTERS
from schemania.validator import (
    AllValidator,
    AnyValidator,
    DictValidator,
    ListValidator,
    LiteralValidator,
    RegexValidator,
    TypeValidator,
)


class MockSchema(object):
    """Mock schema to use as an argument for validators.

    Validator objects are expected to be created within a schema, except in
    this testing module.

    """


Schema = MockSchema()
Schema.formatters = DEFAULT_FORMATTERS


class TestLiteralValidator(object):
    """LiteralValidator tests."""

    @pytest.mark.parametrize(
        'literal, data',
        (
            ('string', 'string'),
            (1, 1),
        ),
    )
    def test_validation_passes(self, literal, data):
        """Validation passes when data is equal to literal value."""
        validator = LiteralValidator(Schema, literal)
        validator.validate(data)

    @pytest.mark.parametrize('literal', ('string', 1))
    def test_validation_fails(self, literal):
        """"Validation fails when data isn't equal to literal value."""
        validator = LiteralValidator(Schema, literal)
        with pytest.raises(ValidationLiteralError):
            validator.validate(None)


class TestTypeValidator(object):
    """TypeValidator tests."""

    @pytest.mark.parametrize(
        'type_, data',
        (
            (str, 'string'),
            (int, 1),
            (list, []),
            (dict, {}),
        ),
    )
    def test_validation_passes(self, type_, data):
        """Validation passes when data matches expected type."""
        validator = TypeValidator(Schema, type_)
        validator.validate(data)

    @pytest.mark.parametrize('type_', (str, int, list, dict))
    def test_validation_fails(self, type_):
        """"Validation fails when data doesn't match expected type."""
        validator = TypeValidator(Schema, type_)
        with pytest.raises(ValidationTypeError):
            validator.validate(None)


class TestListValidator(object):
    """ListValidator tests."""

    @pytest.mark.parametrize(
        'type_, data',
        (
            (str, ['a', 'b', 'c']),
            (int, [1, 2, 3]),
            (list, [[], [], []]),
            (dict, [{}, {}, {}]),
        ),
    )
    def test_validation_passes(self, type_, data):
        """Validation passes when data matches expected type."""
        type_validator = TypeValidator(Schema, type_)
        list_validator = ListValidator(Schema, type_validator)
        list_validator.validate(data)

    @pytest.mark.parametrize(
        'type_, data',
        (
            (str, ['a', 'b', 'c', None]),
            (int, [1, 2, 3, None]),
            (list, [[], [], [], None]),
            (dict, [{}, {}, {}, None]),
        ),
    )
    def test_validation_fails_with_type_error(self, type_, data):
        """"Validation fails with type error."""
        type_validator = TypeValidator(Schema, type_)
        list_validator = ListValidator(Schema, type_validator)
        with pytest.raises(ValidationTypeError):
            list_validator.validate(data)

    @pytest.mark.parametrize(
        'type_, data',
        (
            (str, ['a', 1, [], {}]),
            (int, ['a', 1, [], {}]),
            (list, ['a', 1, [], {}]),
            (dict, ['a', 1, [], {}]),
        ),
    )
    def test_validation_fails_with_multiple_error(self, type_, data):
        """"Validation fails with multiple error."""
        type_validator = TypeValidator(Schema, type_)
        list_validator = ListValidator(Schema, type_validator)
        with pytest.raises(ValidationMultipleError):
            list_validator.validate(data)


class TestDictValidator(object):
    """DictValidator tests."""

    @pytest.mark.parametrize(
        'validators, data',
        (
            (
                {
                    LiteralValidator(Schema, 'a'):
                        TypeValidator(Schema, str),
                    LiteralValidator(Schema, 'b'):
                        TypeValidator(Schema, int),
                    LiteralValidator(Schema, 'c'):
                        TypeValidator(Schema, list),
                    LiteralValidator(Schema, 'd'):
                        TypeValidator(Schema, dict),
                    LiteralValidator(Schema, 'e', optional=True):
                        TypeValidator(Schema, str),
                },
                {
                    'a': 'string',
                    'b': 1,
                    'c': [],
                    'd': {},
                },
            ),
        ),
    )
    def test_validation_passes(self, validators, data):
        """Validation passes when data matches expected type."""
        dict_validator = DictValidator(Schema, validators)
        dict_validator.validate(data)

    @pytest.mark.parametrize(
        'validators, data',
        (
            (
                {
                    LiteralValidator(Schema, 'a'):
                        TypeValidator(Schema, str),
                },
                {'a': None},
            ),
            (
                {
                    LiteralValidator(Schema, 'a'):
                        TypeValidator(Schema, int),
                },
                {'a': None},
            ),
            (
                {
                    LiteralValidator(Schema, 'a'):
                        TypeValidator(Schema, list),
                },
                {'a': None},
            ),
            (
                {
                    LiteralValidator(Schema, 'a'):
                        TypeValidator(Schema, dict),
                },
                {'a': None},
            ),
        ),
    )
    def test_validation_fails_with_type_error(self, validators, data):
        """Validation fails with type error."""
        dict_validator = DictValidator(Schema, validators)
        with pytest.raises(ValidationTypeError):
            dict_validator.validate(data)

    @pytest.mark.parametrize(
        'validators, data',
        (
            (
                {
                    LiteralValidator(Schema, 'a'):
                        TypeValidator(Schema, str),
                    LiteralValidator(Schema, 'b'):
                        TypeValidator(Schema, int),
                    LiteralValidator(Schema, 'c'):
                        TypeValidator(Schema, list),
                    LiteralValidator(Schema, 'd'):
                        TypeValidator(Schema, dict),
                },
                {
                    'a': None,
                    'b': None,
                    'c': None,
                    'd': None,
                },
            ),
            (
                {
                    LiteralValidator(Schema, 'a'):
                        TypeValidator(Schema, str),
                },
                {'b': None},
            ),
        ),
    )
    def test_validation_fails_with_multiple_error(
            self, validators, data):
        """Validation fails with multiple error."""
        dict_validator = DictValidator(Schema, validators)
        with pytest.raises(ValidationMultipleError):
            dict_validator.validate(data)

    @pytest.mark.parametrize(
        'validators, data',
        (
            (
                {
                    LiteralValidator(Schema, 'a'):
                        TypeValidator(Schema, str),
                },
                {
                    'a': 'string',
                    'b': None,
                },
            ),
        ),
    )
    def test_validation_fails_with_unknown_key_error(
            self, validators, data):
        """Validation fails with unknown key error."""
        dict_validator = DictValidator(Schema, validators)
        with pytest.raises(ValidationUnknownKeyError):
            dict_validator.validate(data)

    @pytest.mark.parametrize(
        'validators, data',
        (
            (
                {
                    LiteralValidator(Schema, 'a'):
                        TypeValidator(Schema, str),
                },
                {},
            ),
        ),
    )
    def test_validation_fails_with_missing_key_error(
            self, validators, data):
        """Validation fails with mmissing key error."""
        dict_validator = DictValidator(Schema, validators)
        with pytest.raises(ValidationMissingKeyError):
            dict_validator.validate(data)


class TestRegexValidator(object):
    """RegexValidator tests."""

    @pytest.mark.parametrize(
        'regex, data',
        (
            (re.compile(r'^\d+$'), '1234567890'),
            (re.compile(r'^[a-z]+$'), 'string'),
        ),
    )
    def test_validation_passes(self, regex, data):
        """Validation passes when data matches against regular expression."""
        regex_validator = RegexValidator(Schema, regex)
        regex_validator.validate(data)

    @pytest.mark.parametrize(
        'regex, data',
        (
            (re.compile(r'^\d+$'), 0),
            (re.compile(r'^[a-z]+$'), None),
        ),
    )
    def test_validation_fails_with_type_error(self, regex, data):
        """Validation fails with match error."""
        regex_validator = RegexValidator(Schema, regex)
        with pytest.raises(ValidationTypeError):
            regex_validator.validate(data)

    @pytest.mark.parametrize(
        'regex, data',
        (
            (re.compile(r'^\d+$'), 'string'),
            (re.compile(r'^[a-z]+$'), '123456790'),
        ),
    )
    def test_validation_fails_with_match_error(self, regex, data):
        """Validation fails with match error."""
        regex_validator = RegexValidator(Schema, regex)
        with pytest.raises(ValidationMatchError):
            regex_validator.validate(data)


class TestAllValidator(object):
    """AllValidator tests."""

    @pytest.mark.parametrize(
        'validators, data',
        (
            (
                (
                    TypeValidator(Schema, str),
                    LiteralValidator(Schema, 'string'),
                ),
                'string',
            ),
            (
                (
                    TypeValidator(Schema, int),
                    LiteralValidator(Schema, 1),
                ),
                1,
            ),
        ),
    )
    def test_validation_passes(self, validators, data):
        """Validation passes when all validator calls pass."""
        validator = AllValidator(Schema, validators)
        validator.validate(data)

    @pytest.mark.parametrize(
        'validators, data',
        (
            (
                (
                    TypeValidator(Schema, str),
                    LiteralValidator(Schema, 1),
                ),
                'string',
            ),
            (
                (
                    TypeValidator(Schema, int),
                    LiteralValidator(Schema, 'string'),
                ),
                1,
            ),
        ),
    )
    def test_validation_fails(self, validators, data):
        """"Validation fails when at least one validator fails."""
        validator = AllValidator(Schema, validators)
        with pytest.raises(ValidationError):
            validator.validate(data)


class TestAnyValidator(object):
    """AnyValidator tests."""

    @pytest.mark.parametrize(
        'validators, data',
        (
            (
                (
                    LiteralValidator(Schema, 'string'),
                    LiteralValidator(Schema, 1),
                ),
                'string',
            ),
            (
                (
                    LiteralValidator(Schema, 'string'),
                    LiteralValidator(Schema, 1),
                ),
                1,
            ),
        ),
    )
    def test_validation_passes(self, validators, data):
        """Validation passes when at least one validator call passes."""
        validator = AnyValidator(Schema, validators)
        validator.validate(data)

    @pytest.mark.parametrize(
        'validators, data',
        (
            (
                (
                    TypeValidator(Schema, int),
                    LiteralValidator(Schema, 1),
                ),
                'string',
            ),
            (
                (
                    TypeValidator(Schema, str),
                    LiteralValidator(Schema, 'string'),
                ),
                1,
            ),
        ),
    )
    def test_validation_fails(self, validators, data):
        """"Validation fails when all validator calls fail."""
        validator = AnyValidator(Schema, validators)
        with pytest.raises(ValidationError):
            validator.validate(data)
