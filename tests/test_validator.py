"""Schema validator tests."""
import re

import pytest

from schemania.error import (
    ValidationLiteralError,
    ValidationMatchError,
    ValidationMultipleError,
    ValidationTypeError,
)
from schemania.validator import (
    DictValidator,
    ListValidator,
    LiteralValidator,
    RegexValidator,
    TypeValidator,
)


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
        validator = LiteralValidator('<schema>', literal)
        validator.validate(data)

    @pytest.mark.parametrize('literal', ('string', 1))
    def test_validation_fails(self, literal):
        """"Validation fails when data isn't equal to literal value."""
        validator = LiteralValidator('<schema>', literal)
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
        validator = TypeValidator('<schema>', type_)
        validator.validate(data)

    @pytest.mark.parametrize('type_', (str, int, list, dict))
    def test_validation_fails(self, type_):
        """"Validation fails when data doesn't match expected type."""
        validator = TypeValidator('<schema>', type_)
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
        type_validator = TypeValidator('<schema>', type_)
        list_validator = ListValidator('<schema>', type_validator)
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
        type_validator = TypeValidator('<schema>', type_)
        list_validator = ListValidator('<schema>', type_validator)
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
        type_validator = TypeValidator('<schema>', type_)
        list_validator = ListValidator('<schema>', type_validator)
        with pytest.raises(ValidationMultipleError):
            list_validator.validate(data)


class TestDictValidator(object):
    """DictValidator tests."""

    @pytest.mark.parametrize(
        'value_validators, data',
        (
            (
                {
                    'a': TypeValidator('<schema>', str),
                    'b': TypeValidator('<schema>', int),
                    'c': TypeValidator('<schema>', list),
                    'd': TypeValidator('<schema>', dict),
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
    def test_validation_passes(self, value_validators, data):
        """Validation passes when data matches expected type."""
        dict_validator = DictValidator('<schema>', value_validators)
        dict_validator.validate(data)

    @pytest.mark.parametrize(
        'value_validators, data',
        (
            (
                {'a': TypeValidator('<schema>', str)},
                {'a': None},
            ),
            (
                {'a': TypeValidator('<schema>', int)},
                {'a': None},
            ),
            (
                {'a': TypeValidator('<schema>', list)},
                {'a': None},
            ),
            (
                {'a': TypeValidator('<schema>', dict)},
                {'a': None},
            ),
        ),
    )
    def test_validation_fails_with_type_error(self, value_validators, data):
        """Validation fails with type error."""
        dict_validator = DictValidator('<schema>', value_validators)
        with pytest.raises(ValidationTypeError):
            dict_validator.validate(data)

    @pytest.mark.parametrize(
        'value_validators, data',
        (
            (
                {
                    'a': TypeValidator('<schema>', str),
                    'b': TypeValidator('<schema>', int),
                    'c': TypeValidator('<schema>', list),
                    'd': TypeValidator('<schema>', dict),
                },
                {
                    'a': None,
                    'b': None,
                    'c': None,
                    'd': None,
                },
            ),
        ),
    )
    def test_validation_fails_with_multiple_error(
            self, value_validators, data):
        """Validation fails with multiple error."""
        dict_validator = DictValidator('<schema>', value_validators)
        with pytest.raises(ValidationMultipleError):
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
        regex_validator = RegexValidator('<schema>', regex)
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
        regex_validator = RegexValidator('<schema>', regex)
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
        regex_validator = RegexValidator('<schema>', regex)
        with pytest.raises(ValidationMatchError):
            regex_validator.validate(data)
