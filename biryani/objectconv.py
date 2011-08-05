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


"""Object Related Converters"""


from . import baseconv as conv
from . import states


__all__ = [
    'object_to_clean_dict',
    'object_to_dict',
    ]


object_to_clean_dict = conv.function(lambda instance: dict(
    (name, value)
    for name, value in instance.__dict__.iteritems()
    if getattr(instance.__class__, name, None) is not value
    ))
"""Convert an object's instance to a dictionary, by extracting the attributes whose value differs from the ones defined
    in the object's class.

    .. note:: Use this converter instead of :func:`object_to_dict` when you want to remove defaut values from generated
       dictionary.

    >>> class C(object):
    ...     a = 1
    >>> c = C()
    >>> object_to_clean_dict(c)
    ({}, None)
    >>> c.a = 2
    >>> object_to_clean_dict(c)
    ({'a': 2}, None)
    >>> d = C()
    >>> d.a = 2
    >>> d.b = 3
    >>> object_to_clean_dict(d)
    ({'a': 2, 'b': 3}, None)
    >>> e = C()
    >>> e.a = 1
    >>> object_to_clean_dict(e)
    ({}, None)
    >>> f = C()
    >>> f.a = 1
    >>> f.b = 2
    >>> object_to_clean_dict(e)
    ({'b': 2}, None)
    >>> object_to_clean_dict(None)
    (None, None)
    >>> object_to_clean_dict(42)
    Traceback (most recent call last):
    AttributeError: 'int' object has no attribute '__dict__'
    """

object_to_dict = conv.function(lambda instance: getattr(instance, '__dict__'))
"""Convert an object's instance to a dictionary, by returning its ``__dict__`` atribute.

    .. note:: Use converter :func:`object_to_clean_dict` when you want to remove defaut values from generated
       dictionary.

    >>> class C(object):
    ...     a = 1
    >>> c = C()
    >>> object_to_dict(c)
    ({}, None)
    >>> c.a = 2
    >>> object_to_dict(c)
    ({'a': 2}, None)
    >>> d = C()
    >>> d.a = 2
    >>> d.b = 3
    >>> object_to_dict(d)
    ({'a': 2, 'b': 3}, None)
    >>> e = C()
    >>> e.a = 1
    >>> object_to_dict(e)
    ({'a': 1}, None)
    >>> f = C()
    >>> f.a = 1
    >>> f.b = 2
    >>> object_to_dict(e)
    ({'a': 1, 'b': 2}, None)
    >>> object_to_dict(None)
    (None, None)
    >>> object_to_dict(42)
    Traceback (most recent call last):
    AttributeError: 'int' object has no attribute '__dict__'
    """


# Level-1 Converters


def clean_iso8601_to_date(value, state = states.default_state):
    """Convert a clean string in ISO 8601 format to a date."""
    if value is None:
        return value, None
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
        return value, state._('Value must be a date in ISO 8601 format')


def clean_iso8601_to_datetime(value, state = states.default_state):
    """Convert a clean string in ISO 8601 format to a datetime."""
    if value is None:
        return value, None
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
        return value, state._('Value must be a date-time in ISO 8601 format')


def date_to_datetime(value, state = states.default_state):
    """Convert a date object to a datetime."""
    if value is None:
        return value, None
    return datetime.datetime(value.year, value.month, value.day), None


def date_to_iso8601(value, state = states.default_state):
    """Convert a date to a string using ISO 8601 format."""
    if value is None:
        return value, None
    return unicode(value.strftime('%Y-%m-%d')), None


def date_to_timestamp(value, state = states.default_state):
    """Convert a datetime to a JavaScript timestamp."""
    if value is None:
        return value, None
    return int(calendar.timegm(value.timetuple()) * 1000), None


def datetime_to_date(value, state = states.default_state):
    """Convert a datetime object to a date."""
    if value is None:
        return value, None
    return value.date(), None


def datetime_to_iso8601(value, state = states.default_state):
    """Convert a datetime to a string using ISO 8601 format."""
    if value is None:
        return value, None
    return unicode(value.strftime('%Y-%m-%d %H:%M:%S')), None


def datetime_to_timestamp(value, state = states.default_state):
    """Convert a datetime to a JavaScript timestamp."""
    if value is None:
        return value, None
    utcoffset = value.utcoffset()
    if utcoffset is not None:
        value -= utcoffset
    return int(calendar.timegm(value.timetuple()) * 1000 + value.microsecond / 1000), None


def timestamp_to_date(value, state = states.default_state):
    """Convert a JavaScript timestamp to a date."""
    if value is None:
        return value, None
    try:
        return datetime.date.fromtimestamp(value / 1000), None
    except ValueError:
        return value, state._('Value must be a timestamp')


def timestamp_to_datetime(value, state = states.default_state):
    """Convert a JavaScript timestamp to a datetime."""
    if value is None:
        return value, None
    try:
        return datetime.datetime.fromtimestamp(value / 1000, pytz.utc), None
    except ValueError:
        return value, state._('Value must be a timestamp')


# Level-2 Converters


iso8601_to_date = conv.pipe(conv.cleanup_line, clean_iso8601_to_date)
iso8601_to_datetime = conv.pipe(conv.cleanup_line, clean_iso8601_to_datetime)

