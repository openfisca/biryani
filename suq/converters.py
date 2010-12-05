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


import re
import itertools


domain_re = re.compile(r'''
    (?:[a-z0-9][a-z0-9\-]{0,62}\.)+ # (sub)domain - alpha followed by 62max chars (63 total)
    [a-z]{2,}$                      # TLD
    ''', re.I | re.VERBOSE)
html_id_re = re.compile(r'[A-Za-z][A-Za-z0-9-_:.]+')
html_name_re = html_id_re
N_ = lambda s: s
object_id_re = re.compile(r'[\da-f]{24}$')
username_re = re.compile(r"[^ \t\n\r@<>()]+$", re.I)


# Constructors that return filters


def assert_ok(filter):
    """Return a compound filter that applies a filter, raising an assertion error if an error occurs."""
    def f(ctx, *args, **kwargs):
        value, error = filter(ctx, *args, **kwargs)
        assert error is None, error
        return value, error
    return f


def attribute(name):
    """Return a filter that retrieve an existing attribute from an object."""
    def f(ctx, value):
        if value is None or name is None:
            return value, None
        # It assumes that an attribute is always declared in its class, so it always exists.
        return getattr(value, name)
    return f


def compose(*filters):
    """Return a compound filter that applies each of its filters (in reverse order) till the end or an error occurs."""
    def f(ctx, *args, **kwargs):
        for filter in reversed(filters):
            if filter is None:
                continue
            value, error = filter(ctx, *args, **kwargs)
            if error is not None:
                return value, error
            args = [value]
            kwargs = {}
        return value, None
    return f


def default(constant):
    """Return a filter that replace missing value by given one."""
    return lambda ctx, value: (constant, None) if value is None else (value, None)


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


def less_or_equal(constant):
    """Return a filter that accepts only values less than or equal to given constant."""
    def f(ctx, value):
        if constant is None or value is None or value <= constant:
            return value, None
        else:
            _ = ctx.translator.ugettext
            return None, _('Value must be less than or equal to {0}').format(constant)
    return f


def map(filter, constructor = list, keep_empty = False, keep_null_items = False):
    """Return a filter that applies the same filter to each value of a list."""
    def f(ctx, values):
        if values is None:
            return None, None
        else:
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


def mapping(filters, ignore_extras = False, constructor = dict, keep_empty = False):
    """Return a filter that maps a mapping of filters to a mapping (ie dict, etc) of values."""
    filters = dict(
        (name, filter)
        for name, filter in (filters or {}).iteritems()
        if filter is not None
        )
    def f(ctx, values):
        if values is None:
            return None, None
        errors = {}
        filtered_values = {}
        if not ignore_extras and not set(values.iterkeys()).issubset(filters.iterkeys()):
            _ = ctx.translator.ugettext
            for name in values:
                if name not in filters:
                    errors[name] = _('Unexpected item')
        for name, filter in filters.iteritems():
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


def match(regex):
    """Return a filter that accepts only values that match given (compiled) regular expression."""
    def f(ctx, value):
        if regex is None or value is None or regex.match(value):
            return value, None
        else:
            _ = ctx.translator.ugettext
            return None, _('Invalid value format')
    return f


def object_from_id(object_class):
    def f(ctx, value):
        """Convert an ID to an object wrapped to a MongoDB document."""
        if value is None:
            return None, None
        else:
            instance = object_class.find_one(value)
            if instance is None:
                _ = ctx.translator.ugettext
                return None, _('No document with ID: {0}').format(value)
            return instance, None
    return f


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


def sequence(filters, constructor = list, ignore_extras = False, keep_empty = False):
    """Return a filter that map a sequence of filters to a sequence of values."""
    filters = [
        filter
        for filter in filters or []
        if filter is not None
        ]
    def f(ctx, values):
        if values is None:
            return None, None
        elif len(values) > len(filters) and not ignore_extras:
            _ = ctx.translator.ugettext
            return None, _('Too much values: {0} instead of {1}').format(len(values), len(filters))
        else:
            errors = {}
            filtered_values = []
            for i, (filter, value) in enumerate(itertools.izip_longest(
                    filters, itertools.islice(values, len(filters)))):
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


def strip(chars = None):
    """Returns a filter that removes leading and trailing characters from string."""
    def f(ctx, value):
        if value is None:
            return None, None
        else:
            return value.strip(chars), None
    return f


