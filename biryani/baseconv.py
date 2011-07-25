# -*- coding: utf-8 -*-


# Biryani -- A conversion and validation toolbox
# By: Emmanuel Raviart <eraviart@easter-eggs.com>
#
# Copyright (C) 2009, 2010, 2011 Easter-eggs
# http://packages.python.org/biryani/
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


"""Conversion functions

Most converters do only one operation and can fail when given wrong data. To ensure that they don't fail, they must be
combined with other converters.
"""


import itertools
import re

from . import states


domain_re = re.compile(r'''
    (?:[a-z0-9][a-z0-9\-]{0,62}\.)+ # (sub)domain - alpha followed by 62max chars (63 total)
    [a-z]{2,}$                      # TLD
    ''', re.I | re.VERBOSE)
html_id_re = re.compile(r'[A-Za-z][A-Za-z0-9-_:.]+')
html_name_re = html_id_re
N_ = lambda s: s
username_re = re.compile(r"[^ \t\n\r@<>()]+$", re.I)


# Level-1 Converters


def boolean_to_unicode(value, state = states.default_state):
    """Convert a boolean to unicode.
    
    Like most converters, a ``None`` value is not converted.

    >>> boolean_to_unicode(False)
    (u'0', None)
    >>> boolean_to_unicode(True)
    (u'1', None)
    >>> boolean_to_unicode(0)
    (u'0', None)
    >>> boolean_to_unicode('')
    (u'0', None)
    >>> boolean_to_unicode('any non-empty string')
    (u'1', None)
    >>> boolean_to_unicode('0')
    (u'1', None)
    >>> boolean_to_unicode(None)
    (None, None)
    >>> pipe(default(False), boolean_to_unicode)(None)
    (u'0', None)
    """
    if value is None:
        return None, None
    return unicode(int(bool(value))), None


def clean_unicode_to_balanced_ternary_digit(value, state = states.default_state):
    """Convert a clean unicode string to an integer -1, 0 or 1."""
    if value is None:
        return None, None
    try:
        return cmp(int(value), 0), None
    except ValueError:
        return None, state._('Value must be a balanced ternary digit')


def clean_unicode_to_boolean(value, state = states.default_state):
    """Convert a clean unicode string to a boolean."""
    if value is None:
        return None, None
    try:
        return bool(int(value)), None
    except ValueError:
        return None, state._('Value must be a boolean')


def clean_unicode_to_email(value, state = states.default_state):
    """Convert a clean unicode string to an email address."""
    if value is None:
        return None, None
    value = value.lower()
    if value.startswith(u'mailto:'):
        value = value.replace(u'mailto:', u'')
    try:
        username, domain = value.split('@', 1)
    except ValueError:
        return None, state._('An email must contain exactly one "@".')
    if not username_re.match(username):
        return None, state._('Invalid username')
    if not domain_re.match(domain) and domain != 'localhost':
        return None, state._('Invalid domain name')
    return value, None


def clean_unicode_to_json(value, state = states.default_state):
    """Convert a clean unicode string to a JSON value."""
    if value is None:
        return None, None
    import simplejson as json
    if isinstance(value, str):
        # Ensure that json.loads() uses unicode strings.
        value = value.decode('utf-8')
    try:
        return json.loads(value), None
    except json.JSONDecodeError, e:
        return None, unicode(e)


