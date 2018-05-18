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
        r'\.?(\d+)',
        r'[\1]',
        path_with_dots
    )
    return path_with_brackets


def default_type_formatter(error):
    """Format type errors.

    :param error: Error to be formated
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
        "expected {!r} in {!r}, but got {!r}"
        .format(
            error.validator.type.__name__,
            _format_path(error.path),
            error.data,
        )
    )


def default_multiple_formatter(error):
    """Format multiple errors.

    :param error: Error to be formated
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
