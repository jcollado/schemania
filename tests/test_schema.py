"""Schema tests."""

import re

import pytest

from schemania.error import (
    ValidationFunctionError,
    ValidationLengthError,
    ValidationLiteralError,
    ValidationMatchError,
    ValidationMissingKeyError,
    ValidationMultipleError,
    ValidationTypeError,
    ValidationUnknownKeyError,
)
from schemania.schema import (
    All,
    Any,
    Length,
    Optional,
    Schema,
    Self,
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
    TypeValidator,
)


class TestSchema(object):
    """Test schema."""

    @pytest.mark.parametrize(
        'raw_schema, expected_cls',
        (
            ('string', LiteralValidator),
            (1, LiteralValidator),
            (str, TypeValidator),
            (int, TypeValidator),
            ([str], ListValidator),
            ({'a': str}, DictValidator),
            (re.compile(r'^\d+$'), RegexValidator),
            (All(str), AllValidator),
            (Any(str), AnyValidator),
            (lambda string: string.strip(), FunctionValidator),
            (Length(str), LengthValidator),
        ),
    )
    def test_compile(self, raw_schema, expected_cls):
        """Compile raw schema."""
        schema = Schema(raw_schema)
        assert isinstance(schema.validator, expected_cls)

    @pytest.mark.parametrize(
        'raw_schema, data, expected',
        (
            ('string', 'string', 'string'),
            (1, 1, 1),
            (str, 'str', 'str'),
            (int, 1, 1),
            ([str], ['str'], ['str']),
            ({'a': str}, {'a': 'string'}, {'a': 'string'}),
            (
                {str: str},
                {'a': 'string', 'b': 'string'},
                {'a': 'string', 'b': 'string'},
            ),
            (
                {int: str},
                {0: 'string', 1: 'string'},
                {0: 'string', 1: 'string'},
            ),
            (re.compile(r'^\d+$'), '1234567890', '1234567890'),
            (
                {re.compile(r'^\w\d'): int},
                {'a1': 0, 'b2': 0},
                {'a1': 0, 'b2': 0},
            ),
            ({Optional('a'): str}, {}, {}),
            (
                {'a': str, Optional('next'): Self},
                {
                    'a': 'string',
                    'next': {
                        'a': 'string',
                        'next': {
                            'a': 'string',
                        }
                    },
                },
                {
                    'a': 'string',
                    'next': {
                        'a': 'string',
                        'next': {
                            'a': 'string',
                        }
                    },
                },
            ),
            (
                {'a': str, Optional('children'): [Self]},
                {
                    'a': 'string',
                    'children': [
                        {
                            'a': 'string',
                            'children': [
                                {'a': 'string'},
                            ],
                        },
                        {'a': 'string'},
                        {'a': 'string', 'children': []},
                    ],
                },
                {
                    'a': 'string',
                    'children': [
                        {
                            'a': 'string',
                            'children': [
                                {'a': 'string'},
                            ],
                        },
                        {'a': 'string'},
                        {'a': 'string', 'children': []},
                    ],
                },
            ),
            (All(str), 'string', 'string'),
            (All(str, re.compile('^[a-z]+$')), 'string', 'string'),
            (Any(str), 'string', 'string'),
            (Any(str, int), 'string', 'string'),
            (lambda string: string.strip(), '  string  ', 'string'),
            (lambda string: int(string), '123467890', 123467890),
            (Length(min_length=0, max_length=10), 'string', 'string'),
        ),
    )
    def test_validation_passes(self, raw_schema, data, expected):
        """Compile raw schema and validate data that matches."""
        schema = Schema(raw_schema)
        new_data = schema(data)
        assert new_data == expected

    @pytest.mark.parametrize(
        'raw_schema, data, expected',
        (
            ('string', None, "expected 'string', but got None"),
            (1, None, "expected 1, but got None"),
        ),
    )
    def test_validation_fails_with_literal_error(
            self, raw_schema, data, expected):
        """Compile raw schema and validation fails with literal error."""
        schema = Schema(raw_schema)
        with pytest.raises(ValidationLiteralError) as excinfo:
            schema(data)
        assert str(excinfo.value) == expected

    @pytest.mark.parametrize(
        'raw_schema, data, expected',
        (
            (str, None, "expected 'str', but got None"),
            (int, None, "expected 'int', but got None"),
            ([str], None, "expected 'list', but got None"),
            ({'a': str}, None, "expected 'dict', but got None"),
            (re.compile(r'^\d+$'), None, "expected 'str', but got None"),
        ),
    )
    def test_validation_fails_with_type_error(
            self, raw_schema, data, expected):
        """Compile raw schema and validation fails with type error."""
        schema = Schema(raw_schema)
        with pytest.raises(ValidationTypeError) as excinfo:
            schema(data)
        assert str(excinfo.value) == expected

    @pytest.mark.parametrize(
        'raw_schema, data, expected',
        (
            (
                {'a': str},
                {'a': 'string', 'b': 0},
                "unknown key 'b'",
            ),
        ),
    )
    def test_validation_fails_with_unknown_key_error(
            self, raw_schema, data, expected):
        """Compile raw schema and validation fails with unknown key error."""
        schema = Schema(raw_schema)
        with pytest.raises(ValidationUnknownKeyError) as excinfo:
            schema(data)
        assert str(excinfo.value) == expected

    @pytest.mark.parametrize(
        'raw_schema, data, expected',
        (
            ({'a': str}, {}, "missing key 'a'"),
            ({re.compile(r'\w+'): str}, {}, "missing key '\\\\w+'"),
            ({str: str}, {}, "missing key 'str'"),
            ({int: str}, {}, "missing key 'int'"),
        ),
    )
    def test_validation_fails_with_missing_key_error(
            self, raw_schema, data, expected):
        """Compile raw schema and validation fails with missing key error."""
        schema = Schema(raw_schema)
        with pytest.raises(ValidationMissingKeyError) as excinfo:
            schema(data)
        assert str(excinfo.value) == expected

    @pytest.mark.parametrize(
        'raw_schema, data, expected',
        (
            (
                [str],
                ['a', 1, [], {}],
                (
                    'multiple errors:\n'
                    "- expected 'str' in [1], but got 1\n"
                    "- expected 'str' in [2], but got []\n"
                    "- expected 'str' in [3], but got {}"
                ),
            ),
            (
                [int],
                ['a', 1, [], {}],
                (
                    'multiple errors:\n'
                    "- expected 'int' in [0], but got 'a'\n"
                    "- expected 'int' in [2], but got []\n"
                    "- expected 'int' in [3], but got {}"
                ),
            ),
            (
                {'a': str, 'b': int},
                {'a': 1, 'b': 'string', 'c': None},
                (
                    'multiple errors:\n'
                    "- expected 'str' in ['a'], but got 1\n"
                    "- expected 'int' in ['b'], but got 'string'\n"
                    "- unknown key 'c'"
                ),
            ),
            (
                All(str, 'string'),
                1,
                (
                    'multiple errors:\n'
                    "- expected 'str', but got 1\n"
                    "- expected 'string', but got 1"
                )
            ),
            (
                Any(str, 'string'),
                1,
                (
                    'multiple errors:\n'
                    "- expected 'str', but got 1\n"
                    "- expected 'string', but got 1"
                )
            ),
        ),
    )
    def test_validation_fails_with_multiple_error(
            self, raw_schema, data, expected):
        """Compile raw schema and validation fails with multiple error."""
        schema = Schema(raw_schema)
        with pytest.raises(ValidationMultipleError) as excinfo:
            schema(data)
        assert str(excinfo.value) == expected

    @pytest.mark.parametrize(
        'raw_schema, data, expected',
        (
            (
                re.compile(r'^\d+$'), 'string',
                "expected to match against regex '^\\\\d+$', but got 'string'",
            ),
            (
                re.compile(r'^[a-z]+$'), '1234567890',
                (
                    "expected to match against regex '^[a-z]+$', "
                    "but got '1234567890'"
                ),
            ),
        ),
    )
    def test_validation_fails_with_match_error(
            self, raw_schema, data, expected):
        """Compile raw schema and validation fails with literal error."""
        schema = Schema(raw_schema)
        with pytest.raises(ValidationMatchError) as excinfo:
            schema(data)
        assert str(excinfo.value) == expected

    @pytest.mark.parametrize(
        'raw_schema, data, expected',
        (
            (
                lambda string: int(string),
                'string',
                "error calling '<lambda>' with data 'string'",
            ),
            (
                [lambda string: int(string)],
                ['12347890', 'string'],
                "error calling '<lambda>' in [1] with data 'string'",
            ),
            (
                {'a': lambda string: int(string)},
                {'a': 'string'},
                "error calling '<lambda>' in ['a'] with data 'string'",
            ),
        ),
    )
    def test_validation_fails_with_function_error(
            self, raw_schema, data, expected):
        """Compile raw schema and validation fails with function error."""
        schema = Schema(raw_schema)
        with pytest.raises(ValidationFunctionError) as excinfo:
            schema(data)
        assert str(excinfo.value) == expected

    @pytest.mark.parametrize(
        'raw_schema, data, expected',
        (
            (
                Length(min_length=1),
                '',
                "length must be greater than 1, got ''",
            ),
            (
                Length(max_length=5),
                'string',
                "length must be less than 5, got 'string'",
            ),
            (
                Length(min_length=1, max_length=5),
                'string',
                "length must be between 1 and 5, got 'string'",
            ),
            (
                [Length(min_length=1)],
                [''],
                "length must be greater than 1 in [0], got ''",
            ),
            (
                [Length(max_length=5)],
                ['string'],
                "length must be less than 5 in [0], got 'string'",
            ),
            (
                [Length(min_length=1, max_length=5)],
                ['string'],
                "length must be between 1 and 5 in [0], got 'string'",
            ),
        ),
    )
    def test_validation_fails_with_length_error(
            self, raw_schema, data, expected):
        """Compile raw schema and validation fails with length error."""
        schema = Schema(raw_schema)
        with pytest.raises(ValidationLengthError) as excinfo:
            schema(data)
        assert str(excinfo.value) == expected
