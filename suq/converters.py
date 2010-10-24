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


domain_re = re.compile(r'''
    (?:[a-z0-9][a-z0-9\-]{0,62}\.)+ # (sub)domain - alpha followed by 62max chars (63 total)
    [a-z]{2,}$                      # TLD
    ''', re.I | re.VERBOSE)
N_ = lambda s: s
object_id_re = re.compile(r'[\da-f]{24}$')
username_re = re.compile(r"[^ \t\n\r@<>()]+$", re.I)


# Constructors that return filters


def assert_ok(filter):
    """Return a compound filter that applies a filter, raising an assertion error if an error occurs."""
    def f(ctx, value):
        value, error = filter(ctx, value)
        assert error is None, error
        return value, error
    return f


def compose(*filters):
    """Return a compound filter that applies each of its filters (in reverse order) till the end or an error occurs."""
    def f(ctx, value):
        for filter in reversed(filters):
            value, error = filter(ctx, value)
            if error is not None:
                return None, error
        return value, None
    return f


def default(constant):
    """Return a filter that replace missing value by given one."""
    return lambda value: (constant, None) if value is None else (value, None)


def greater_or_equal(constant):
    """Return a filter that accepts only values greater than or equal to given constant."""
    def f(ctx, value):
        if constant is None or value is None or value >= constant:
            return value, None
        else:
            _ = ctx.translator.ugettext
            return None, _('Value must be greater than or equal to %s') % constant
    return f


def less_or_equal(constant):
    """Return a filter that accepts only values less than or equal to given constant."""
    def f(ctx, value):
        if constant is None or value is None or value <= constant:
            return value, None
        else:
            _ = ctx.translator.ugettext
            return None, _('Value must be less than or equal to %s') % constant
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


def restrict(values):
    """Return a filter that accepts only values belonging to a given set (or list or...)."""
    def f(ctx, value):
        if value is None or values is None or value in values:
            return value, None
        else:
            _ = ctx.translator.ugettext
            return None, _('Value must be one of %s') % list(values)
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
            elif schemes is not None and scheme not in schemes:
                _ = ctx.translator.ugettext
                return None, _('Scheme must belongs to %s') % sorted(schemes)
            else:
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


def url_from_unicode(full = False, remove_fragment = False, schemes = None):
    """Return a filter that converts an unicode string to an URL."""
    return compose(
        url_from_clean_unicode(full = full, remove_fragment = remove_fragment, schemes = schemes),
        clean_empty,
        strip(),
        )


# Simple filtering functions (without (value, error) parameter)


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


def email_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to an email address."""
    if value is None:
        return None, None
    else:
        value = value.lower()
        try:
            username, domain = value.split('@', 1)
        except ValueError:
            return None, _('An email must contain exactly one "@".')
        if not username_re.match(username):
            return None, _('Invalid username')
        if not domain_re.match(domain) and domain != 'localhost':
            return None, _('Invalid domain name')
        return value, None


def empty_string_from_none(ctx, value):
    """Replace None value with empty string."""
    return u'' if value is None else value, None


def float_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to a float."""
    if value is None:
        return None, None
    else:
        try:
            return float(value), None
        except ValueError:
            _ = ctx.translator.ugettext
            return None, _('Value must be a float')


def integer_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to an integer."""
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
        unicode(value.strftime('%Y-%m-%d %H:%M:%S')), None


def json_from_clean_unicode(ctx, value):
    """Convert a clean unicode string to a JSON value."""
    if value is None:
        return None, None
    else:
        import simplejson as json
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
                    return '+%s %s %s %s' % (value[2:5], value[5:7], value[7:9], value[9:11]), None
                else:
                    _ = ctx.translator.ugettext
                    return None, _('Wrong number of digits for phone number of %s') % _(country)
            else:
                _ = ctx.translator.ugettext
                return None, _('Unknown international phone number')
        elif len(value) == 4:
            return value, None
        elif len(value) == 10:
            if value[0] != '0':
                _ = ctx.translator.ugettext
                return None, _('Unexpected first digit in phone number: %s instead of 0') % value[0]
            else:
                mask = '+33 %s%s %s %s %s' if value[1] == '8' else '+33 %s %s %s %s %s'
                return mask % (value[1], value[2:4], value[4:6], value[6:8], value[8:10]), None
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


def unicode_from_boolean(ctx, value):
    """Convert a boolean to unicode."""
    if value is None:
        return None, None
    else:
        return unicode(int(bool(value))), None


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
        return value, None


# Compound simple filtering functions


boolean_from_unicode = compose(boolean_from_clean_unicode, clean_empty, strip())
date_from_iso8601 = compose(date_from_clean_iso8601, clean_empty, strip())
datetime_from_iso8601 = compose(datetime_from_clean_iso8601, clean_empty, strip())
email_from_unicode = compose(email_from_clean_unicode, clean_empty, strip())
float_from_unicode = compose(float_from_clean_unicode, clean_empty, strip())
integer_from_unicode = compose(integer_from_clean_unicode, clean_empty, strip())
json_from_unicode = compose(json_from_clean_unicode, clean_empty, strip())
lang_from_unicode = compose(lang_from_clean_unicode, clean_empty, strip())
object_id_from_unicode = compose(object_id_from_clean_unicode, clean_empty, strip())
phone_from_unicode = compose(phone_from_clean_unicode, clean_empty, strip())
strictly_positive_integer_from_unicode = compose(greater_or_equal(1), integer_from_clean_unicode, clean_empty, strip())
text_from_unicode = compose(clean_crlf, strip(), clean_empty, strip(), clean_crlf)
url_name_from_unicode = compose(url_name_from_clean_unicode, clean_empty, strip())


# Constructors that return functions using filters.


def to_value(filter):
    """Return a function that calls a filtersand returns its result value, ignoring any error."""
    def f(ctx, value):
        value, error = filter(ctx, value)
        return value
    return f

