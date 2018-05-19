"""Formatters.

Formatters are the objects that are used to transform an error in to a text
representation to the user. There's a default implementatio of all the error
classes supported, but it's also possible to create custom ones and overwrite
the default behavior.

"""

import re


def _format_path(path):
    """Format path to data for which an error was found.

    :param path: Path as a list of keys/indexes used to get to a piece of data
    :type path: collections.deque[str|int]
    :returns: String representation of a given path
    :rtype: str

    """
    path_with_dots = '.'.join(str(fragment) for fragment in path)
    path_with_brackets = re.sub(
        r'(^|\.)(\d+)',
        r'[\2]',
        path_with_dots
    )
    return path_with_brackets


def default_literal_formatter(error):
    """Format literal value errors.

    :param error: Error to be formatted
    :type error: schemania.error.ValidationTypeError
    :returns: Error string representation
    :rtype: str

    """
    if len(error.path) == 0:
        return (
            'expected {!r}, but got {!r}'
            .format(error.validator.literal, error.data)
        )

    return (
        'expected {!r} in {!r}, but got {!r}'
        .format(
            error.validator.literal,
            _format_path(error.path),
            error.data,
        )
    )


def default_type_formatter(error):
    """Format type errors.

    :param error: Error to be formatted
    :type error: schemania.error.ValidationTypeError
    :returns: Error string representation
    :rtype: str

    """
    if len(error.path) == 0:
        return (
            'expected {!r}, but got {!r}'
            .format(error.validator.type.__name__, error.data)
        )

    return (
        'expected {!r} in {!r}, but got {!r}'
        .format(
            error.validator.type.__name__,
            _format_path(error.path),
            error.data,
        )
    )


def default_unknown_key_formatter(error):
    """Format unknown key errors.

    :param error: Error to be formatted
    :type error: schemania.error.ValidationUnknownKeyError
    :returns: Error string representation
    :rtype: str

    """
    if len(error.path) == 0:
        return 'unknown key {!r}'.format(error.key)

    return (
        'unknown key {!r} in {!r}'
        .format(error.key, _format_path(error.path))
    )


def default_missing_key_formatter(error):
    """Format missing key errors.

    :param error: Error to be formatted
    :type error: schemania.error.ValidationMissingKeyError
    :returns: Error string representation
    :rtype: str

    """
    if len(error.path) == 0:
        return 'missing key {!r}'.format(error.key_validator)

    return (
        'missing key {!r} in {!r}'
        .format(error.key_validator, _format_path(error.path))
    )


def default_multiple_formatter(error):
    """Format multiple errors.

    :param error: Error to be formatted
    :type error: schemania.error.MultipleError
    :returns: Error string representation
    :rtype: str

    """
    error_messages = '\n'.join([
        '- {}'.format(suberror)
        for suberror in error.errors
    ])
    if len(error.path) == 0:
        return 'multiple errors:\n{}'.format(error_messages)

    return (
        'multiple errors in {!r}:\n{}'
        .format(
            _format_path(error.path),
            error_messages,
        )
    )


def default_match_formatter(error):
    """Format match error.

    :param error: Error to be formatted
    :type error: schemania.error.MultipleError
    :returns: Error string representation
    :rtype: str

    """
    if len(error.path) == 0:
        return (
            'expected to match against regex {!r}, but got {!r}'
            .format(error.validator.regex.pattern, error.data)
        )

    return (
            'expected to match against regex {!r} in {!r}, but got {!r}'
            .format(
                error.validator.regex.pattern,
                _format_path(error.path),
                error.data,
            )
    )
