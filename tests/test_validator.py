"""Schema validator tests."""
import pytest

from schemania.error import (
    ValidationMultipleError,
    ValidationTypeError,
)
from schemania.validator import (
    DictValidator,
    ListValidator,
    TypeValidator,
)


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
