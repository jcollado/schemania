"""Schema tests."""

import pytest

from schemania.error import (
    ValidationMultipleError,
    ValidationTypeError,
)
from schemania.schema import Schema
from schemania.validator import (
    DictValidator,
    ListValidator,
    TypeValidator,
)


class TestSchema(object):
    """Test schema."""

    @pytest.mark.parametrize(
        'raw_schema, expected_cls',
        (
            (str, TypeValidator),
            (int, TypeValidator),
            ([str], ListValidator),
            ({'a': str}, DictValidator),
        ),
    )
    def test_compile(self, raw_schema, expected_cls):
        """Compile raw schema."""
        schema = Schema(raw_schema)
        assert isinstance(schema.validator, expected_cls)

    @pytest.mark.parametrize(
        'raw_schema, data',
        (
            (str, 'str'),
            (int, 1),
            ([str], ['str']),
            ({'a': str}, {'a': 'str'}),
        ),
    )
    def test_validation_passes(self, raw_schema, data):
        """Compile raw schema and validate data that matches."""
        schema = Schema(raw_schema)
        schema(data)

    @pytest.mark.parametrize(
        'raw_schema, data',
        (
            (str, None),
            (int, None),
            ([str], None),
            ({'a': str}, None),
        ),
    )
    def test_validation_fails_with_type_error(self, raw_schema, data):
        """Compile raw schema and validation fails with type error."""
        schema = Schema(raw_schema)
        with pytest.raises(ValidationTypeError):
            schema(data)

    @pytest.mark.parametrize(
        'raw_schema, data',
        (
            ([str], ['a', 1, [], {}]),
            ([int], ['a', 1, [], {}]),
            (
                {'a': str, 'b': int},
                {'a': 1, 'b': 'string'},
            ),
        ),
    )
    def test_validation_fails_with_multiple_error(self, raw_schema, data):
        """Compile raw schema and validation fails with multiple error."""
        schema = Schema(raw_schema)
        with pytest.raises(ValidationMultipleError):
            schema(data)