def clean_unicode_to_uri(add_prefix = 'http://', full = False, remove_fragment = False, schemes = ('http', 'https')):
    """Return a converter that converts a clean unicode string to an URI."""
    def clean_unicode_to_uri_converter(value, state = states.default_state):
        if value is None:
            return None, None
        else:
            import urlparse
            split_uri = list(urlparse.urlsplit(value))
            if full and add_prefix and not split_uri[0] and not split_uri[1] and split_uri[2] \
                    and not split_uri[2].startswith('/'):
                split_uri = list(urlparse.urlsplit(add_prefix + value))
            scheme = split_uri[0]
            if scheme != scheme.lower():
                split_uri[0] = scheme = scheme.lower()
            if full and not scheme:
                return None, state._('URI must be complete')
            if scheme and schemes is not None and scheme not in schemes:
                return None, state._('Scheme must belong to {0}').format(sorted(schemes))
            network_location = split_uri[1]
            if network_location != network_location.lower():
                split_uri[1] = network_location = network_location.lower()
            if scheme in ('http', 'https') and not split_uri[2]:
                # By convention a full HTTP URI must always have at least a "/" in its path.
                split_uri[2] = '/'
            if remove_fragment and split_uri[4]:
                split_uri[4] = ''
            return unicode(urlparse.urlunsplit(split_uri)), None
    return clean_unicode_to_uri_converter


def clean_unicode_to_uri_path_and_query(value, state = states.default_state):
    """Converts a clean unicode string to the path and query of an URI."""
    if value is None:
        return None, None
    else:
        import urlparse
        split_uri = list(urlparse.urlsplit(value))
        if split_uri[0] or split_uri[1]:
            return None, state._('URI must not be complete"')
        if split_uri[4]:
            split_uri[4] = ''
        return unicode(urlparse.urlunsplit(split_uri)), None


def cleanup_crlf(value, state = states.default_state):
    """Replace CR+LF or CR with CR."""
    if value is None:
        return None, None
    else:
        return value.replace('\r\n', '\n').replace('\r', '\n'), None


def cleanup_empty(value, state = states.default_state):
    """When value is comparable to False (ie None, 0 , '', etc) replace it with None else keep it as is."""
    return value if value else None, None


def condition(test_converter, ok_converter, error_converter = None):
    """When ``test_converter`` succeeds (ie no error), then apply ``ok_converter``, otherwise applies ``error_converter``."""
    def condition_converter(value, state = states.default_state):
        test, error = test_converter(value, state = state)
        if error is None:
            return ok_converter(value, state = state)
        elif error_converter is None:
            return value, None
        else:
            return error_converter(value, state = state)
    return condition_converter


def default(constant):
    """Return a converter that replace missing value by given one."""
    return lambda value, state = states.default_state: (constant, None) if value is None else (value, None)


def dict_to_instance(cls):
    """Return a converter that creates in instance of a class from a dictionary."""
    def dict_to_instance_converter(value, state = states.default_state):
        if value is None:
            return None, None
        instance = cls()
        instance.__dict__ = value
        return instance, None
    return dict_to_instance_converter


def equals(constant):
    """Return a converter that accepts only values equals to given constant."""
    def equals_converter(value, state = states.default_state):
        if constant is None or value is None or value == constant:
            return value, None
        else:
            return None, state._('Value must be equal to {0}').format(constant)
    return equals_converter


def fail(msg):
    """Return a converter that always returns an error."""
    def fail_converter(value, state = states.default_state):
        return None, state._(msg)
    return fail_converter


def first_valid(*converters):
    """Try each converter successively until one succeeds. When every converter fail, return the result of the last one."""
    def first_valid_converter(value, state = states.default_state):
        convertered_value = value
        error = None
        for converter in converters:
            convertered_value, error = converter(value, state = state)
            if error is None:
                return convertered_value, error
        return convertered_value, error
    return first_valid_converter


def function(function, handle_none = False):
    """Return a converter that applies a function to value and returns a new value."""
    def function_converter(value, state = states.default_state):
        if value is None and not handle_none or function is None:
            return value, None
        return function(value), None
    return function_converter


def greater_or_equal(constant):
    """Return a converter that accepts only values greater than or equal to given constant."""
    def greater_or_equal_converter(value, state = states.default_state):
        if constant is None or value is None or value >= constant:
            return value, None
        else:
            return None, state._('Value must be greater than or equal to {0}').format(constant)
    return greater_or_equal_converter


