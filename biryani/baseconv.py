# -*- coding: utf-8 -*-


# Biryani -- A conversion and validation toolbox
# By: Emmanuel Raviart <eraviart@easter-eggs.com>
#
# Copyright (C) 2009, 2010, 2011 Easter-eggs
# http://packages.python.org/Biryani/
#
# This file is part of Biryani.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Base Conversion Functions

.. note:: Most converters do only one operation and can fail when given wrong data. To ensure that they don't fail, they
   must be combined with other converters.

.. note:: Most converters work on unicode strings. To use them you must first convert your strings to unicode. By using
   converter :func:`decode_str`, for example.
"""


import re

from . import states, strings


__all__ = [
    'bool_to_str',
    'clean_str_to_bool',
    'clean_str_to_email',
    'clean_str_to_json',
    'clean_str_to_slug',
    'clean_str_to_url',
    'clean_str_to_url_name',
    'clean_str_to_url_path_and_query',
    'cleanup_empty',
    'cleanup_line',
    'cleanup_text',
    'condition',
    'decode_str',
    'default',
    'dict_to_instance',
    'encode_str',
    'extract_when_singleton',
    'fail',
    'first_match',
    'function',
    'guess_bool',
    'guess_bool_default_false',
    'item_or_sequence',
    'mapping',
    'noop',
    'pipe',
    'python_data_to_bool',
    'python_data_to_float',
    'python_data_to_int',
    'python_data_to_str',
    'rename_item',
    'sequence',
    'set_value',
    'str_to_bool',
    'str_to_email',
    'str_to_float',
    'str_to_int',
    'str_to_json',
    'str_to_slug',
    'str_to_url',
    'str_to_url_name',
    'struct',
    'structured_mapping',
    'structured_sequence',
    'test',
    'test_between',
    'test_equals',
    'test_exists',
    'test_greater_or_equal',
    'test_in',
    'test_is',
    'test_isinstance',
    'test_less_or_equal',
    'to_value',
    'translate',
#    'uniform_mapping',
    'uniform_sequence',
    ]

domain_re = re.compile(r'''
    (?:[a-z0-9][a-z0-9\-]{0,62}\.)+ # (sub)domain - alpha followed by 62max chars (63 total)
    [a-z]{2,}$                      # TLD
    ''', re.I | re.VERBOSE)
html_id_re = re.compile(r'[A-Za-z][-A-Za-z0-9_:.]+$')
html_name_re = html_id_re
N_ = lambda s: s
username_re = re.compile(r"[^ \t\n\r@<>()]+$", re.I)


# Level-1 Converters


def bool_to_str(value, state = states.default_state):
    """Convert a boolean to a string.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> bool_to_str(False)
    (u'0', None)
    >>> bool_to_str(True)
    (u'1', None)
    >>> bool_to_str(0)
    (u'0', None)
    >>> bool_to_str('')
    (u'0', None)
    >>> bool_to_str('any non-empty string')
    (u'1', None)
    >>> bool_to_str('0')
    (u'1', None)
    >>> bool_to_str(None)
    (None, None)
    >>> pipe(default(False), bool_to_str)(None)
    (u'0', None)
    """
    if value is None:
        return value, None
    return unicode(int(bool(value))), None


def clean_str_to_bool(value, state = states.default_state):
    """Convert a clean string to a boolean.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_bool`.

    .. note:: For a converter that accepts special strings like "f", "off", "no", etc, see :func:`guess_bool`.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> clean_str_to_bool(u'0')
    (False, None)
    >>> clean_str_to_bool(u'1')
    (True, None)
    >>> clean_str_to_bool(None)
    (None, None)
    >>> clean_str_to_bool(u'vrai')
    (u'vrai', u'Value must be a boolean')
    >>> clean_str_to_bool(u'on')
    (u'on', u'Value must be a boolean')
    """
    if value is None:
        return value, None
    try:
        return bool(int(value)), None
    except ValueError:
        return value, state._(u'Value must be a boolean')


def clean_str_to_email(value, state = states.default_state):
    """Convert a clean string to an email address.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_email`.

    >>> clean_str_to_email(u'spam@easter-eggs.com')
    (u'spam@easter-eggs.com', None)
    >>> clean_str_to_email(u'mailto:spam@easter-eggs.com')
    (u'spam@easter-eggs.com', None)
    >>> clean_str_to_email(u'root@localhost')
    (u'root@localhost', None)
    >>> clean_str_to_email(u'root@127.0.0.1')
    (u'root@127.0.0.1', u'Invalid domain name')
    >>> clean_str_to_email(u'root')
    (u'root', u'An email must contain exactly one "@"')
    """
    if value is None:
        return value, None
    value = value.lower()
    if value.startswith(u'mailto:'):
        value = value.replace(u'mailto:', u'')
    try:
        username, domain = value.split('@', 1)
    except ValueError:
        return value, state._(u'An email must contain exactly one "@"')
    if not username_re.match(username):
        return value, state._(u'Invalid username')
    if not domain_re.match(domain) and domain != 'localhost':
        return value, state._(u'Invalid domain name')
    return value, None


def clean_str_to_json(value, state = states.default_state):
    """Convert a clean string to a JSON value.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_json`.

    .. note:: This converter uses module ``simplejson``  when it is available, or module ``json`` otherwise.

    >>> clean_str_to_json(u'{"a": 1, "b": 2}')
    ({u'a': 1, u'b': 2}, None)
    >>> clean_str_to_json(u'null')
    (None, None)
    >>> clean_str_to_json(None)
    (None, None)
    """
    if value is None:
        return value, None
    try:
        import simplejson as json
    except ImportError:
        import json
    if isinstance(value, str):
        # Ensure that json.loads() uses unicode strings.
        value = value.decode('utf-8')
    try:
        return json.loads(value), None
    except json.JSONDecodeError, e:
        return value, unicode(e)


def clean_str_to_slug(value, state = states.default_state):
    """Convert a clean string to a slug.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_slug`.

    >>> clean_str_to_slug(u'Hello world!')
    (u'hello-world', None)
    >>> clean_str_to_slug('Hello world!')
    (u'hello-world', None)
    >>> clean_str_to_slug(u'')
    (None, None)
    """
    if value is None:
        return value, None
    value = strings.slugify(value)
    return unicode(value) if value else None, None


def clean_str_to_url(add_prefix = u'http://', full = False, remove_fragment = False, schemes = (u'http', u'https')):
    """Return a converter that converts a clean string to an URL.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_url`.

    >>> clean_str_to_url()(u'http://packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> clean_str_to_url(full = True)(u'packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> clean_str_to_url()(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html#tutorial', None)
    >>> clean_str_to_url(full = True)(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html#tutorial', u'URL must be complete')
    >>> clean_str_to_url(remove_fragment = True)(u'http://packages.python.org/Biryani/presentation.html#tutorial')
    (u'http://packages.python.org/Biryani/presentation.html', None)
    """
    def clean_str_to_url_converter(value, state = states.default_state):
        if value is None:
            return value, None
        import urlparse
        split_url = list(urlparse.urlsplit(value))
        if full and add_prefix and not split_url[0] and not split_url[1] and split_url[2] \
                and not split_url[2].startswith(u'/'):
            split_url = list(urlparse.urlsplit(add_prefix + value))
        scheme = split_url[0]
        if scheme != scheme.lower():
            split_url[0] = scheme = scheme.lower()
        if full and not scheme:
            return value, state._(u'URL must be complete')
        if scheme and schemes is not None and scheme not in schemes:
            return value, state._(u'Scheme must belong to {0}').format(sorted(schemes))
        network_location = split_url[1]
        if network_location != network_location.lower():
            split_url[1] = network_location = network_location.lower()
        if scheme in (u'http', u'https') and not split_url[2]:
            # By convention a full HTTP URL must always have at least a "/" in its path.
            split_url[2] = u'/'
        if remove_fragment and split_url[4]:
            split_url[4] = u''
        return unicode(urlparse.urlunsplit(split_url)), None
    return clean_str_to_url_converter


def clean_str_to_url_name(value, state = states.default_state):
    """Convert a clean string to a normalized string that can be used in an URL path or a query parameter.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_url_name`.

    >>> clean_str_to_url_name(u'Hello world!')
    (u'hello_world!', None)
    >>> clean_str_to_url_name(u'')
    (None, None)
    """
    if value is None:
        return value, None
    for character in u'\n\r/?&#':
        value = value.replace(character, u' ')
    value = strings.normalize(value, separator = u'_')
    return value or None, None


def clean_str_to_url_path_and_query(value, state = states.default_state):
    """Convert a clean string to the path and query of an URL.

    >>> clean_str_to_url_path_and_query(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html', None)
    >>> clean_str_to_url_path_and_query(u'/Biryani/search.html?q=pipe')
    (u'/Biryani/search.html?q=pipe', None)
    >>> clean_str_to_url_path_and_query(u'http://packages.python.org/Biryani/search.html?q=pipe')
    (u'http://packages.python.org/Biryani/search.html?q=pipe', u'URL must not be complete')
    >>> import urlparse
    >>> pipe(
    ...     clean_str_to_url(),
    ...     function(lambda value: urlparse.urlunsplit([u'', u''] + list(urlparse.urlsplit(value))[2:])),
    ...     clean_str_to_url_path_and_query,
    ...     )(u'http://packages.python.org/Biryani/search.html?q=pipe')
    (u'/Biryani/search.html?q=pipe', None)
    """
    if value is None:
        return value, None
    import urlparse
    split_url = list(urlparse.urlsplit(value))
    if split_url[0] or split_url[1]:
        return value, state._(u'URL must not be complete')
    if split_url[4]:
        split_url[4] = ''
    return unicode(urlparse.urlunsplit(split_url)), None


def cleanup_empty(value, state = states.default_state):
    """When value is comparable to False (ie None, 0 , '', etc) replace it with None else keep it as is.

    >>> cleanup_empty(0)
    (None, None)
    >>> cleanup_empty('')
    (None, None)
    >>> cleanup_empty([])
    (None, None)
    >>> cleanup_empty({})
    (None, None)
    >>> cleanup_empty(u'hello world')
    (u'hello world', None)
    >>> cleanup_empty(u'   hello world   ')
    (u'   hello world   ', None)
    """
    return value if value else None, None


def condition(test_converter, ok_converter, error_converter = None):
    """When *test_converter* succeeds (ie no error), then apply *ok_converter*, otherwise apply *error_converter*.

    .. note:: See also :func:`first_match`.

    >>> detect_unknown_values = condition(
    ...     test_in(['?', 'x']),
    ...     set_value(False),
    ...     set_value(True),
    ...     )
    >>> detect_unknown_values(u'Hello world!')
    (True, None)
    >>> detect_unknown_values(u'?')
    (False, None)
    """
    def condition_converter(value, state = states.default_state):
        test, error = test_converter(value, state = state)
        if error is None:
            return ok_converter(value, state = state)
        elif error_converter is None:
            return value, None
        else:
            return error_converter(value, state = state)
    return condition_converter


def decode_str(encoding = 'utf-8'):
    """Return a string to unicode converter that uses given *encoding*.

    >>> decode_str()('   Hello world!   ')
    (u'   Hello world!   ', None)
    >>> decode_str()(u'   Hello world!   ')
    (u'   Hello world!   ', None)
    >>> decode_str()(42)
    (42, None)
    >>> decode_str()(None)
    (None, None)
    """
    return function(lambda value: value.decode(encoding) if isinstance(value, str) else value)


def default(constant):
    """Return a converter that replace a missing value (aka ``None``) by given one.

    >>> default(42)(None)
    (42, None)
    >>> default(42)(u'1234')
    (u'1234', None)
    >>> pipe(str_to_int, default(42))(u'1234')
    (1234, None)
    >>> pipe(str_to_int, default(42))(u'    ')
    (42, None)
    >>> pipe(str_to_int, default(42))(None)
    (42, None)
    """
    return lambda value, state = states.default_state: (constant, None) if value is None else (value, None)


def dict_to_instance(cls):
    """Return a converter that creates in instance of a class from a dictionary.

    >>> class C(object):
    ...     pass
    >>> dict_to_instance(C)(dict(a = 1, b = 2))
    (<C object at 0x...>, None)
    >>> c = to_value(dict_to_instance(C))(dict(a = 1, b = 2))
    >>> c.a, c.b
    (1, 2)
    >>> dict_to_instance(C)(None)
    (None, None)
    """
    def dict_to_instance_converter(value, state = states.default_state):
        if value is None:
            return value, None
        instance = cls()
        instance.__dict__ = value
        return instance, None
    return dict_to_instance_converter


def encode_str(encoding = 'utf-8'):
    """Return a unicode to string converter that uses given *encoding*.

    >>> encode_str()(u'   Hello world!   ')
    ('   Hello world!   ', None)
    >>> encode_str()('   Hello world!   ')
    ('   Hello world!   ', None)
    >>> encode_str()(42)
    (42, None)
    >>> encode_str()(None)
    (None, None)
    """
    return function(lambda value: value.encode(encoding) if isinstance(value, unicode) else value)


def fail(msg = N_(u'An error occured')):
    """Return a converter that always returns an error.

    >>> fail(u'Wrong answer')(42)
    (42, u'Wrong answer')
    >>> fail()(42)
    (42, u'An error occured')
    """
    def fail_converter(value, state = states.default_state):
        return value, state._(msg)
    return fail_converter


def first_match(*converters):
    """Try each converter successively until one succeeds. When every converter fail, return the result of the last one.

    >>> first_match(test_equals(u'NaN'), str_to_int)(u'NaN')
    (u'NaN', None)
    >>> first_match(test_equals(u'NaN'), str_to_int)(u'42')
    (42, None)
    >>> first_match(test_equals(u'NaN'), str_to_int)(u'abc')
    (u'abc', u'Value must be an integer')
    >>> first_match(test_equals(u'NaN'), str_to_int, set_value(0))(u'Hello world!')
    (0, None)
    >>> first_match()(u'Hello world!')
    (u'Hello world!', None)
    """
    def first_match_converter(value, state = states.default_state):
        convertered_value = value
        error = None
        for converter in converters:
            convertered_value, error = converter(value, state = state)
            if error is None:
                return convertered_value, error
        return convertered_value, error
    return first_match_converter


def function(function, handle_missing_value = False, handle_state = False):
    """Return a converter that applies a function to value and returns a new value.

    .. note:: Like most converters, by default a missing value (aka ``None``) is not converted (ie function is not
       called). Set ``handle_missing_value`` to ``True`` to call function when value is ``None``.

    .. note:: When your function doesn't modify value but may generate an error, use a :func:`test` instead.

    .. note:: When your function modifies value and may generate an error, write a full converter instead of a function.

    See :doc:`how-to-create-converter` for more informations.

    >>> function(int)('42')
    (42, None)
    >>> function(sorted)([3, 2, 1])
    ([1, 2, 3], None)
    >>> function(lambda value: value + 1)(42)
    (43, None)
    >>> function(lambda value: value + 1)(None)
    (None, None)
    >>> function(lambda value: value + 1)(u'hello world')
    Traceback (most recent call last):
    TypeError: coercing to Unicode: need string or buffer, int found
    >>> function(lambda value: value + 1, handle_missing_value = True)(None)
    Traceback (most recent call last):
    TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
    """
    def function_converter(value, state = states.default_state):
        if value is None and not handle_missing_value or function is None:
            return value, None
        if handle_state:
            return function(value, state = state), None
        return function(value), None
    return function_converter


def guess_bool(value, state = states.default_state):
    """Convert the content of a string (or a number) to a boolean. Do nothing when input value is already a boolean.

    This converter accepts usual values for ``True`` and ``False``: "0", "f", "false", "n", etc.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted. Use
       :func:`guess_bool_default_false` when you want ``None`` to be converted to ``False``.

    >>> guess_bool(u'0')
    (False, None)
    >>> guess_bool(u'f')
    (False, None)
    >>> guess_bool(u'FALSE')
    (False, None)
    >>> guess_bool(u'false')
    (False, None)
    >>> guess_bool(u'n')
    (False, None)
    >>> guess_bool(u'no')
    (False, None)
    >>> guess_bool(u'off')
    (False, None)
    >>> guess_bool(u'  0  ')
    (False, None)
    >>> guess_bool(u'  f  ')
    (False, None)
    >>> guess_bool(False)
    (False, None)
    >>> guess_bool(0)
    (False, None)
    >>> guess_bool(u'1')
    (True, None)
    >>> guess_bool(u'on')
    (True, None)
    >>> guess_bool(u't')
    (True, None)
    >>> guess_bool(u'TRUE')
    (True, None)
    >>> guess_bool(u'true')
    (True, None)
    >>> guess_bool(u'y')
    (True, None)
    >>> guess_bool(u'yes')
    (True, None)
    >>> guess_bool(u'  1  ')
    (True, None)
    >>> guess_bool(u'  tRuE  ')
    (True, None)
    >>> guess_bool(True)
    (True, None)
    >>> guess_bool(1)
    (True, None)
    >>> guess_bool(2)
    (True, None)
    >>> guess_bool(-1)
    (True, None)
    >>> guess_bool(u'')
    (None, None)
    >>> guess_bool(u'   ')
    (None, None)
    >>> guess_bool(None)
    (None, None)
    >>> guess_bool(u'vrai')
    (u'vrai', u'Value must be a boolean')
    """
    if value is None:
        return value, None
    try:
        return bool(int(value)), None
    except ValueError:
        lower_value = value.strip().lower()
        if not lower_value:
            return None, None
        if lower_value in (u'f', u'false', u'n', u'no', u'off'):
            return False, None
        if lower_value in (u'on', u't', u'true', u'y', u'yes'):
            return True, None
        return value, state._(u'Value must be a boolean')


def item_or_sequence(converter, constructor = list, keep_missing_items = False):
    """Return a converter that accepts either an item or a sequence of items and applies a converter to them.

    >>> item_or_sequence(str_to_int)(u'42')
    (42, None)
    >>> item_or_sequence(str_to_int)([u'42'])
    (42, None)
    >>> item_or_sequence(str_to_int)([u'42', u'43'])
    ([42, 43], None)
    >>> item_or_sequence(str_to_int)([u'42', u'43', u'Hello world!'])
    ([42, 43, u'Hello world!'], {2: u'Value must be an integer'})
    >>> item_or_sequence(str_to_int)([u'42', None, u'43'])
    ([42, 43], None)
    >>> item_or_sequence(str_to_int)([None, None])
    (None, None)
    >>> item_or_sequence(str_to_int, keep_missing_items = True)([None, None])
    ([None, None], None)
    >>> item_or_sequence(str_to_int, keep_missing_items = True)([u'42', None, u'43'])
    ([42, None, 43], None)
    >>> item_or_sequence(str_to_int, keep_missing_items = True)([u'42', u'43', u'Hello world!'])
    ([42, 43, u'Hello world!'], {2: u'Value must be an integer'})
    >>> item_or_sequence(str_to_int, constructor = set)(set([u'42', u'43']))
    (set([42, 43]), None)
    """
    return condition(
        test_isinstance(constructor),
        pipe(
            uniform_sequence(converter, constructor = constructor, keep_missing_items = keep_missing_items),
            extract_when_singleton,
            ),
        converter,
        )


def mapping(converters, constructor = dict, keep_empty = False, keep_missing_items = False):
    """Return a converter that constructs a mapping (ie dict, etc) from any kind of value.

    .. note:: Most of the times, when input value is also a mapping, converters :func:`uniform_mapping` or
       :func:`struct` should be used instead.

    >>> def get(index):
    ...     return function(lambda value: value[index])
    >>> def convert_list_to_dict(constructor = dict, keep_empty = False, keep_missing_items = False):
    ...     return mapping(
    ...         dict(
    ...             name = get(0),
    ...             age = pipe(get(1), str_to_int),
    ...             email = pipe(get(2), str_to_email),
    ...             ),
    ...         constructor = constructor,
    ...         keep_empty = keep_empty,
    ...         keep_missing_items = keep_missing_items,
    ...         )
    >>> convert_list_to_dict()([u'John Doe', u'72', u'spam@easter-eggs.com'])
    ({'age': 72, 'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> convert_list_to_dict()([u'John Doe', u'72'])
    Traceback (most recent call last):
    IndexError: list index out of range
    >>> convert_list_to_dict()([u'John Doe', u'72', None])
    ({'age': 72, 'name': u'John Doe'}, None)
    >>> convert_list_to_dict(keep_missing_items = True)([u'John Doe', u'72', None])
    ({'age': 72, 'email': None, 'name': u'John Doe'}, None)
    >>> convert_list_to_dict()([None, u' ', None])
    (None, None)
    >>> convert_list_to_dict(keep_empty = True)([None, u' ', None])
    ({}, None)
    >>> convert_list_to_dict()(None)
    (None, None)
    """
    converters = dict(
        (name, converter)
        for name, converter in (converters or {}).iteritems()
        if converter is not None
        )
    def mapping_converter(value, state = states.default_state):
        if value is None:
            return value, None
        errors = {}
        convertered_values = {}
        for name, converter in converters.iteritems():
            converted_value, error = converter(value, state = state)
            if converted_value is not None or keep_missing_items:
                convertered_values[name] = converted_value
            if error is not None:
                errors[name] = error
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return mapping_converter


def noop(value, state = states.default_state):
    """Return value as is.

    >>> noop(42)
    (42, None)
    >>> noop(None)
    (None, None)
    """
    return value, None


def pipe(*converters):
    """Return a compound converter that applies each of its converters till the end or an error occurs.

    >>> str_to_bool(42)
    Traceback (most recent call last):
    AttributeError: 'int' object has no attribute 'strip'
    >>> pipe(str_to_bool)(42)
    Traceback (most recent call last):
    AttributeError: 'int' object has no attribute 'strip'
    >>> pipe(test_isinstance(unicode), str_to_bool)(42)
    (42, u"Value is not an instance of <type 'unicode'>")
    >>> pipe(python_data_to_str, test_isinstance(unicode), str_to_bool)(42)
    (True, None)
    >>> pipe()(42)
    (42, None)
    """
    def pipe_converter(*args, **kwargs):
        if not converters:
            return noop(*args, **kwargs)
        state = kwargs.get('state', UnboundLocalError)
        for converter in converters:
            if converter is None:
                continue
            value, error = converter(*args, **kwargs)
            if error is not None:
                return value, error
            args = [value]
            kwargs = {}
            if state != UnboundLocalError:
                kwargs['state'] = state
        return value, None
    return pipe_converter


def python_data_to_float(value, state = states.default_state):
    """Convert any python data to a float.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> python_data_to_float(42)
    (42.0, None)
    >>> python_data_to_float('42')
    (42.0, None)
    >>> python_data_to_float(u'42')
    (42.0, None)
    >>> python_data_to_float(42.75)
    (42.75, None)
    >>> python_data_to_float(None)
    (None, None)
    """
    if value is None:
        return value, None
    try:
        return float(value), None
    except ValueError:
        return value, state._(u'Value must be a float')


def python_data_to_int(value, state = states.default_state):
    """Convert any python data to an integer.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> python_data_to_int(42)
    (42, None)
    >>> python_data_to_int('42')
    (42, None)
    >>> python_data_to_int(u'42')
    (42, None)
    >>> python_data_to_int(42.75)
    (42, None)
    >>> python_data_to_int(None)
    (None, None)
    """
    if value is None:
        return value, None
    try:
        return int(value), None
    except ValueError:
        return value, state._(u'Value must be an integer')


def python_data_to_str(value, state = states.default_state):
    """Convert any Python data to unicode.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> python_data_to_str(42)
    (u'42', None)
    >>> python_data_to_str('42')
    (u'42', None)
    >>> python_data_to_str(None)
    (None, None)
    """
    if value is None:
        return value, None
    if isinstance(value, str):
        return value.decode('utf-8'), None
    try:
        return unicode(value), None
    except UnicodeDecodeError:
        return str(value).decode('utf-8'), None


def rename_item(old_key, new_key):
    """Return a converter that renames a key in a mapping.

    >>> rename_item('a', 'c')(dict(a = 1, b = 2))
    ({'c': 1, 'b': 2}, None)
    >>> rename_item('c', 'd')(dict(a = 1, b = 2))
    ({'a': 1, 'b': 2}, None)
    >>> rename_item('c', 'd')(None)
    (None, None)
    """
    def rename_item_converter(value, state = states.default_state):
        if value is None:
            return value, None
        if old_key in value:
            value[new_key] = value.pop(old_key)
        return value, None
    return rename_item_converter


def sequence(converters, constructor = list, keep_empty = False, keep_missing_items = False):
    """Return a converter that constructs a sequence (ie list, tuple, etc) from any kind of value.

    .. note:: Most of the times, when input value is also a sequence, converters :func:`uniform_sequence` or
       :func:`struct` should be used instead.

    >>> def get(key):
    ...     return function(lambda value: value.get(key))
    >>> def convert_dict_to_list(constructor = list, keep_empty = False, keep_missing_items = False):
    ...     return sequence(
    ...         [
    ...             get('name'),
    ...             pipe(get('age'), str_to_int),
    ...             pipe(get('email'), str_to_email),
    ...             ],
    ...         constructor = constructor,
    ...         keep_empty = keep_empty,
    ...         keep_missing_items = keep_missing_items,
    ...         )
    >>> convert_dict_to_list()({'age': u'72', 'email': u'spam@easter-eggs.com', 'name': u'John Doe'})
    ([u'John Doe', 72, u'spam@easter-eggs.com'], None)
    >>> convert_dict_to_list(constructor = tuple)({'age': u'72', 'email': u'spam@easter-eggs.com', 'name': u'John Doe'})
    ((u'John Doe', 72, u'spam@easter-eggs.com'), None)
    >>> convert_dict_to_list()({'email': u'spam@easter-eggs.com', 'name': u'John Doe'})
    ([u'John Doe', u'spam@easter-eggs.com'], None)
    >>> convert_dict_to_list(keep_missing_items = True)({'email': u'spam@easter-eggs.com', 'name': u'John Doe'})
    ([u'John Doe', None, u'spam@easter-eggs.com'], None)
    >>> convert_dict_to_list()({})
    (None, None)
    >>> convert_dict_to_list(keep_empty = True)({})
    ([], None)
    >>> convert_dict_to_list()(None)
    (None, None)
    """
    converters = [
        converter
        for converter in converters or []
        if converter is not None
        ]
    def sequence_converter(value, state = states.default_state):
        if value is None:
            return value, None
        errors = {}
        convertered_values = []
        for i, converter in enumerate(converters):
            converted_value, error = converter(value, state = state)
            if converted_value is not None or keep_missing_items:
                convertered_values.append(converted_value)
            if error is not None:
                errors[i] = error
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return sequence_converter


def set_value(constant):
    """Return a converter that replaces any non-null value by given one.

    .. note:: This is the opposite behaviour of func:`default`.

    >>> set_value(42)(u'Answer to the Ultimate Question of Life, the Universe, and Everything')
    (42, None)
    >>> set_value(42)(None)
    (None, None)
    """
    return lambda value, state = states.default_state: (constant, None) if value is not None else (None, None)


def str_to_url(add_prefix = u'http://', full = False, remove_fragment = False, schemes = (u'http', u'https')):
    """Return a converter that converts an string to an URL.

    >>> str_to_url()(u'http://packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> str_to_url(full = True)(u'packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> str_to_url()(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html#tutorial', None)
    >>> str_to_url(full = True)(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html#tutorial', u'URL must be complete')
    >>> str_to_url(remove_fragment = True)(u'http://packages.python.org/Biryani/presentation.html#tutorial')
    (u'http://packages.python.org/Biryani/presentation.html', None)
    >>> str_to_url()(u'    http://packages.python.org/Biryani/   ')
    (u'http://packages.python.org/Biryani/', None)
    """
    return pipe(
        cleanup_line,
        clean_str_to_url(add_prefix = add_prefix, full = full, remove_fragment = remove_fragment,
            schemes = schemes),
        )


def struct(converters, constructor = None, default = None, keep_empty = False):
    """Return a converter that maps a collection of converters to a collection (ie dict, list, set, etc) of values.

    Usage to convert a mapping (ie dict, etc):

    >>> strict_converter = struct(dict(
    ...     name = pipe(cleanup_line, test_exists),
    ...     age = str_to_int,
    ...     email = str_to_email,
    ...     ))
    ...
    >>> strict_converter(dict(name = u'John Doe', age = u'72', email = u'spam@easter-eggs.com'))
    ({'age': 72, 'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', email = u'spam@easter-eggs.com'))
    ({'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', age = None, email = u'spam@easter-eggs.com'))
    ({'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', age = u'72', phone = u'   +33 9 12 34 56 78   '))
    ({'phone': u'   +33 9 12 34 56 78   ', 'age': 72, 'name': u'John Doe'}, {'phone': u'Unexpected item'})
    >>> non_strict_converter = struct(
    ...     dict(
    ...         name = pipe(cleanup_line, test_exists),
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     )
    ...
    >>> non_strict_converter(dict(name = u'John Doe', age = u'72', email = u'spam@easter-eggs.com'))
    ({'age': 72, 'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> non_strict_converter(dict(name = u'John Doe', email = u'spam@easter-eggs.com'))
    ({'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> non_strict_converter(dict(name = u'John Doe', age = u'72', email = u'spam@easter-eggs.com',
    ...     phone = u'   +33 9 12 34 56 78   '))
    ({'phone': u'+33 9 12 34 56 78', 'age': 72, 'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> struct(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     )(dict(name = u'   ', email = None))
    (None, None)
    >>> struct(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     keep_empty = True,
    ...     )(dict(name = u'   ', email = None))
    ({}, None)

    Usage to convert a sequence (ie list, tuple, etc) or a set:

    >>> strict_converter = struct([
    ...     pipe(cleanup_line, test_exists),
    ...     str_to_int,
    ...     str_to_email,
    ...     ])
    ...
    >>> strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com'])
    ([u'John Doe', 72, u'spam@easter-eggs.com'], None)
    >>> strict_converter([u'John Doe', u'spam@easter-eggs.com'])
    ([u'John Doe', u'spam@easter-eggs.com', None], {1: u'Value must be an integer'})
    >>> strict_converter([u'John Doe', None, u'spam@easter-eggs.com'])
    ([u'John Doe', None, u'spam@easter-eggs.com'], None)
    >>> strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com', u'   +33 9 12 34 56 78   '])
    ([u'John Doe', 72, u'spam@easter-eggs.com', u'   +33 9 12 34 56 78   '], {3: u'Unexpected item'})
    >>> non_strict_converter = struct(
    ...     [
    ...         pipe(cleanup_line, test_exists),
    ...         str_to_int,
    ...         str_to_email,
    ...         ],
    ...     default = cleanup_line,
    ...     )
    ...
    >>> non_strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com'])
    ([u'John Doe', 72, u'spam@easter-eggs.com'], None)
    >>> non_strict_converter([u'John Doe', u'spam@easter-eggs.com'])
    ([u'John Doe', u'spam@easter-eggs.com', None], {1: u'Value must be an integer'})
    >>> non_strict_converter([u'John Doe', None, u'spam@easter-eggs.com'])
    ([u'John Doe', None, u'spam@easter-eggs.com'], None)
    >>> non_strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com', u'   +33 9 12 34 56 78   '])
    ([u'John Doe', 72, u'spam@easter-eggs.com', u'+33 9 12 34 56 78'], None)
    """
    import collections

    if isinstance(converters, collections.Mapping):
        return structured_mapping(converters, constructor = constructor or dict, default = default,
            keep_empty = keep_empty)
    assert isinstance(converters, collections.Sequence), \
            'Converters must be a mapping or a sequence. Got {0} instead.'.format(type(converters))
    return structured_sequence(converters, constructor = constructor or list, default = default,
        keep_empty = keep_empty)


def structured_mapping(converters, constructor = dict, default = None, keep_empty = False):
    """Return a converter that maps a mapping of converters to a mapping (ie dict, etc) of values.

    .. note:: This converter should not be used directly. Use :func:`struct` instead.

    >>> strict_converter = structured_mapping(dict(
    ...     name = pipe(cleanup_line, test_exists),
    ...     age = str_to_int,
    ...     email = str_to_email,
    ...     ))
    ...
    >>> strict_converter(dict(name = u'John Doe', age = u'72', email = u'spam@easter-eggs.com'))
    ({'age': 72, 'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', email = u'spam@easter-eggs.com'))
    ({'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', age = None, email = u'spam@easter-eggs.com'))
    ({'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', age = u'72', phone = u'   +33 9 12 34 56 78   '))
    ({'phone': u'   +33 9 12 34 56 78   ', 'age': 72, 'name': u'John Doe'}, {'phone': u'Unexpected item'})
    >>> non_strict_converter = structured_mapping(
    ...     dict(
    ...         name = pipe(cleanup_line, test_exists),
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     )
    ...
    >>> non_strict_converter(dict(name = u'John Doe', age = u'72', email = u'spam@easter-eggs.com'))
    ({'age': 72, 'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> non_strict_converter(dict(name = u'John Doe', email = u'spam@easter-eggs.com'))
    ({'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> non_strict_converter(dict(name = u'John Doe', age = u'72', email = u'spam@easter-eggs.com',
    ...     phone = u'   +33 9 12 34 56 78   '))
    ({'phone': u'+33 9 12 34 56 78', 'age': 72, 'email': u'spam@easter-eggs.com', 'name': u'John Doe'}, None)
    >>> structured_mapping(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     )(dict(name = u'   ', email = None))
    (None, None)
    >>> structured_mapping(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     keep_empty = True,
    ...     )(dict(name = u'   ', email = None))
    ({}, None)
    """
    converters = dict(
        (name, converter)
        for name, converter in (converters or {}).iteritems()
        if converter is not None
        )
    def structured_mapping_converter(values, state = states.default_state):
        if values is None:
            return values, None
        if default == 'ignore':
            values_converter = converters
        else:
            values_converter = converters.copy()
            for name in values:
                if name not in values_converter:
                    values_converter[name] = default if default is not None else fail(N_(u'Unexpected item'))
        errors = {}
        convertered_values = {}
        for name, converter in values_converter.iteritems():
            value, error = converter(values.get(name), state = state)
            if value is not None:
                convertered_values[name] = value
            if error is not None:
                errors[name] = error
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return structured_mapping_converter


def structured_sequence(converters, constructor = list, default = None, keep_empty = False):
    """Return a converter that map a sequence of converters to a sequence of values.

    .. note:: This converter should not be used directly. Use :func:`struct` instead.

    >>> strict_converter = structured_sequence([
    ...     pipe(cleanup_line, test_exists),
    ...     str_to_int,
    ...     str_to_email,
    ...     ])
    ...
    >>> strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com'])
    ([u'John Doe', 72, u'spam@easter-eggs.com'], None)
    >>> strict_converter([u'John Doe', u'spam@easter-eggs.com'])
    ([u'John Doe', u'spam@easter-eggs.com', None], {1: u'Value must be an integer'})
    >>> strict_converter([u'John Doe', None, u'spam@easter-eggs.com'])
    ([u'John Doe', None, u'spam@easter-eggs.com'], None)
    >>> strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com', u'   +33 9 12 34 56 78   '])
    ([u'John Doe', 72, u'spam@easter-eggs.com', u'   +33 9 12 34 56 78   '], {3: u'Unexpected item'})
    >>> non_strict_converter = structured_sequence(
    ...     [
    ...         pipe(cleanup_line, test_exists),
    ...         str_to_int,
    ...         str_to_email,
    ...         ],
    ...     default = cleanup_line,
    ...     )
    ...
    >>> non_strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com'])
    ([u'John Doe', 72, u'spam@easter-eggs.com'], None)
    >>> non_strict_converter([u'John Doe', u'spam@easter-eggs.com'])
    ([u'John Doe', u'spam@easter-eggs.com', None], {1: u'Value must be an integer'})
    >>> non_strict_converter([u'John Doe', None, u'spam@easter-eggs.com'])
    ([u'John Doe', None, u'spam@easter-eggs.com'], None)
    >>> non_strict_converter([u'John Doe', u'72', u'spam@easter-eggs.com', u'   +33 9 12 34 56 78   '])
    ([u'John Doe', 72, u'spam@easter-eggs.com', u'+33 9 12 34 56 78'], None)
    """
    converters = [
        converter
        for converter in converters or []
        if converter is not None
        ]
    def structured_sequence_converter(values, state = states.default_state):
        if values is None:
            return values, None
        if default == 'ignore':
            values_converter = converters
        else:
            values_converter = converters[:]
            while len(values) > len(values_converter):
                values_converter.append(default if default is not None else fail(N_(u'Unexpected item')))
        import itertools
        errors = {}
        convertered_values = []
        for i, (converter, value) in enumerate(itertools.izip_longest(
                values_converter, itertools.islice(values, len(values_converter)))):
            value, error = converter(value, state = state)
            convertered_values.append(value)
            if error is not None:
                errors[i] = error
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return structured_sequence_converter


def test(function, error = N_(u'Test failed'), handle_missing_value = False, handle_state = False):
    """Return a converter that applies a test function to a value and returns an error when test fails.

    ``test`` always returns the initial value, even when test fails.

     See :doc:`how-to-create-converter` for more informations.

    >>> test(lambda value: isinstance(value, basestring))('hello')
    ('hello', None)
    >>> test(lambda value: isinstance(value, basestring))(1)
    (1, u'Test failed')
    >>> test(lambda value: isinstance(value, basestring), error = u'Value is not a string')(1)
    (1, u'Value is not a string')
    """
    def test_converter(value, state = states.default_state):
        if value is None and not handle_missing_value or function is None:
            return value, None
        ok = function(value, state = state) if handle_state else function(value)
        if ok:
            return value, None
        return value, state._(error)
    return test_converter


def test_between(min_value, max_value, error = None):
    """Return a converter that accepts only values between the two given bounds (included).

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared.

    >>> test_between(0, 9)(5)
    (5, None)
    >>> test_between(0, 9)(0)
    (0, None)
    >>> test_between(0, 9)(9)
    (9, None)
    >>> test_between(0, 9)(10)
    (10, u'Value must be between 0 and 9')
    >>> test_between(0, 9, error = u'Number must be a digit')(10)
    (10, u'Number must be a digit')
    >>> test_between(0, 9)(None)
    (None, None)
    """
    return test(lambda value: min_value <= value <= max_value,
        error = error or N_(u'Value must be between {0} and {1}').format(min_value, max_value))


def test_equals(constant, error = None):
    """Return a converter that accepts only values equals to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared. Furthermore, when *constant* is
       ``None``, value is never compared.

    >>> test_equals(42)(42)
    (42, None)
    >>> test_equals(dict(a = 1, b = 2))(dict(a = 1, b = 2))
    ({'a': 1, 'b': 2}, None)
    >>> test_equals(41)(42)
    (42, u'Value must be equal to 41')
    >>> test_equals(41, error = u'Value is not the answer')(42)
    (42, u'Value is not the answer')
    >>> test_equals(None)(42)
    (42, None)
    >>> test_equals(42)(None)
    (None, None)
    """
    return test(lambda value: value == constant if constant is not None else True,
        error = error or N_(u'Value must be equal to {0}').format(constant))


def test_exists(value, state = states.default_state):
    """Return an error when value is missing (aka ``None``).

    >>> test_exists(42)
    (42, None)
    >>> test_exists(u'')
    (u'', None)
    >>> test_exists(None)
    (None, u'Missing value')
    """
    if value is None:
        return value, state._(u'Missing value')
    else:
        return value, None


def test_greater_or_equal(constant, error = None):
    """Return a converter that accepts only values greater than or equal to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared.

    >>> test_greater_or_equal(0)(5)
    (5, None)
    >>> test_greater_or_equal(9)(5)
    (5, u'Value must be greater than or equal to 9')
    >>> test_greater_or_equal(9, error = u'Value must be a positive two-digits number')(5)
    (5, u'Value must be a positive two-digits number')
    >>> test_greater_or_equal(9)(None)
    (None, None)
    >>> test_greater_or_equal(None)(5)
    (5, None)
    """
    return test(lambda value: (value >= constant) if constant is not None else True,
        error = error or N_(u'Value must be greater than or equal to {0}').format(constant))


def test_in(values, error = None):
    """Return a converter that accepts only values belonging to a given set (or list or...).

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared. Furthermore, when *values* is
       ``None``, value is never compared.

    >>> test_in('abcd')('a')
    ('a', None)
    >>> test_in(['a', 'b', 'c', 'd'])('a')
    ('a', None)
    >>> test_in(['a', 'b', 'c', 'd'])('z')
    ('z', u"Value must be one of ['a', 'b', 'c', 'd']")
    >>> test_in(['a', 'b', 'c', 'd'], error = u'Value must be a letter less than "e"')('z')
    ('z', u'Value must be a letter less than "e"')
    >>> test_in([])('z')
    ('z', u'Value must be one of []')
    >>> test_in(None)('z')
    ('z', None)
    >>> test_in(['a', 'b', 'c', 'd'])(None)
    (None, None)
    """
    return test(lambda value: value in values if values is not None else True,
        error = error or N_(u'Value must be one of {0}').format(values))


def test_is(constant, error = None):
    """Return a converter that accepts only values that are strictly equal to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared. Furthermore, when *constant* is
       ``None``, value is never compared.

    >>> test_is(42)(42)
    (42, None)
    >>> test_is(dict(a = 1, b = 2))(dict(a = 1, b = 2))
    ({'a': 1, 'b': 2}, u"Value must be {'a': 1, 'b': 2}")
    >>> test_is(41)(42)
    (42, u'Value must be 41')
    >>> test_is(41, error = u'Value is not the answer')(42)
    (42, u'Value is not the answer')
    >>> test_is(None)(42)
    (42, None)
    >>> test_is(42)(None)
    (None, None)
    """
    return test(lambda value: value is constant if constant is not None else True,
        error = error or N_(u'Value must be {0}').format(constant))


def test_isinstance(class_or_classes, error = None):
    """Return a converter that accepts only an instance of given class (or tuple of classes).

    >>> test_isinstance(basestring)('This is a string')
    ('This is a string', None)
    >>> test_isinstance(basestring)(42)
    (42, u"Value is not an instance of <type 'basestring'>")
    >>> test_isinstance(basestring, error = u'Value is not a string')(42)
    (42, u'Value is not a string')
    >>> test_isinstance((float, int))(42)
    (42, None)
    """
    return test(lambda value: isinstance(value, class_or_classes),
        error = error or N_(u'Value is not an instance of {0}').format(class_or_classes))


def test_less_or_equal(constant, error = None):
    """Return a converter that accepts only values less than or equal to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared.

    >>> test_less_or_equal(9)(5)
    (5, None)
    >>> test_less_or_equal(0)(5)
    (5, u'Value must be less than or equal to 0')
    >>> test_less_or_equal(0, error = u'Value must be negative')(5)
    (5, u'Value must be negative')
    >>> test_less_or_equal(9)(None)
    (None, None)
    >>> test_less_or_equal(None)(5)
    (5, None)
    """
    return test(lambda value: (value <= constant) if constant is not None else True,
        error = error or N_(u'Value must be less than or equal to {0}').format(constant))


def translate(conversions):
    """Return a converter that converts values found in given dictionary and keep others as is.

    .. warning:: Like most converters, a missing value (aka ``None``) is not handled => It is never translated.

    >>> translate({0: u'bad', 1: u'OK'})(0)
    (u'bad', None)
    >>> translate({0: u'bad', 1: u'OK'})(1)
    (u'OK', None)
    >>> translate({0: u'bad', 1: u'OK'})(2)
    (2, None)
    >>> translate({0: u'bad', 1: u'OK'})(u'three')
    (u'three', None)
    >>> translate({None: u'problem', 0: u'bad', 1: u'OK'})(None)
    (None, None)
    >>> pipe(translate({0: u'bad', 1: u'OK'}), default(u'no problem'))(None)
    (u'no problem', None)
    """
    return function(lambda value: value
        if value is None or conversions is None or value not in conversions
        else conversions[value])


#def uniform_mapping(key_converter, value_converter, constructor = dict, keep_empty = False, keep_missing_keys = False,
#        keep_missing_values = False):
#    """Return a converter that applies a unique converter to each key and another unique converter to each value of a mapping."""
#    def uniform_mapping_converter(values, state = states.default_state):
#        if values is None:
#            return values, None
#        errors = {}
#        convertered_values = {}
#        for key, value in values.iteritems():
#            key, error = key_converter(key, state = state)
#            if error is not None:
#                errors[key] = error
#            if key is None and not keep_missing_keys:
#                continue
#            value, error = value_converter(value, state = state)
#            if value is not None or keep_missing_values:
#                convertered_values[key] = value
#            if error is not None:
#                errors[key] = error
#        if keep_empty or convertered_values:
#            convertered_values = constructor(convertered_values)
#        else:
#            convertered_values = None
#        return convertered_values, errors or None
#    return uniform_mapping_converter


def uniform_sequence(converter, constructor = list, keep_empty = False, keep_missing_items = False):
    """Return a converter that applies the same converter to each value of a list.

    >>> uniform_sequence(str_to_int)([u'42'])
    ([42], None)
    >>> uniform_sequence(str_to_int)([u'42', u'43'])
    ([42, 43], None)
    >>> uniform_sequence(str_to_int)([u'42', u'43', u'Hello world!'])
    ([42, 43, u'Hello world!'], {2: u'Value must be an integer'})
    >>> uniform_sequence(str_to_int)([u'42', None, u'43'])
    ([42, 43], None)
    >>> uniform_sequence(str_to_int)([None, None])
    (None, None)
    >>> uniform_sequence(str_to_int, keep_empty = True)([None, None])
    ([], None)
    >>> uniform_sequence(str_to_int, keep_empty = True, keep_missing_items = True)([None, None])
    ([None, None], None)
    >>> uniform_sequence(str_to_int, keep_missing_items = True)([u'42', None, u'43'])
    ([42, None, 43], None)
    >>> uniform_sequence(str_to_int, keep_missing_items = True)([u'42', u'43', u'Hello world!'])
    ([42, 43, u'Hello world!'], {2: u'Value must be an integer'})
    >>> uniform_sequence(str_to_int, constructor = set)(set([u'42', u'43']))
    (set([42, 43]), None)
    """
    def uniform_sequence_converter(values, state = states.default_state):
        if values is None:
            return values, None
        errors = {}
        convertered_values = []
        for i, value in enumerate(values):
            value, error = converter(value, state = state)
            if keep_missing_items or value is not None:
                convertered_values.append(value)
            if error is not None:
                errors[i] = error
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return uniform_sequence_converter


# Level-2 Converters


cleanup_line = pipe(
    function(lambda value: value.strip()),
    cleanup_empty,
    )
"""Strip spaces from a string and remove it when empty.

    >>> cleanup_line(u'   Hello world!   ')
    (u'Hello world!', None)
    >>> cleanup_line('   ')
    (None, None)
    >>> cleanup_line(None)
    (None, None)
    """

cleanup_text = pipe(
    function(lambda value: value.replace(u'\r\n', u'\n').replace(u'\r', u'\n')),
    cleanup_line,
    )
"""Replaces CR + LF or CR to LF in a string, then strip spaces and remove it when empty.

    >>> cleanup_text(u'   Hello\\r\\n world!\\r   ')
    (u'Hello\\n world!', None)
    >>> cleanup_text('   ')
    (None, None)
    >>> cleanup_text(None)
    (None, None)
    """

extract_when_singleton = condition(
    test(lambda value: len(value) == 1 and not isinstance(value[0], (list, set, tuple))),
    function(lambda value: list(value)[0]),
    )
"""Extract first item of sequence when it is a singleton and it is not itself a sequence, otherwise keep it unchanged.

    >>> extract_when_singleton([42])
    (42, None)
    >>> extract_when_singleton([42, 43])
    ([42, 43], None)
    >>> extract_when_singleton([])
    ([], None)
    >>> extract_when_singleton(None)
    (None, None)
    >>> extract_when_singleton([[42]])
    ([[42]], None)
"""


# Level-3 Converters


guess_bool_default_false = pipe(guess_bool, default(False))
"""Convert the content of a string (or a number) to a boolean. Do nothing when input value is already a boolean.

    This converter accepts usual values for ``True`` and ``False``: "0", "f", "false", "n", etc.

    .. warning:: Unlike most converters, a missing value (aka ``None``) is converted (to ``False``). Use
       :func:`guess_bool` when you don't want to keep ``None`` instead of converting it to ``False``.

    >>> guess_bool_default_false(u'0')
    (False, None)
    >>> guess_bool_default_false(u'f')
    (False, None)
    >>> guess_bool_default_false(u'FALSE')
    (False, None)
    >>> guess_bool_default_false(u'false')
    (False, None)
    >>> guess_bool_default_false(u'n')
    (False, None)
    >>> guess_bool_default_false(u'no')
    (False, None)
    >>> guess_bool_default_false(u'off')
    (False, None)
    >>> guess_bool_default_false(u'  0  ')
    (False, None)
    >>> guess_bool_default_false(u'  f  ')
    (False, None)
    >>> guess_bool_default_false(u'')
    (False, None)
    >>> guess_bool_default_false(u'   ')
    (False, None)
    >>> guess_bool_default_false(False)
    (False, None)
    >>> guess_bool_default_false(0)
    (False, None)
    >>> guess_bool_default_false(u'1')
    (True, None)
    >>> guess_bool_default_false(u'on')
    (True, None)
    >>> guess_bool_default_false(u't')
    (True, None)
    >>> guess_bool_default_false(u'TRUE')
    (True, None)
    >>> guess_bool_default_false(u'true')
    (True, None)
    >>> guess_bool_default_false(u'y')
    (True, None)
    >>> guess_bool_default_false(u'yes')
    (True, None)
    >>> guess_bool_default_false(u'  1  ')
    (True, None)
    >>> guess_bool_default_false(u'  tRuE  ')
    (True, None)
    >>> guess_bool_default_false(True)
    (True, None)
    >>> guess_bool_default_false(1)
    (True, None)
    >>> guess_bool_default_false(2)
    (True, None)
    >>> guess_bool_default_false(-1)
    (True, None)
    >>> guess_bool_default_false(None)
    (False, None)
    >>> guess_bool_default_false(u'vrai')
    (u'vrai', u'Value must be a boolean')
"""

python_data_to_bool = function(lambda value: bool(value))
"""Convert any Python data to a boolean.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> python_data_to_bool(0)
    (False, None)
    >>> python_data_to_bool(-1)
    (True, None)
    >>> python_data_to_bool(u'0')
    (True, None)
    >>> python_data_to_bool(u'1')
    (True, None)
    >>> python_data_to_bool(u'true')
    (True, None)
    >>> python_data_to_bool(u'false')
    (True, None)
    >>> python_data_to_bool(u'  0  ')
    (True, None)
    >>> python_data_to_bool(u'    ')
    (True, None)
    >>> python_data_to_bool(None)
    (None, None)
    """

str_to_bool = pipe(cleanup_line, clean_str_to_bool)
"""Convert a string to a boolean.

    Like most converters, a missing value (aka ``None``) is not converted.

    >>> str_to_bool(u'0')
    (False, None)
    >>> str_to_bool(u'   0   ')
    (False, None)
    >>> str_to_bool(u'1')
    (True, None)
    >>> str_to_bool(u'   1   ')
    (True, None)
    >>> str_to_bool(None)
    (None, None)
    >>> str_to_bool(u'vrai')
    (u'vrai', u'Value must be a boolean')
    >>> str_to_bool(u'on')
    (u'on', u'Value must be a boolean')
"""

str_to_email = pipe(cleanup_line, clean_str_to_email)
"""Convert a string to an email address.

    >>> str_to_email(u'spam@easter-eggs.com')
    (u'spam@easter-eggs.com', None)
    >>> str_to_email(u'mailto:spam@easter-eggs.com')
    (u'spam@easter-eggs.com', None)
    >>> str_to_email(u'root@localhost')
    (u'root@localhost', None)
    >>> str_to_email('root@127.0.0.1')
    ('root@127.0.0.1', u'Invalid domain name')
    >>> str_to_email(u'root')
    (u'root', u'An email must contain exactly one "@"')
    >>> str_to_email(u'    spam@easter-eggs.com  ')
    (u'spam@easter-eggs.com', None)
    >>> str_to_email(None)
    (None, None)
    >>> str_to_email(u'    ')
    (None, None)
    """

str_to_float = pipe(cleanup_line, python_data_to_float)
"""Convert a string to float.

    >>> str_to_float('42')
    (42.0, None)
    >>> str_to_float(u'   42.25   ')
    (42.25, None)
    >>> str_to_float(u'hello world')
    (u'hello world', u'Value must be a float')
    >>> str_to_float(None)
    (None, None)
    """


str_to_int = pipe(cleanup_line, python_data_to_int)
"""Convert a string to an integer.

    >>> str_to_int('42')
    (42, None)
    >>> str_to_int(u'   42   ')
    (42, None)
    >>> str_to_int(u'42.75')
    (u'42.75', u'Value must be an integer')
    >>> str_to_int(None)
    (None, None)
    """

str_to_json = pipe(cleanup_line, clean_str_to_json)
"""Convert a string to a JSON value.

    .. note:: This converter uses module ``simplejson``  when it is available, or module ``json`` otherwise.

    >>> str_to_json(u'{"a": 1, "b": 2}')
    ({u'a': 1, u'b': 2}, None)
    >>> str_to_json(u'null')
    (None, None)
    >>> str_to_json(u'   {"a": 1, "b": 2}    ')
    ({u'a': 1, u'b': 2}, None)
    >>> str_to_json(None)
    (None, None)
    >>> str_to_json(u'    ')
    (None, None)
    """

str_to_slug = pipe(cleanup_line, clean_str_to_slug)
"""Convert a string to a slug.

    >>> str_to_slug(u'   Hello world!   ')
    (u'hello-world', None)
    >>> clean_str_to_slug('   Hello world!   ')
    (u'hello-world', None)
    >>> str_to_slug(u'')
    (None, None)
    """

str_to_url_name = pipe(cleanup_line, clean_str_to_url_name)
"""Convert a string to a normalized string that can be used in an URL path or a query parameter.

    >>> str_to_url_name(u'   Hello world!   ')
    (u'hello_world!', None)
    >>> str_to_url_name(u'')
    (None, None)
    """


# Utility Functions


def to_value(converter, clear_on_error = False):
    """Return a function that calls given converter and returns its result or raises an exception when an error occurs.

    When *clear_on_error* is ``True``, return None instead of raising and exception.

    >>> to_value(str_to_int)(u'42')
    42
    >>> to_value(str_to_int)(u'hello world')
    Traceback (most recent call last):
    ValueError: Value must be an integer
    >>> to_value(pipe(python_data_to_str, test_isinstance(unicode), str_to_bool))(42)
    True
    >>> to_value(str_to_int, clear_on_error = True)(u'42')
    42
    >>> to_value(str_to_int, clear_on_error = True)(u'hello world')
    """
    def to_value_converter(*args, **kwargs):
        value, error = converter(*args, **kwargs)
        if error is not None:
            if clear_on_error:
                return None
            raise ValueError(error)
        return value
    return to_value_converter

