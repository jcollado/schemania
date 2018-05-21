"""Formatters tests."""

import re

import pytest

from schemania.error import (
    ValidationFunctionError,
    ValidationLiteralError,
    ValidationMatchError,
    ValidationMissingKeyError,
    ValidationMultipleError,
    ValidationTypeError,
    ValidationUnknownKeyError,
)
from schemania.formatter import (
    _format_path,
    default_function_formatter,
    default_literal_formatter,
    default_match_formatter,
    default_missing_key_formatter,
    default_multiple_formatter,
    default_type_formatter,
    default_unknown_key_formatter,
)
from schemania.validator import (
    DictValidator,
    FunctionValidator,
    ListValidator,
    LiteralValidator,
    RegexValidator,
    TypeValidator,
)


@pytest.mark.parametrize(
    'path, expected',
    (
        (['a', 'b', 'c'], "['a']['b']['c']"),
        ([0, 1, 2], '[0][1][2]'),
        (['a', 0, 'b', 1], "['a'][0]['b'][1]"),
        (['a1', 'b2'], "['a1']['b2']"),
    ),
)
def test_format_path(path, expected):
    """Path is formatted as expected."""
    assert _format_path(path) == expected


@pytest.mark.parametrize(
    'literal, data, path, expected',
    (
        (
            'string', 0, [],
            "expected 'string', but got 0",
        ),
        (
            0, 'string', [],
            "expected 0, but got 'string'",
        ),
        (
            'string', 0, ['a', 0],
            "expected 'string' in ['a'][0], but got 0",
        ),
        (
            0, 'string', ['a', 0],
            "expected 0 in ['a'][0], but got 'string'",
        ),
    ),
)
def test_default_literal_formatter(literal, data, path, expected):
    """Default literal formatter returns error string as expected."""
    literal_validator = LiteralValidator('<schema>', literal)
    error = ValidationLiteralError(literal_validator, data)
    error.path = path
    assert default_literal_formatter(error) == expected


@pytest.mark.parametrize(
    'type_, data, path, expected',
    (
        (
            str, 0, [],
            "expected 'str', but got 0",
        ),
        (
            int, 'string', [],
            "expected 'int', but got 'string'",
        ),
        (
            str, 0, ['a', 0],
            "expected 'str' in ['a'][0], but got 0",
        ),
        (
            int, 'string', ['a', 0],
            "expected 'int' in ['a'][0], but got 'string'",
        ),
    ),
)
def test_default_type_formatter(type_, data, path, expected):
    """Default type formatter returns error string as expected."""
    type_validator = TypeValidator('<schema>', type_)
    error = ValidationTypeError(type_validator, data)
    error.path = path
    assert default_type_formatter(error) == expected


@pytest.mark.parametrize(
    'key, path, expected',
    (
        ('a', [], "unknown key 'a'"),
        ('a', ['a', 0], "unknown key 'a' in ['a'][0]"),
    ),
)
def test_default_unknown_key_formatter(key, path, expected):
    """Default unknown key formatter returns error string as expected."""
    dict_validator = DictValidator('<schema>', '<validators>')
    error = ValidationUnknownKeyError(dict_validator, key)
    error.path = path
    assert default_unknown_key_formatter(error) == expected


@pytest.mark.parametrize(
    'key, path, expected',
    (
        ('a', [], "missing key 'a'"),
        ('a', ['a', 0], "missing key 'a' in ['a'][0]"),
    ),
)
def test_default_missing_key_formatter(key, path, expected):
    """Default missing key formatter returns error string as expected."""
    dict_validator = DictValidator('<schema>', '<validators>')
    key_validator = LiteralValidator('<schema>', key)
    error = ValidationMissingKeyError(dict_validator, key_validator)
    error.path = path
    assert default_missing_key_formatter(error) == expected


@pytest.mark.parametrize(
    'errors, path, expected',
    (
        (
            ('error#1', 'error#2'), [],
            'multiple errors:\n- error#1\n- error#2'
        ),
        (
            ('error#1', 'error#2'), ['a', 0],
            "multiple errors in ['a'][0]:\n- error#1\n- error#2"
        ),
    ),
)
def test_default_multiple_formatter(errors, path, expected):
    """Default multiple formatter returns error string as expected."""
    list_validator = ListValidator('<schema>', TypeValidator('<schema>', str))
    error = ValidationMultipleError(list_validator, errors, '<data>')
    error.path = path
    assert default_multiple_formatter(error) == expected


@pytest.mark.parametrize(
    'regex, data, path, expected',
    (
        (
            re.compile(r'^\d+$'), 'string', [],
            "expected to match against regex '^\\\\d+$', but got 'string'",
        ),
        (
            re.compile(r'^[a-z]+$'), '1234567890', [],
            "expected to match against regex '^[a-z]+$', but got '1234567890'",
        ),
        (
            re.compile(r'^\d+$'), 'string', ['a', 0],
            (
                "expected to match against regex '^\\\\d+$' in ['a'][0], "
                "but got 'string'"
            ),
        ),
        (
            re.compile(r'^[a-z]+$'), '1234567890', ['a', 0],
            (
                "expected to match against regex '^[a-z]+$' in ['a'][0], "
                "but got '1234567890'"
            ),
        ),
    ),
)
def test_default_match_formatter(regex, data, path, expected):
    """Default match formatter returns error string as expected."""
    regex_validator = RegexValidator('<schema>', regex)
    error = ValidationMatchError(regex_validator, data)
    error.path = path
    assert default_match_formatter(error) == expected


@pytest.mark.parametrize(
    'func, data, path, expected',
    (
        (
            lambda string: int, 'string', [],
            "error calling '<lambda>' with data 'string'",
        ),
        (
            lambda string: int, 'string', ['a', 0],
            "error calling '<lambda>' in ['a'][0] with data 'string'",
        ),
    ),
)
def test_default_function_formatter(func, data, path, expected):
    """Default function formatter returns error string as expected."""
    function_validator = FunctionValidator('<schema>', func)
    exception = ValueError('invalid literal')
    error = ValidationFunctionError(function_validator, exception, data)
    error.path = path
    assert default_function_formatter(error) == expected