def item_or_sequence(converter, constructor = list, keep_empty = False, keep_null_items = False):
    """Return a converter that accepts either an item or a sequence of items."""
    return condition(
        test_isinstance(constructor),
        pipe(
            uniform_sequence(converter, constructor = constructor, keep_empty = keep_empty,
                keep_null_items = keep_null_items),
            extract_if_singleton,
            ),
        converter,
        )


def less_or_equal(constant):
    """Return a converter that accepts only values less than or equal to given constant."""
    def less_or_equal_converter(value, state = states.default_state):
        if constant is None or value is None or value <= constant:
            return value, None
        else:
            return None, state._('Value must be less than or equal to {0}').format(constant)
    return less_or_equal_converter


def mapping_value(key, default = None):
    """Return a converter that retrieves an item value from a mapping."""
    def mapping_value_converter(value, state = states.default_state):
        if value is None:
            return None, None
        return value.get(key, default), None
    return mapping_value_converter


def match(regex):
    """Return a converter that accepts only values that match given (compiled) regular expression."""
    def match_converter(value, state = states.default_state):
        if regex is None or value is None or regex.match(value):
            return value, None
        else:
            return None, state._('Invalid value format')
    return match_converter


def none_to_empty_unicode(value, state = states.default_state):
    """Replace None value with empty string."""
    return u'' if value is None else value, None


def noop(value, state = states.default_state):
    """Return value as is."""
    return value, None


def one_of(values):
    """Return a converter that accepts only values belonging to a given set (or list or...)."""
    def one_of_converter(value, state = states.default_state):
        if value is None or values is None or value in values:
            return value, None
        else:
            return None, state._('Value must be one of {0}').format(values)
    return one_of_converter


def pipe(*converters):
    """Return a compound converter that applies each of its converters till the end or an error occurs."""
    def pipe_converter(*args, **kwargs):
        for converter in converters:
            if converter is None:
                continue
            value, error = converter(*args, **kwargs)
            if error is not None:
                return value, error
            args = [value]
            kwargs = {}
        return value, None
    return pipe_converter


def python_data_to_boolean(value, state = states.default_state):
    """boolean any Python data to a boolean."""
    if value is None:
        return None, None
    else:
        return bool(value), None


def python_data_to_float(value, state = states.default_state):
    """Convert any python data to a float."""
    if value is None:
        return None, None
    else:
        try:
            return float(value), None
        except ValueError:
            return None, state._('Value must be a float')


def python_data_to_integer(value, state = states.default_state):
    """Convert any python data to an integer."""
    if value is None:
        return None, None
    else:
        try:
            return int(value), None
        except ValueError:
            return None, state._('Value must be an integer')


def python_data_to_unicode(value, state = states.default_state):
    """Convert any Python data to unicode."""
    if value is None:
        return None, None
    elif isinstance(value, str):
        return value.decode('utf-8'), None
    else:
        try:
            return unicode(value), None
        except UnicodeDecodeError:
            return str(value).decode('utf-8'), None


def rename_item(old_key, new_key):
    """Return a converter that renames a key of a mapping."""
    def rename_item_converter(value, state = states.default_state):
        if value is None:
            return None, None
        if old_key in value:
            value[new_key] = value.pop(old_key)
        return value, None
    return rename_item_converter


def require(value, state = states.default_state):
    """converter missing value."""
    if value is None:
        return None, state._('Missing value')
    else:
        return value, None


def set_value(constant):
    """Return a converter that replaces any non-null value by given one.

    This is the opposite behaviour of function ``default``.
    """
    return lambda value, state = states.default_state: (constant, None) if value is not None else (None, None)


def sort(cmp = None, key = None, reverse = False):
    """Return a converter that sorts an iterable."""
    def sort_converter(values, state = states.default_state):
        if values is None:
            return None, None
        else:
            return sorted(values, cmp = cmp, key = key, reverse = reverse), None
    return sort_converter


def split(separator = None):
    """Returns a converter that splits a string."""
    def split_converter(value, state = states.default_state):
        if value is None:
            return None, None
        else:
            return value.split(separator), None
    return split_converter


