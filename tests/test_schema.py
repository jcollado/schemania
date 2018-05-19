"""Schema tests."""

import re

import pytest

from schemania.error import (
    ValidationLiteralError,
    ValidationMatchError,
    ValidationMultipleError,
    ValidationTypeError,
    ValidationUnknownKeyError,
)
from schemania.schema import Schema
from schemania.validator import (
    DictValidator,
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
        ),
    )
    def test_compile(self, raw_schema, expected_cls):
        """Compile raw schema."""
        schema = Schema(raw_schema)
        assert isinstance(schema.validator, expected_cls)

    @pytest.mark.parametrize(
        'raw_schema, data',
        (
            ('string', 'string'),
            (1, 1),
            (str, 'str'),
            (int, 1),
            ([str], ['str']),
            ({'a': str}, {'a': 'str'}),
            (re.compile(r'^\d+$'), '1234567890'),
            ({re.compile(r'^\w\d'): int}, {'a1': 0, 'b2': 0}),
        ),
    )
    def test_validation_passes(self, raw_schema, data):
        """Compile raw schema and validate data that matches."""
        schema = Schema(raw_schema)
        schema(data)

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
    def test_validation_fails_unknown_key_error(
            self, raw_schema, data, expected):
        """Compile raw schema and validation fails with type error."""
        schema = Schema(raw_schema)
        with pytest.raises(ValidationUnknownKeyError) as excinfo:
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
                    "- expected 'str' in '[1]', but got 1\n"
                    "- expected 'str' in '[2]', but got []\n"
                    "- expected 'str' in '[3]', but got {}"
                ),
            ),
            (
                [int],
                ['a', 1, [], {}],
                (
                    'multiple errors:\n'
                    "- expected 'int' in '[0]', but got 'a'\n"
                    "- expected 'int' in '[2]', but got []\n"
                    "- expected 'int' in '[3]', but got {}"
                ),
            ),
            (
                {'a': str, 'b': int},
                {'a': 1, 'b': 'string', 'c': None},
                (
                    'multiple errors:\n'
                    "- expected 'str' in 'a', but got 1\n"
                    "- expected 'int' in 'b', but got 'string'\n"
                    "- unknown key 'c'"
                ),
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
