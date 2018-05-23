"""Formatters.

Formatters are the objects that are used to transform an error in to a text
representation to the user. There's a default implementatio of all the error
classes supported, but it's also possible to create custom ones and overwrite
the default behavior.

"""


def _format_path(path):
    """Format path to data for which an error was found.

    :param path: Path as a list of keys/indexes used to get to a piece of data
    :type path: collections.deque[str|int]
    :returns: String representation of a given path
    :rtype: str

    """
    path_with_brackets = (
        ''.join('[{!r}]'.format(fragment) for fragment in path)
    )
    return '{}'.format(path_with_brackets)


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
        'expected {!r} in {}, but got {!r}'
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
        'expected {!r} in {}, but got {!r}'
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
        'unknown key {!r} in {}'
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
        return 'missing key {}'.format(error.key_validator)

    return (
        'missing key {} in {}'
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
        'multiple errors in {}:\n{}'
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
            'expected to match against regex {!r} in {}, but got {!r}'
            .format(
                error.validator.regex.pattern,
                _format_path(error.path),
                error.data,
            )
    )


def default_function_formatter(error):
    """Format function error.

    :param error: Error to be formatted
    :type error: schemania.error.FunctionError
    :returns: Error string representation
    :rtype: str

    """
    if len(error.path) == 0:
        return (
            'error calling {!r} with data {!r}'
            .format(error.validator.func.__name__, error.data)
        )

    return (
        'error calling {!r} in {} with data {!r}'
        .format(
            error.validator.func.__name__,
            _format_path(error.path),
            error.data,
        )
    )


def default_length_formatter(error):
    """Format length error.

    :param error: Error to be formatted
    :type error: schemania.error.FunctionError
    :returns: Error string representation
    :rtype: str

    """
    if len(error.path) == 0:
        if error.validator.max_length is None:
            return (
                'length must be greater than {!r}, got {!r}'
                .format(error.validator.min_length, error.data)
            )

        if error.validator.min_length is None:
            return (
                'length must be less than {!r}, got {!r}'
                .format(error.validator.max_length, error.data)
            )

        return (
            'length must be between {!r} and {!r}, got {!r}'
            .format(
                error.validator.min_length,
                error.validator.max_length,
                error.data,
            )
        )

    if error.validator.max_length is None:
        return (
            'length must be greater than {!r} in {}, got {!r}'
            .format(
                error.validator.min_length,
                _format_path(error.path),
                error.data,
            )
        )

    if error.validator.min_length is None:
        return (
            'length must be less than {!r} in {}, got {!r}'
            .format(
                error.validator.max_length,
                _format_path(error.path),
                error.data,
            )
        )

    return (
        'length must be between {!r} and {!r} in {}, got {!r}'
        .format(
            error.validator.min_length,
            error.validator.max_length,
            _format_path(error.path),
            error.data,
        )
    )