def strip(chars = None):
    """Returns a converter that removes leading and trailing characters from string."""
    def strip_converter(value, state = states.default_state):
        if value is None:
            return None, None
        else:
            return value.strip(chars), None
    return strip_converter


def structured_mapping(converters, constructor = dict, default = None, keep_empty = False):
    """Return a converter that maps a mapping of converters to a mapping (ie dict, etc) of values."""
    converters = dict(
        (name, converter)
        for name, converter in (converters or {}).iteritems()
        if converter is not None
        )
    def structured_mapping_converter(values, state = states.default_state):
        if values is None:
            return None, None
        if default == 'ignore':
            values_converter = converters
        else:
            values_converter = converters.copy()
            for name in values:
                if name not in values_converter:
                    values_converter[name] = default if default is not None else fail(N_('Unexpected item'))
        errors = {}
        convertered_values = {}
        for name, converter in values_converter.iteritems():
            convertered_value, error = converter(values.get(name), state = state)
            if error is not None:
                errors[name] = error
            elif convertered_value is not None:
                convertered_values[name] = convertered_value
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return structured_mapping_converter


def structured_sequence(converters, constructor = list, default = None, keep_empty = False):
    """Return a converter that map a sequence of converters to a sequence of values."""
    converters = [
        converter
        for converter in converters or []
        if converter is not None
        ]
    def structured_sequence_converter(values, state = states.default_state):
        if values is None:
            return None, None
        if default == 'ignore':
            values_converter = converters
        else:
            values_converter = converters[:]
            while len(values) > len(values_converter):
                values_converter.append(default if default is not None else fail(N_('Unexpected item')))
        errors = {}
        convertered_values = []
        for i, (converter, value) in enumerate(itertools.izip_longest(
                values_converter, itertools.islice(values, len(values_converter)))):
            convertered_value, error = converter(value, state = state)
            if error is not None:
                errors[i] = error
            convertered_values.append(convertered_value)
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return structured_sequence_converter


def test(function, error = 'Test failed', handle_none = False):
    """Return a converter that applies a test function to a value and returns an error when test fails.

    ``test`` always returns the initial value, even when test fails.

    >>> test(lambda value: isinstance(value, basestring))('hello')
    ('hello', None)
    >>> test(lambda value: isinstance(value, basestring))(1)
    (1, 'Test failed')
    >>> test(lambda value: isinstance(value, basestring), error = 'Value is not a string')(1)
    (1, 'Value is not a string')
    """
    def test_converter(value, state = states.default_state):
        if value is None and not handle_none or function is None or function(value):
            return value, None
        return value, state._(error)
    return test_converter


def test_isinstance(class_or_classes):
    """Return a converter that accepts only an instance of given class (or tuple of classes).

    >>> test_isinstance(basestring)('This is a string')
    ('This is a string', None)
    >>> test_isinstance(basestring)(42)
    (42, "Value is not an instance of <type 'basestring'>")
    >>> test_isinstance((float, int))(42)
    (42, None)
    """
    return test(lambda value: isinstance(value, class_or_classes),
        error = N_('Value is not an instance of {0}').format(class_or_classes))


def translate(conversions):
    """Return a converter that converts values found in given dictionary and keep others as is."""
    def translate_converter(value, state = states.default_state):
        if value is None or conversions is None or value not in conversions:
            return value, None
        else:
            return conversions[value], None
    return translate_converter


def unicode_to_uri(add_prefix = 'http://', full = False, remove_fragment = False, schemes = ('http', 'https')):
    """Return a converter that converts an unicode string to an URI."""
    return pipe(
        strip(),
        cleanup_empty,
        clean_unicode_to_uri(add_prefix = add_prefix, full = full, remove_fragment = remove_fragment,
            schemes = schemes),
        )