def url_from_clean_unicode(full = False, remove_fragment = False, schemes = ('http', 'https')):
    """Return a filter that converts a clean unicode string to an URL."""
    def f(ctx, value):
        if value is None:
            return None, None
        else:
            import urlparse
            split_url = list(urlparse.urlsplit(value))
            scheme = split_url[0]
            if scheme != scheme.lower():
                split_url[0] = scheme = scheme.lower()
            if full and not scheme:
                _ = ctx.translator.ugettext
                return None, _('URL must be complete"')
            if scheme and schemes is not None and scheme not in schemes:
                _ = ctx.translator.ugettext
                return None, _('Scheme must belong to {0}').format(sorted(schemes))
            network_location = split_url[1]
            if network_location != network_location.lower():
                split_url[1] = network_location = network_location.lower()
            if scheme in ('http', 'https') and not split_url[2]:
                # By convention a full HTTP URL must always have at least a "/" in its path.
                split_url[2] = '/'
            if remove_fragment and split_url[4]:
                split_url[4] = ''
            return unicode(urlparse.urlunsplit(split_url)), None
    return f


def url_from_unicode(full = False, remove_fragment = False, schemes = ('http', 'https')):
    """Return a filter that converts an unicode string to an URL."""
    return compose(
        url_from_clean_unicode(full = full, remove_fragment = remove_fragment, schemes = schemes),
        clean_empty,
        strip(),
        )


# Filtering functions without (value, error) parameter


def balanced_ternary_digit_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to an integer -1, 0 or 1."""
    if value is None:
        return None, None
    else:
        try:
            return cmp(int(value), 0), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a balanced ternary digit')


def boolean_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to a boolean."""
    if value is None:
        return None, None
    else:
        try:
            return bool(int(value)), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a boolean')


def boolean_from_python_data(ctx, value):
    """boolean any Python data to a boolean."""
    if value is None:
        return None, None
    else:
        return bool(value), None


def clean_crlf(ctx, value):
    """Replace CR+LF or CR with CR."""
    if value is None:
        return None, None
    else:
        return value.replace('\r\n', '\n').replace('\r', '\n'), None


def clean_empty(ctx, value):
    """When value is comparable to False (ie None, 0 , '', etc) replace it with None else keep it as is."""
    return value if value else None, None


def date_from_clean_iso8601(ctx, value):
    """Convert a clean unicode string in ISO 8601 format to a date."""
    if value is None:
        return None, None
    else:
        import datetime
        import mx.DateTime
        try:
            return datetime.date.fromtimestamp(mx.DateTime.ISO.ParseDateTimeUTC(value)), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a date in ISO 8601 format')


def date_from_datetime(ctx, value):
    """Convert a datetime object to a date."""
    if value is None:
        return None, None
    else:
        return value.date(), None


def date_from_timestamp(ctx, value):
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


def datetime_from_clean_iso8601(ctx, value):
    """Convert a clean unicode string in ISO 8601 format to a datetime."""
    if value is None:
        return None, None
    else:
        import datetime
        import mx.DateTime
        try:
            return datetime.datetime.fromtimestamp(mx.DateTime.ISO.ParseDateTimeUTC(value)), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a date-time in ISO 8601 format')


def datetime_from_date(ctx, value):
    """Convert a date object to a datetime."""
    if value is None:
        return None, None
    else:
        import datetime
        return datetime.datetime(value.year, value.month, value.day), None


def datetime_from_timestamp(ctx, value):
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


def email_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to an email address."""
    if value is None:
        return None, None
    else:
        value = value.lower()
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


def empty_unicode_from_none(ctx, value):
    """Replace None value with empty string."""
    return u'' if value is None else value, None


def float_from_python_data(ctx, value):
    """Convert any python data to a float."""
    if value is None:
        return None, None
    else:
        try:
            return float(value), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a float')


def integer_from_python_data(ctx, value):
    """Convert any python data to an integer."""
    if value is None:
        return None, None
    else:
        try:
            return int(value), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be an integer')


def iso8601_from_date(ctx, value):
    """Convert a date to unicode string using ISO 8601 format."""
    if value is None:
        return None, None
    else:
        return unicode(value.strftime('%Y-%m-%d')), None


def iso8601_from_datetime(ctx, value):
    """Convert a datetime to unicode string using ISO 8601 format."""
    if value is None:
        return None, None
    else:
        return unicode(value.strftime('%Y-%m-%d %H:%M:%S')), None


def json_from_clean_unicode(ctx, value):
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


def lang_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to a language code."""
    if value is None:
        return None, None
    else:
        import babel
        if not babel.localedata.exists(value):
            _ = ctx.translator.ugettext
            return None, _('Invalid value')
        return value, None


def noop(ctx, value):
    """Return value as is."""
    return value, None


