"""Formatters tests."""

import pytest

from schemania.error import (
    ValidationTypeError,
    ValidationMultipleError,
)
from schemania.formatter import (
    _format_path,
    default_type_formatter,
    default_multiple_formatter,
)
from schemania.validator import (
    TypeValidator,
    ListValidator,
)


@pytest.mark.parametrize(
    'path, expected',
    (
        (['a', 'b', 'c'], 'a.b.c'),
        ([0, 1, 2], '[0][1][2]'),
        (['a', 0, 'b', 1], 'a[0].b[1]'),
    ),
)
def test_format_attributes(path, expected):
    """Path is formatted as expected."""
    assert _format_path(path) == expected


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
            "expected 'str' in 'a[0]', but got 0",
        ),
        (
            int, 'string', ['a', 0],
            "expected 'int' in 'a[0]', but got 'string'",
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
    'errors, path, expected',
    (
        (
            ('error#1', 'error#2'), [],
            'multiple errors:\n- error#1\n- error#2'
        ),
        (
            ('error#1', 'error#2'), ['a', 0],
            "multiple errors in 'a[0]':\n- error#1\n- error#2"
        ),
    ),
)
def test_default_multiple_formatter(errors, path, expected):
    """Default multiple formatter returns error string as expected."""
    list_validator = ListValidator('<schema>', TypeValidator('<schema>', str))
    error = ValidationMultipleError(list_validator, errors, '<data>')
    error.path = path
    assert default_multiple_formatter(error) == expected