def uniform_mapping(key_converter, value_converter, constructor = dict, keep_empty = False, keep_null_keys = False,
        keep_null_values = False):
    """Return a converter that applies a unique converter to each key and another unique converter to each value of a mapping."""
    def uniform_mapping_converter(values, state = states.default_state):
        if values is None:
            return None, None
        errors = {}
        convertered_values = {}
        for key, value in values.iteritems():
            convertered_key, error = key_converter(key, state = state)
            if error is not None:
                errors[key] = error
                continue
            if convertered_key is None and not keep_null_keys:
                continue
            convertered_value, error = value_converter(value, state = state)
            if error is not None:
                errors[key] = error
            if convertered_value is None and not keep_null_values:
                continue
            convertered_values[convertered_key] = convertered_value
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return uniform_mapping_converter


def uniform_sequence(converter, constructor = list, keep_empty = False, keep_null_items = False):
    """Return a converter that applies the same converter to each value of a list."""
    def uniform_sequence_converter(values, state = states.default_state):
        if values is None:
            return None, None
        errors = {}
        convertered_values = []
        for i, value in enumerate(values):
            convertered_value, error = converter(value, state = state)
            if error is not None:
                errors[i] = error
            if keep_null_items or convertered_value is not None:
                convertered_values.append(convertered_value)
        if keep_empty or convertered_values:
            convertered_values = constructor(convertered_values)
        else:
            convertered_values = None
        return convertered_values, errors or None
    return uniform_sequence_converter


# Level-2 Converters


cleanup_line = pipe(strip(), cleanup_empty)
cleanup_text = pipe(cleanup_crlf, cleanup_line)
# Extract first item of sequence when it is a singleton and it is not itself a sequence, otherwise keep it unchanged.
extract_if_singleton = condition(
    test(lambda value: len(value) == 1 and not isinstance(value[0], (list, set, tuple))),
    function(lambda value: list(value)[0]),
    )


# Level-3 Converters


form_data_to_boolean = pipe(cleanup_line, clean_unicode_to_boolean, default(False))
python_data_to_geo = pipe(
    test_isinstance((list, tuple)),
    structured_sequence(
        [
            pipe(python_data_to_float, greater_or_equal(-90), less_or_equal(90)), # latitude
            pipe(python_data_to_float, greater_or_equal(-180), less_or_equal(180)), # longitude
            pipe(python_data_to_integer, greater_or_equal(0), less_or_equal(9)), # accuracy
            ],
        default = 'ignore'),
    )
unicode_to_balanced_ternary_digit = pipe(cleanup_line, clean_unicode_to_balanced_ternary_digit)
unicode_to_boolean = pipe(cleanup_line, clean_unicode_to_boolean)
unicode_to_email = pipe(cleanup_line, clean_unicode_to_email)
unicode_to_float = pipe(cleanup_line, python_data_to_float)
unicode_to_html_id = pipe(cleanup_line, match(html_id_re))
unicode_to_html_name = pipe(cleanup_line, match(html_id_re))
unicode_to_integer = pipe(cleanup_line, python_data_to_integer)
unicode_to_json = pipe(cleanup_line, clean_unicode_to_json)


# Level-4 Converters


strictly_positive_unicode_to_integer = pipe(unicode_to_integer, greater_or_equal(1))


# Deprecated Converters


restrict = one_of


def restrict_json_class_name(values):
    """Return a converter that accepts only JSON dictionaries with an attribute "class_name" belonging to given set."""
    def restrict_json_class_name_converter(value, state = states.default_state):
        if value is None:
            return value, None
        if not isinstance(value, dict):
            return None, state._('Invalid value: Not a JSON dictionary')
        class_name = value.get('class_name')
        if class_name is None:
            return None, state._('Missing class name in JSON dictionary')
        if values is not None and class_name not in values:
            return None, state._('Value must be one of {0}').format(values)
        return value, None
    return restrict_json_class_name_converter


# Utility Functions


def to_value(converter, ignore_error = False):
    """Return a function that calls a converter and returns its result value."""
    def to_value_converter(*args, **kwargs):
        value, error = converter(*args, **kwargs)
        if not ignore_error and error is not None:
            raise ValueError(error)
        return value
    return to_value_converter