def object_id_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to MongoDB ObjectId."""
    if value is None:
        return None, None
    else:
        import pymongo
        id = value.lower()
        if object_id_re.match(id) is None:
            _ = ctx.translator.ugettext
            return None, _('Invalid value')
        return pymongo.objectid.ObjectId(id), None


def phone_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to an email address."""
    if value is None:
        return None, None
    else:
        from suq import strings
        if value.startswith('+'):
            value = value.replace('+', '00', 1)
        value = unicode(strings.simplify(value, separator = ''))
        if not value:
            return None, None
        elif not value.isdigit():
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
                else:
                    _ = ctx.translator.ugettext
                    return None, _('Wrong number of digits for phone number of {0}').format(_(country))
            else:
                _ = ctx.translator.ugettext
                return None, _('Unknown international phone number')
        elif len(value) == 4:
            return value, None
        elif len(value) == 10:
            if value[0] != '0':
                _ = ctx.translator.ugettext
                return None, _('Unexpected first digit in phone number: {0} instead of 0').format(value[0])
            else:
                mask = '+33 {0}{1} {2} {3} {4}' if value[1] == '8' else '+33 {0} {1} {2} {3} {4}'
                return mask.format(value[1], value[2:4], value[4:6], value[6:8], value[8:10]), None
        else:
            _ = ctx.translator.ugettext
            return None, _('Wrong number of digits in phone number')


def require(ctx, value):
    """Filter missing value."""
    if value is None:
        _ = ctx.translator.ugettext
        return None, _('Missing value')
    else:
        return value, None


def slug_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to a slug."""
    if value is None:
        return None, None
    else:
        from suq import strings
        value = strings.simplify(value)
        return value or None, None


def timestamp_from_date(ctx, value):
    """Convert a datetime to a JavaScript timestamp."""
    if value is None:
        return None, None
    else:
        import calendar
        return int(calendar.timegm(value.timetuple()) * 1000), None


def timestamp_from_datetime(ctx, value):
    """Convert a datetime to a JavaScript timestamp."""
    if value is None:
        return None, None
    else:
        import calendar
        utcoffset = value.utcoffset()
        if utcoffset is not None:
            value -= utcoffset
        return int(calendar.timegm(value.timetuple()) * 1000 + value.microsecond / 1000), None


def unicode_from_boolean(ctx, value):
    """Convert a boolean to unicode."""
    if value is None:
        return None, None
    else:
        return unicode(int(bool(value))), None


def unicode_from_object_id(ctx, value):
    """Convert a MongoDB ObjectId to unicode."""
    if value is None:
        return None, None
    else:
        return unicode(value), None


def unicode_from_python_data(ctx, value):
    """Convert any Python data to unicode."""
    if value is None:
        return None, None
    elif isinstance(value, str):
        return value.decode('utf-8'), None
    else:
        return unicode(value), None


def url_name_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to a normalized string that can be used as a part of an URL path."""
    if value is None:
        return None, None
    else:
        from suq import strings
        for character in u'\n\r/?#':
            value = value.replace(character, u' ')
        value = strings.normalize(value, separator = u'_')
        return value or None, None


# Base compound filtering functions


name_from_unicode = compose(clean_empty, strip())
text_from_unicode = compose(clean_empty, strip(), clean_crlf)


# Compound filtering functions


balanced_ternary_digit_from_unicode = compose(balanced_ternary_digit_from_clean_unicode, name_from_unicode)
boolean_from_form_data = compose(default(False), boolean_from_clean_unicode, name_from_unicode)
boolean_from_unicode = compose(boolean_from_clean_unicode, name_from_unicode)
date_from_iso8601 = compose(date_from_clean_iso8601, name_from_unicode)
datetime_from_iso8601 = compose(datetime_from_clean_iso8601, name_from_unicode)
email_from_unicode = compose(email_from_clean_unicode, name_from_unicode)
float_from_unicode = compose(float_from_python_data, name_from_unicode)
geo_from_python_data = compose(
    sequence([
        compose(greater_or_equal(-90), less_or_equal(90), float_from_python_data), # latitude
        compose(greater_or_equal(-180), less_or_equal(180), float_from_python_data), # longitude
        compose(greater_or_equal(0), less_or_equal(9), integer_from_python_data), # accuracy
        ], ignore_extras = True),
    is_instance((list, tuple)),
    )
html_id_from_unicode = compose(match(html_id_re), name_from_unicode)
html_name_from_unicode = compose(match(html_id_re), name_from_unicode)
integer_from_unicode = compose(integer_from_python_data, name_from_unicode)
json_from_unicode = compose(json_from_clean_unicode, clean_empty, strip())
lang_from_unicode = compose(lang_from_clean_unicode, name_from_unicode)
object_id_from_unicode = compose(object_id_from_clean_unicode, name_from_unicode)
phone_from_unicode = compose(phone_from_clean_unicode, name_from_unicode)
slug_from_unicode = compose(slug_from_clean_unicode, name_from_unicode)
strictly_positive_integer_from_unicode = compose(greater_or_equal(1), integer_from_unicode)
url_name_from_unicode = compose(url_name_from_clean_unicode, name_from_unicode)


# Constructors that return functions using filters.


def to_value(filter):
    """Return a function that calls a filter and returns its result value, ignoring any error."""
    def f(ctx, *args, **kwargs):
        value, error = filter(ctx, *args, **kwargs)
        return value
    return f

