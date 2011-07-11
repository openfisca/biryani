# -*- coding: utf-8 -*-


# Suq -- Python Toolbox
# By: Emmanuel Raviart <eraviart@easter-eggs.com>
#
# Copyright (C) 2009, 2010 Easter-eggs
# http://wiki.infos-pratiques.org/wiki/Suq
#
# This file is part of Suq.
#
# Suq is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Suq is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Conversion functions

Most converters do only one operation and can fail when given wrong data. To ensure that they don't fail, they must be
combined with other converters.
"""


import gettext
import re
import itertools

try:
    import bson
except ImportError:
    bson = None


domain_re = re.compile(r'''
    (?:[a-z0-9][a-z0-9\-]{0,62}\.)+ # (sub)domain - alpha followed by 62max chars (63 total)
    [a-z]{2,}$                      # TLD
    ''', re.I | re.VERBOSE)
html_id_re = re.compile(r'[A-Za-z][A-Za-z0-9-_:.]+')
html_name_re = html_id_re
N_ = lambda s: s
if bson is not None:
    object_id_re = re.compile(r'[\da-f]{24}$')
username_re = re.compile(r"[^ \t\n\r@<>()]+$", re.I)


# Minimal context, usable with converters


class Context(object):
    translator = gettext.NullTranslations()

ctx = Context()


# Level-1 Converters


def attribute(name):
    """Return a filter that retrieves an existing attribute from an object."""
    def f(ctx, value):
        if value is None or name is None:
            return value, None
        # It assumes that an attribute is always declared in its class, so it always exists.
        return getattr(value, name), None
    return f


def boolean_to_unicode(ctx, value):
    """Convert a boolean to unicode."""
    if value is None:
        return None, None
    else:
        return unicode(int(bool(value))), None


def clean_iso8601_to_date(ctx, value):
    """Convert a clean unicode string in ISO 8601 format to a date."""
    if value is None:
        return None, None
    else:
        import datetime
        import mx.DateTime
        # mx.DateTime.ISO.ParseDateTimeUTC fails when time zone is preceded with a space. For example,
        # mx.DateTime.ISO.ParseDateTimeUTC'2011-03-17 14:46:03 +01:00') raises a"ValueError: wrong format,
        # use YYYY-MM-DD HH:MM:SS" while mx.DateTime.ISO.ParseDateTimeUTC'2011-03-17 14:46:03+01:00') works.
        # So we remove space before "+" and "-".
        while u' +' in value:
            value = value.replace(u' +', '+')
        while u' -' in value:
            value = value.replace(u' -', '-')
        try:
            return datetime.date.fromtimestamp(mx.DateTime.ISO.ParseDateTimeUTC(value)), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a date in ISO 8601 format')


def clean_iso8601_to_datetime(ctx, value):
    """Convert a clean unicode string in ISO 8601 format to a datetime."""
    if value is None:
        return None, None
    else:
        import datetime
        import mx.DateTime
        # mx.DateTime.ISO.ParseDateTimeUTC fails when time zone is preceded with a space. For example,
        # mx.DateTime.ISO.ParseDateTimeUTC'2011-03-17 14:46:03 +01:00') raises a"ValueError: wrong format,
        # use YYYY-MM-DD HH:MM:SS" while mx.DateTime.ISO.ParseDateTimeUTC'2011-03-17 14:46:03+01:00') works.
        # So we remove space before "+" and "-".
        while u' +' in value:
            value = value.replace(u' +', '+')
        while u' -' in value:
            value = value.replace(u' -', '-')
        try:
            return datetime.datetime.fromtimestamp(mx.DateTime.ISO.ParseDateTimeUTC(value)), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a date-time in ISO 8601 format')


def clean_unicode_to_balanced_ternary_digit(ctx, value):
    """Convert a clean unicode string to an integer -1, 0 or 1."""
    if value is None:
        return None, None
    else:
        try:
            return cmp(int(value), 0), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a balanced ternary digit')


def clean_unicode_to_boolean(ctx, value):
    """Convert a clean unicode string to a boolean."""
    if value is None:
        return None, None
    else:
        try:
            return bool(int(value)), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a boolean')


def clean_unicode_to_email(ctx, value):
    """Convert a clean unicode string to an email address."""
    if value is None:
        return None, None
    else:
        value = value.lower()
        if value.startswith(u'mailto:'):
            value = value.replace(u'mailto:', u'')
        try:
            username, domain = value.split('@', 1)
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('An email must contain exactly one "@".')
        if not username_re.match(username):
            _ = ctx.translator.ugettext
            return None, _('Invalid username')
        if not domain_re.match(domain) and domain != 'localhost':
            _ = ctx.translator.ugettext
            return None, _('Invalid domain name')
        return value, None


def clean_unicode_to_json(ctx, value):
    """Convert a clean unicode string to a JSON value."""
    if value is None:
        return None, None
    else:
        import simplejson as json
        if isinstance(value, str):
            # Ensure that json.loads() uses unicode strings.
            value = value.decode('utf-8')
        try:
            return json.loads(value), None
        except json.JSONDecodeError, e:
            return None, unicode(e)


def clean_unicode_to_lang(ctx, value):
    """Convert a clean unicode string to a language code."""
    if value is None:
        return None, None
    else:
        import babel
        if not babel.localedata.exists(value):
            _ = ctx.translator.ugettext
            return None, _('Invalid value')
        return value, None


if bson is not None:
    def clean_unicode_to_object_id(ctx, value):
        """Convert a clean unicode string to MongoDB ObjectId."""
        if value is None:
            return None, None
        else:
            id = value.lower()
            if object_id_re.match(id) is None:
                _ = ctx.translator.ugettext
                return None, _('Invalid value')
            return bson.objectid.ObjectId(id), None


def clean_unicode_to_phone(ctx, value):
    """Convert a clean unicode string to phone number."""
    if value is None:
        return None, None
    from suq import strings
    if value.startswith('+'):
        value = value.replace('+', '00', 1)
    value = unicode(strings.simplify(value, separator = ''))
    if not value:
        return None, None
    if not value.isdigit():
        _ = ctx.translator.ugettext
        return None, _('Unexpected non numerical characters in phone number')

    if value.startswith('0033'):
        value = value[2:]
    if value.startswith('330'):
        value = value[2:]
    elif value.startswith('33'):
        value = '0' + value[2:]

    if value.startswith('00'):
        # International phone number
        country = {
            '594': N_('French Guyana'),
            '681': N_('Wallis and Futuna'),
            '687': N_('New Caledonia'),
            '689': N_('French Polynesia'),
            }.get(value[2:5])
        if country is not None:
            if len(value) == 11:
                return '+{0} {1} {2} {3}'.format(value[2:5], value[5:7], value[7:9], value[9:11]), None
            _ = ctx.translator.ugettext
            return None, _('Wrong number of digits for phone number of {0}').format(_(country))
        _ = ctx.translator.ugettext
        return None, _('Unknown international phone number')
    if len(value) == 4:
        return value, None
    if len(value) == 9 and value[0] != '0':
        value = u'0{0}'.format(value)
    if len(value) == 10:
        if value[0] != '0':
            _ = ctx.translator.ugettext
            return None, _('Unexpected first digit in phone number: {0} instead of 0').format(value[0])
        mask = '+33 {0}{1} {2} {3} {4}' if value[1] == '8' else '+33 {0} {1} {2} {3} {4}'
        return mask.format(value[1], value[2:4], value[4:6], value[6:8], value[8:10]), None
    _ = ctx.translator.ugettext
    return None, _('Wrong number of digits in phone number')


def clean_unicode_to_slug(ctx, value):
    """Convert a clean unicode string to a slug."""
    if value is None:
        return None, None
    else:
        from suq import strings
        value = strings.simplify(value)
        return value or None, None


def clean_unicode_to_uri(add_prefix = 'http://', full = False, remove_fragment = False, schemes = ('http', 'https')):
    """Return a filter that converts a clean unicode string to an URI."""
    def f(ctx, value):
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
                _ = ctx.translator.ugettext
                return None, _('URI must be complete')
            if scheme and schemes is not None and scheme not in schemes:
                _ = ctx.translator.ugettext
                return None, _('Scheme must belong to {0}').format(sorted(schemes))
            network_location = split_uri[1]
            if network_location != network_location.lower():
                split_uri[1] = network_location = network_location.lower()
            if scheme in ('http', 'https') and not split_uri[2]:
                # By convention a full HTTP URI must always have at least a "/" in its path.
                split_uri[2] = '/'
            if remove_fragment and split_uri[4]:
                split_uri[4] = ''
            return unicode(urlparse.urlunsplit(split_uri)), None
    return f


def clean_unicode_to_uri_path_and_query(ctx, value):
    """Converts a clean unicode string to the path and query of an URI."""
    if value is None:
        return None, None
    else:
        import urlparse
        split_uri = list(urlparse.urlsplit(value))
        if split_uri[0] or split_uri[1]:
            _ = ctx.translator.ugettext
            return None, _('URI must not be complete"')
        if split_uri[4]:
            split_uri[4] = ''
        return unicode(urlparse.urlunsplit(split_uri)), None


def clean_unicode_to_url_name(ctx, value):
    """Convert a clean unicode string to a normalized string that can be used in an URL path or a query parameter."""
    if value is None:
        return None, None
    else:
        from suq import strings
        for character in u'\n\r/?&#':
            value = value.replace(character, u' ')
        value = strings.normalize(value, separator = u'_')
        return value or None, None


def cleanup_crlf(ctx, value):
    """Replace CR+LF or CR with CR."""
    if value is None:
        return None, None
    else:
        return value.replace('\r\n', '\n').replace('\r', '\n'), None


def cleanup_empty(ctx, value):
    """When value is comparable to False (ie None, 0 , '', etc) replace it with None else keep it as is."""
    return value if value else None, None


def condition(test_filter, ok_filter, error_filter = None):
    """When ``test_filter`` succeeds (ie no error), then apply ``ok_filter``, otherwise applies ``error_filter``."""
    def f(ctx, value):
        test, error = test_filter(ctx, value)
        if error is None:
            return ok_filter(ctx, value)
        elif error_filter is None:
            return value, None
        else:
            return error_filter(ctx, value)
    return f


def date_to_datetime(ctx, value):
    """Convert a date object to a datetime."""
    if value is None:
        return None, None
    else:
        import datetime
        return datetime.datetime(value.year, value.month, value.day), None


def date_to_iso8601(ctx, value):
    """Convert a date to unicode string using ISO 8601 format."""
    if value is None:
        return None, None
    else:
        return unicode(value.strftime('%Y-%m-%d')), None


def date_to_timestamp(ctx, value):
    """Convert a datetime to a JavaScript timestamp."""
    if value is None:
        return None, None
    else:
        import calendar
        return int(calendar.timegm(value.timetuple()) * 1000), None


def datetime_to_date(ctx, value):
    """Convert a datetime object to a date."""
    if value is None:
        return None, None
    else:
        return value.date(), None


def datetime_to_iso8601(ctx, value):
    """Convert a datetime to unicode string using ISO 8601 format."""
    if value is None:
        return None, None
    else:
        return unicode(value.strftime('%Y-%m-%d %H:%M:%S')), None


def datetime_to_timestamp(ctx, value):
    """Convert a datetime to a JavaScript timestamp."""
    if value is None:
        return None, None
    else:
        import calendar
        utcoffset = value.utcoffset()
        if utcoffset is not None:
            value -= utcoffset
        return int(calendar.timegm(value.timetuple()) * 1000 + value.microsecond / 1000), None


def default(constant):
    """Return a filter that replace missing value by given one."""
    return lambda ctx, value: (constant, None) if value is None else (value, None)


def dict_to_instance(cls):
    """Return a filter that creates in instance of a class from a dictionary."""
    def dict_to_instance_filter(ctx, value):
        if value is None:
            return None, None
        instance = cls()
        instance.__dict__ = value
        return instance, None
    return dict_to_instance_filter


def equals(constant):
    """Return a filter that accepts only values equals to given constant."""
    def f(ctx, value):
        if constant is None or value is None or value == constant:
            return value, None
        else:
            _ = ctx.translator.ugettext
            return None, _('Value must be equal to {0}').format(constant)
    return f


def fail(msg):
    """Return a filter that always returns an error."""
    def fail_filter(ctx, value):
        _ = ctx.translator.ugettext
        return None, _(msg)
    return error_filter


def first_valid(*filters):
    """Try each filter successively until one succeeds. When every filter fail, return the result of the last one."""
    def f(ctx, value):
        filtered_value = value
        error = None
        for filter in filters:
            filtered_value, error = filter(ctx, value)
            if error is None:
                return filtered_value, error
        return filtered_value, error
    return f


def function(function):
    """Return a filter that applies a function to value and returns a new value."""
    def f(ctx, value):
        if value is None or function is None:
            return value, None
        return function(value), None
    return f


def is_instance(class_or_classes):
    """Return a filter that accepts only an instance of given classes."""
    def f(ctx, value):
        if class_or_classes is None or value is None or isinstance(value, class_or_classes):
            return value, None
        else:
            _ = ctx.translator.ugettext
            return None, _('Value is not an instance of {0}').format(class_or_classes)
    return f


def greater_or_equal(constant):
    """Return a filter that accepts only values greater than or equal to given constant."""
    def f(ctx, value):
        if constant is None or value is None or value >= constant:
            return value, None
        else:
            _ = ctx.translator.ugettext
            return None, _('Value must be greater than or equal to {0}').format(constant)
    return f


def item_or_sequence(filter, constructor = list, keep_empty = False, keep_null_items = False):
    """Return a filter that accepts either an item or a sequence of items."""
    return condition(
        is_instance(constructor),
        pipe(
            uniform_sequence(filter, constructor = constructor, keep_empty = keep_empty,
                keep_null_items = keep_null_items),
            extract_if_singleton,
            ),
        filter,
        )


def less_or_equal(constant):
    """Return a filter that accepts only values less than or equal to given constant."""
    def f(ctx, value):
        if constant is None or value is None or value <= constant:
            return value, None
        else:
            _ = ctx.translator.ugettext
            return None, _('Value must be less than or equal to {0}').format(constant)
    return f


def mapping_value(key, default = None):
    """Return a filter that retrieves an item value from a mapping."""
    def f(ctx, value):
        if value is None:
            return None, None
        return value.get(key, default), None
    return f


def match(regex):
    """Return a filter that accepts only values that match given (compiled) regular expression."""
    def f(ctx, value):
        if regex is None or value is None or regex.match(value):
            return value, None
        else:
            _ = ctx.translator.ugettext
            return None, _('Invalid value format')
    return f


def none_to_empty_unicode(ctx, value):
    """Replace None value with empty string."""
    return u'' if value is None else value, None


def noop(ctx, value):
    """Return value as is."""
    return value, None


if bson is not None:
    def mongodb_query_to_object(object_class):
        def f(ctx, value):
            """Convert a MongoDB query expression to an object wrapped to a MongoDB document."""
            if value is None:
                return None, None
            instance = object_class.find_one(value)
            if instance is None:
                _ = ctx.translator.ugettext
                return None, _('No document of class {0} for query {1}').format(object_class.__name__, value)
            return instance, None
        return f


    def object_id_to_object(object_class, cache = None):
        def f(ctx, value):
            """Convert an ID to an object wrapped to a MongoDB document."""
            if value is None:
                return None, None
            assert isinstance(value, bson.objectid.ObjectId), str((value,))
            if cache is not None and value in cache:
                return cache[value], None
            instance = object_class.find_one(value)
            if instance is None:
                _ = ctx.translator.ugettext
                return None, _('No document of class {0} with ID {1}').format(object_class.__name__, value)
            return instance, None
        return f


    def object_id_to_unicode(ctx, value):
        """Convert a MongoDB ObjectId to unicode."""
        if value is None:
            return None, None
        else:
            return unicode(value), None


def pipe(*filters):
    """Return a compound filter that applies each of its filters till the end or an error occurs."""
    def f(ctx, *args, **kwargs):
        for filter in filters:
            if filter is None:
                continue
            value, error = filter(ctx, *args, **kwargs)
            if error is not None:
                return value, error
            args = [value]
            kwargs = {}
        return value, None
    return f


def python_data_to_boolean(ctx, value):
    """boolean any Python data to a boolean."""
    if value is None:
        return None, None
    else:
        return bool(value), None


def python_data_to_float(ctx, value):
    """Convert any python data to a float."""
    if value is None:
        return None, None
    else:
        try:
            return float(value), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a float')


def python_data_to_integer(ctx, value):
    """Convert any python data to an integer."""
    if value is None:
        return None, None
    else:
        try:
            return int(value), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be an integer')


def python_data_to_unicode(ctx, value):
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


def require(ctx, value):
    """Filter missing value."""
    if value is None:
        _ = ctx.translator.ugettext
        return None, _('Missing value')
    else:
        return value, None


def restrict(values):
    """Return a filter that accepts only values belonging to a given set (or list or...)."""
    def f(ctx, value):
        if value is None or values is None or value in values:
            return value, None
        else:
            _ = ctx.translator.ugettext
            return None, _('Value must be one of {0}').format(values)
    return f


def restrict_json_class_name(values):
    """Return a filter that accepts only JSON dictionaries with an attribute "class_name" belonging to given set."""
    def f(ctx, value):
        if value is None:
            return value, None
        if not isinstance(value, dict):
            _ = ctx.translator.ugettext
            return None, _('Invalid value: Not a JSON dictionary')
        class_name = value.get('class_name')
        if class_name is None:
            _ = ctx.translator.ugettext
            return None, _('Missing class name in JSON dictionary')
        if values is not None and class_name not in values:
            _ = ctx.translator.ugettext
            return None, _('Value must be one of {0}').format(values)
        return value, None
    return f


def set_value(constant):
    """Return a filter that replaces any non-null value by given one.

    This is the opposite behaviour of function ``default``.
    """
    return lambda ctx, value: (constant, None) if value is not None else (None, None)


def sort(cmp = None, key = None, reverse = False):
    """Return a filter that sorts an iterable."""
    def f(ctx, values):
        if values is None:
            return None, None
        else:
            return sorted(values, cmp = cmp, key = key, reverse = reverse), None
    return f


def split(separator = None):
    """Returns a filter that splits a string."""
    def f(ctx, value):
        if value is None:
            return None, None
        else:
            return value.split(separator), None
    return f


def strip(chars = None):
    """Returns a filter that removes leading and trailing characters from string."""
    def f(ctx, value):
        if value is None:
            return None, None
        else:
            return value.strip(chars), None
    return f


def structured_mapping(filters, constructor = dict, default = None, keep_empty = False):
    """Return a filter that maps a mapping of filters to a mapping (ie dict, etc) of values."""
    filters = dict(
        (name, filter)
        for name, filter in (filters or {}).iteritems()
        if filter is not None
        )
    def f(ctx, values):
        if values is None:
            return None, None
        if default == 'ignore':
            values_filter = filters
        else:
            values_filter = filters.copy()
            for name in values:
                if name not in values_filter:
                    values_filter[name] = default if default is not None else fail(N_('Unexpected item'))
        errors = {}
        filtered_values = {}
        for name, filter in values_filter.iteritems():
            filtered_value, error = filter(ctx, values.get(name))
            if error is not None:
                errors[name] = error
            elif filtered_value is not None:
                filtered_values[name] = filtered_value
        if keep_empty or filtered_values:
            filtered_values = constructor(filtered_values)
        else:
            filtered_values = None
        return filtered_values, errors or None
    return f


def structured_sequence(filters, constructor = list, default = None, keep_empty = False):
    """Return a filter that map a sequence of filters to a sequence of values."""
    filters = [
        filter
        for filter in filters or []
        if filter is not None
        ]
    def f(ctx, values):
        if values is None:
            return None, None
        if default == 'ignore':
            values_filter = filters
        else:
            values_filter = filters[:]
            while len(values) > len(values_filter):
                values_filter.append(default if default is not None else fail(N_('Unexpected item')))
        errors = {}
        filtered_values = []
        for i, (filter, value) in enumerate(itertools.izip_longest(
                values_filter, itertools.islice(values, len(values_filter)))):
            filtered_value, error = filter(ctx, value)
            if error is not None:
                errors[i] = error
            filtered_values.append(filtered_value)
        if keep_empty or filtered_values:
            filtered_values = constructor(filtered_values)
        else:
            filtered_values = None
        return filtered_values, errors or None
    return f


def test(function):
    """Return a filter that applies a test function and returns True when test succeeds or an error when it fails.
    """
    def f(ctx, value):
        if value is None or function is None:
            return value, None
        if function(value):
            return True, None
        else:
            _ = ctx.translator.ugettext
            return False, _('Value test failed')
        return bool(function(value)) or None, None
    return f


def timestamp_to_date(ctx, value):
    """Convert a JavaScript timestamp to a date."""
    if value is None:
        return None, None
    else:
        import datetime
        try:
            return datetime.date.fromtimestamp(value / 1000), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a timestamp')


def timestamp_to_datetime(ctx, value):
    """Convert a JavaScript timestamp to a datetime."""
    if value is None:
        return None, None
    else:
        import datetime
        import pytz
        try:
            return datetime.datetime.fromtimestamp(value / 1000, pytz.utc), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a timestamp')


def translate(conversions):
    """Return a filter that converts values found in given dictionary and keep others as is."""
    def f(ctx, value):
        if value is None or conversions is None or value not in conversions:
            return value, None
        else:
            return conversions[value], None
    return f


def unicode_to_uri(add_prefix = 'http://', full = False, remove_fragment = False, schemes = ('http', 'https')):
    """Return a filter that converts an unicode string to an URI."""
    return pipe(
        strip(),
        cleanup_empty,
        clean_unicode_to_uri(add_prefix = add_prefix, full = full, remove_fragment = remove_fragment,
            schemes = schemes),
        )


def uniform_mapping(key_filter, value_filter, constructor = dict, keep_empty = False, keep_null_keys = False,
        keep_null_values = False):
    """Return a filter that applies a unique filter to each key and another unique filter to each value of a mapping."""
    def f(ctx, values):
        if values is None:
            return None, None
        errors = {}
        filtered_values = {}
        for key, value in values.iteritems():
            filtered_key, error = key_filter(ctx, key)
            if error is not None:
                errors[key] = error
                continue
            if filtered_key is None and not keep_null_keys:
                continue
            filtered_value, error = value_filter(ctx, value)
            if error is not None:
                errors[key] = error
            if filtered_value is None and not keep_null_values:
                continue
            filtered_values[filtered_key] = filtered_value
        if keep_empty or filtered_values:
            filtered_values = constructor(filtered_values)
        else:
            filtered_values = None
        return filtered_values, errors or None
    return f


def uniform_sequence(filter, constructor = list, keep_empty = False, keep_null_items = False):
    """Return a filter that applies the same filter to each value of a list."""
    def f(ctx, values):
        if values is None:
            return None, None
        errors = {}
        filtered_values = []
        for i, value in enumerate(values):
            filtered_value, error = filter(ctx, value)
            if error is not None:
                errors[i] = error
            if keep_null_items or filtered_value is not None:
                filtered_values.append(filtered_value)
        if keep_empty or filtered_values:
            filtered_values = constructor(filtered_values)
        else:
            filtered_values = None
        return filtered_values, errors or None
    return f


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
iso8601_to_date = pipe(cleanup_line, clean_iso8601_to_date)
iso8601_to_datetime = pipe(cleanup_line, clean_iso8601_to_datetime)
python_data_to_geo = pipe(
    is_instance((list, tuple)),
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
unicode_to_lang = pipe(cleanup_line, clean_unicode_to_lang)
if bson is not None:
    unicode_to_object_id = pipe(cleanup_line, clean_unicode_to_object_id)
unicode_to_phone = pipe(cleanup_line, clean_unicode_to_phone)
unicode_to_slug = pipe(cleanup_line, clean_unicode_to_slug)
unicode_to_url_name = pipe(cleanup_line, clean_unicode_to_url_name)


# Level-4 Converters


if bson is not None:
    python_data_to_object_id = first_valid(
        is_instance(bson.objectid.ObjectId),
        pipe(is_instance(basestring), unicode_to_object_id),
        )
strictly_positive_unicode_to_integer = pipe(unicode_to_integer, greater_or_equal(1))


# Utility Functions


def to_value(filter, ignore_error = False):
    """Return a function that calls a filter and returns its result value."""
    def f(ctx, *args, **kwargs):
        value, error = filter(ctx, *args, **kwargs)
        if not ignore_error and error is not None:
            raise ValueError(error)
        return value
    return f

