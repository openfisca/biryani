# -*- coding: utf-8 -*-


# Biryani -- A conversion and validation toolbox
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015 Emmanuel Raviart
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


"""Date and Time Related Converters

.. note:: Date & time converters are not in :mod:`biryani.baseconv`, because some of them depend from external
   libraries (``isodate`` & ``pytz``).
"""


import calendar
import datetime

import isodate
import pytz

from .baseconv import cleanup_line, function, pipe
from . import states


__all__ = [
    'date_to_datetime',
    'date_to_iso8601_str',
    'date_to_timestamp',
    'datetime_to_date',
    'datetime_to_iso8601_str',
    'datetime_to_timestamp',
    'iso8601_input_to_date',
    'iso8601_input_to_datetime',
    'iso8601_input_to_time',
    'iso8601_str_to_date',
    'iso8601_str_to_datetime',
    'iso8601_str_to_time',
    'set_datetime_tzinfo',
    'time_to_iso8601_str',
    'timestamp_to_date',
    'timestamp_to_datetime',
    ]


# Level-1 Converters


def date_to_datetime(value, state = None):
    """Convert a date object to a datetime.

    >>> import datetime
    >>> date_to_datetime(datetime.date(2012, 3, 4))
    (datetime.datetime(2012, 3, 4, 0, 0), None)
    >>> date_to_datetime(datetime.datetime(2012, 3, 4, 5, 6, 7))
    (datetime.datetime(2012, 3, 4, 0, 0), None)
    >>> date_to_datetime(None)
    (None, None)
    """
    if value is None:
        return value, None
    return datetime.datetime(value.year, value.month, value.day), None


def date_to_iso8601_str(value, state = None):
    """Convert a date to a string using ISO 8601 format.

    >>> date_to_iso8601_str(datetime.date(2012, 3, 4))
    (u'2012-03-04', None)
    >>> date_to_iso8601_str(datetime.datetime(2012, 3, 4, 5, 6, 7))
    (u'2012-03-04', None)
    >>> date_to_iso8601_str(None)
    (None, None)
    """
    if value is None:
        return value, None
    # the datetime strftime() methods require year >= 1900
    # return unicode(value.strftime('%Y-%m-%d')), None
    return u'{:04d}-{:02d}-{:02d}'.format(value.year, value.month, value.day), None


def date_to_timestamp(value, state = None):
    """Convert a datetime to a JavaScript timestamp.

    >>> date_to_timestamp(datetime.date(2012, 3, 4))
    (1330819200000, None)
    >>> date_to_timestamp(datetime.datetime(2012, 3, 4, 5, 6, 7))
    (1330837567000, None)
    >>> date_to_timestamp(None)
    (None, None)
    """
    if value is None:
        return value, None
    return int(calendar.timegm(value.timetuple()) * 1000), None


def datetime_to_date(value, state = None):
    """Convert a datetime object to a date.

    >>> datetime_to_date(datetime.datetime(2012, 3, 4, 5, 6, 7))
    (datetime.date(2012, 3, 4), None)
    >>> datetime_to_date(datetime.date(2012, 3, 4))
    Traceback (most recent call last):
    AttributeError:
    >>> datetime_to_date(None)
    (None, None)
    """
    if value is None:
        return value, None
    return value.date(), None


def datetime_to_iso8601_str(value, state = None):
    """Convert a datetime to a string using ISO 8601 format.

    >>> datetime_to_iso8601_str(datetime.datetime(2012, 3, 4, 5, 6, 7))
    (u'2012-03-04 05:06:07', None)
    >>> datetime_to_iso8601_str(datetime.date(2012, 3, 4))
    (u'2012-03-04 00:00:00', None)
    >>> datetime_to_iso8601_str(None)
    (None, None)
    """
    if value is None:
        return value, None
    return unicode(value.strftime('%Y-%m-%d %H:%M:%S')), None


def datetime_to_timestamp(value, state = None):
    """Convert a datetime to a JavaScript timestamp.

    >>> datetime_to_timestamp(datetime.datetime(2012, 3, 4, 5, 6, 7))
    (1330837567000, None)
    >>> datetime_to_timestamp(datetime.date(2012, 3, 4))
    (1330819200000, None)
    >>> datetime_to_timestamp(None)
    (None, None)
    """
    if state is None:
        state = states.default_state
    if not isinstance(value, datetime.datetime):
        return date_to_timestamp(value, state = state)
    utcoffset = value.utcoffset()
    if utcoffset is not None:
        value -= utcoffset
    return int(calendar.timegm(value.timetuple()) * 1000 + value.microsecond / 1000.0), None


def iso8601_str_to_date(value, state = None):
    """Convert a clean string in ISO 8601 format to a date.

    .. note:: For a converter that doesn't require a clean string, see :func:`iso8601_input_to_date`.

    >>> iso8601_str_to_date(u'2012-03-04')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_str_to_date(u'20120304')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_str_to_date(u'2012-03-04 05:06:07')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_str_to_date(u'2012-03-04T05:06:07')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_str_to_date(u'2012-03-04 05:06:07+01:00')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_str_to_date(u'2012-03-04 05:06:07-02:00')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_str_to_date(u'2012-03-04 05:06:07 +01:00')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_str_to_date(u'2012-03-04 05:06:07 -02:00')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_str_to_date(u'20120304 05:06:07')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_str_to_date(u'today')
    (u'today', u'Value must be a date in ISO 8601 format')
    >>> iso8601_str_to_date(u'')
    (u'', u'Value must be a date in ISO 8601 format')
    >>> iso8601_str_to_date(None)
    (None, None)
    """
    if value is None:
        return value, None
    if state is None:
        state = states.default_state
    try:
        return isodate.parse_date(value), None
    except (isodate.ISO8601Error, ValueError):
        return value, state._(u'Value must be a date in ISO 8601 format')


def iso8601_str_to_datetime(value, state = None):
    """Convert a clean string in ISO 8601 format to a datetime.

    .. note:: For a converter that doesn't require a clean string, see :func:`iso8601_input_to_datetime`.

    >>> iso8601_str_to_datetime(u'2012-03-04')
    (datetime.datetime(2012, 3, 4, 0, 0), None)
    >>> iso8601_str_to_datetime(u'20120304')
    (datetime.datetime(2012, 3, 4, 0, 0), None)
    >>> iso8601_str_to_datetime(u'2012-03-04 05:06:07')
    (datetime.datetime(2012, 3, 4, 5, 6, 7), None)
    >>> iso8601_str_to_datetime(u'2012-03-04T05:06:07')
    (datetime.datetime(2012, 3, 4, 5, 6, 7), None)
    >>> iso8601_str_to_datetime(u'2012-03-04 05:06:07+01:00')
    (datetime.datetime(2012, 3, 4, 4, 6, 7), None)
    >>> iso8601_str_to_datetime(u'2012-03-04 05:06:07-02:00')
    (datetime.datetime(2012, 3, 4, 7, 6, 7), None)
    >>> iso8601_str_to_datetime(u'2012-03-04 05:06:07 +01:00')
    (datetime.datetime(2012, 3, 4, 4, 6, 7), None)
    >>> iso8601_str_to_datetime(u'2012-03-04 05:06:07 -02:00')
    (datetime.datetime(2012, 3, 4, 7, 6, 7), None)
    >>> iso8601_str_to_datetime(u'20120304 05:06:07')
    (datetime.datetime(2012, 3, 4, 5, 6, 7), None)
    >>> iso8601_str_to_datetime(u'now')
    (u'now', u'Value must be a date-time in ISO 8601 format')
    >>> iso8601_str_to_datetime(u'')
    (u'', u'Value must be a date-time in ISO 8601 format')
    >>> iso8601_str_to_datetime(None)
    (None, None)
    """
    if value is None:
        return value, None
    if state is None:
        state = states.default_state
    original_value = value
    if u'T' not in value:
        if u' ' in value:
            # Accept a " " instead of a "T" for time separator.
            value = value.replace(u' ', u'T', 1)
        else:
            # Time seems to be missing. Add a zero time.
            value += u'T00:00:00'
    # Parsing fails when time zone is preceded with a space. So we remove space before "+" and "-".
    while u' +' in value:
        value = value.replace(u' +', '+')
    while u' -' in value:
        value = value.replace(u' -', '-')
    try:
        value = isodate.parse_datetime(value)
    except (isodate.ISO8601Error, ValueError):
        return original_value, state._(u'Value must be a date-time in ISO 8601 format')
    if value.tzinfo is not None:
        # Convert datetime to UTC.
        value = value.astimezone(pytz.utc).replace(tzinfo = None)
    return value, None


def iso8601_str_to_time(value, state = None):
    """Convert a clean string in ISO 8601 format to a time.

    .. note:: For a converter that doesn't require a clean string, see :func:`iso8601_input_to_time`.

    >>> iso8601_str_to_time(u'05:06:07')
    (datetime.time(5, 6, 7), None)
    >>> iso8601_str_to_time(u'T05:06:07')
    (datetime.time(5, 6, 7), None)
    >>> iso8601_str_to_time(u'05:06:07+01:00')
    (datetime.time(4, 6, 7), None)
    >>> iso8601_str_to_time(u'05:06:07-02:00')
    (datetime.time(7, 6, 7), None)
    >>> iso8601_str_to_time(u'05:06:07 +01:00')
    (datetime.time(4, 6, 7), None)
    >>> iso8601_str_to_time(u'05:06:07 -02:00')
    (datetime.time(7, 6, 7), None)
    >>> iso8601_str_to_time(u'05:06:07')
    (datetime.time(5, 6, 7), None)
    >>> iso8601_str_to_time(u'now')
    (u'now', u'Value must be a time in ISO 8601 format')
    >>> iso8601_str_to_time(u'')
    (u'', u'Value must be a time in ISO 8601 format')
    >>> iso8601_str_to_time(None)
    (None, None)
    """
    if value is None:
        return value, None
    if state is None:
        state = states.default_state
    # Parsing fails when time zone is preceded with a space. So we remove space before "+" and "-".
    while u' +' in value:
        value = value.replace(u' +', '+')
    while u' -' in value:
        value = value.replace(u' -', '-')
    try:
        value = isodate.parse_time(value)
    except isodate.ISO8601Error:
        return value, state._(u'Value must be a time in ISO 8601 format')
    if value.tzinfo is not None:
        # Convert time to UTC (using a temporary datetime).
        datetime_value = datetime.datetime.combine(datetime.date(2, 2, 2), value)
        datetime_value = datetime_value.astimezone(pytz.utc).replace(tzinfo = None)
        value = datetime_value.time()
    return value, None


def set_datetime_tzinfo(tzinfo = None):
    """Return a converter that sets or clears the field tzinfo of a datetime.

    >>> import datetime, pytz
    >>> set_datetime_tzinfo()(datetime.datetime(2011, 1, 2, 3, 4, 5))
    (datetime.datetime(2011, 1, 2, 3, 4, 5), None)
    >>> datetime.datetime(2011, 1, 2, 3, 4, 5, tzinfo = pytz.utc)
    datetime.datetime(2011, 1, 2, 3, 4, 5, tzinfo=<UTC>)
    >>> set_datetime_tzinfo()(datetime.datetime(2011, 1, 2, 3, 4, 5, tzinfo = pytz.utc))
    (datetime.datetime(2011, 1, 2, 3, 4, 5), None)
    >>> set_datetime_tzinfo(pytz.utc)(datetime.datetime(2011, 1, 2, 3, 4, 5))
    (datetime.datetime(2011, 1, 2, 3, 4, 5, tzinfo=<UTC>), None)
    """
    return function(lambda value: value.replace(tzinfo = tzinfo))


def time_to_iso8601_str(value, state = None):
    """Convert a time to a string using ISO 8601 format.

    >>> time_to_iso8601_str(datetime.time(5, 6, 7))
    (u'05:06:07', None)
    >>> time_to_iso8601_str(None)
    (None, None)
    """
    if value is None:
        return value, None
    return unicode(value.strftime('%H:%M:%S')), None


def timestamp_to_date(value, state = None):
    """Convert a JavaScript timestamp to a date.

    >>> timestamp_to_date(123456789.123)
    (datetime.date(1970, 1, 2), None)
    >>> timestamp_to_date(u'123456789.123')
    Traceback (most recent call last):
    TypeError:
    >>> pipe(input_to_float, timestamp_to_date)(u'123456789.123')
    (datetime.date(1970, 1, 2), None)
    >>> timestamp_to_date(None)
    (None, None)
    """
    if value is None:
        return value, None
    if state is None:
        state = states.default_state
    try:
        return datetime.date.fromtimestamp(value / 1000.0), None
    except ValueError:
        return value, state._(u'Value must be a timestamp')


def timestamp_to_datetime(value, state = None):
    """Convert a JavaScript timestamp to a datetime.

    .. note:: Since a timestamp has no timezone, the generated datetime has no *tzinfo* attribute.
       Use :func:`set_datetime_tzinfo` to add one.

    >>> timestamp_to_datetime(123456789.123)
    (datetime.datetime(1970, 1, 2, 11, 17, 36, 789123), None)
    >>> import pytz
    >>> pipe(timestamp_to_datetime, set_datetime_tzinfo(pytz.utc))(123456789.123)
    (datetime.datetime(1970, 1, 2, 11, 17, 36, 789123, tzinfo=<UTC>), None)
    >>> timestamp_to_datetime(u'123456789.123')
    Traceback (most recent call last):
    TypeError:
    >>> pipe(input_to_float, timestamp_to_datetime)(u'123456789.123')
    (datetime.datetime(1970, 1, 2, 11, 17, 36, 789123), None)
    >>> timestamp_to_datetime(None)
    (None, None)
    """
    if value is None:
        return value, None
    if state is None:
        state = states.default_state
    try:
        # Since a timestamp doesn't containe timezone information, the generated datetime has no timezone (ie naive
        # datetime), so we don't use pytz.utc.
        # return datetime.datetime.fromtimestamp(value / 1000.0, pytz.utc), None
        return datetime.datetime.fromtimestamp(value / 1000.0), None
    except ValueError:
        return value, state._(u'Value must be a timestamp')


# Level-2 Converters


iso8601_input_to_date = pipe(cleanup_line, iso8601_str_to_date)
"""Convert a string in ISO 8601 format to a date.

    >>> iso8601_input_to_date(u'2012-03-04')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_input_to_date(u'20120304')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_input_to_date(u'2012-03-04 05:06:07')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_input_to_date(u'2012-03-04T05:06:07')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_input_to_date(u'2012-03-04 05:06:07+01:00')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_input_to_date(u'2012-03-04 05:06:07-02:00')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_input_to_date(u'2012-03-04 05:06:07 +01:00')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_input_to_date(u'2012-03-04 05:06:07 -02:00')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_input_to_date(u'20120304 05:06:07')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_input_to_date(u'   2012-03-04   ')
    (datetime.date(2012, 3, 4), None)
    >>> iso8601_input_to_date(u'today')
    (u'today', u'Value must be a date in ISO 8601 format')
    >>> iso8601_input_to_date(u'   ')
    (None, None)
    >>> iso8601_input_to_date(None)
    (None, None)
    """

iso8601_input_to_datetime = pipe(cleanup_line, iso8601_str_to_datetime)
"""Convert a string in ISO 8601 format to a datetime.

    >>> iso8601_input_to_datetime(u'2012-03-04')
    (datetime.datetime(2012, 3, 4, 0, 0), None)
    >>> iso8601_input_to_datetime(u'20120304')
    (datetime.datetime(2012, 3, 4, 0, 0), None)
    >>> iso8601_input_to_datetime(u'2012-03-04 05:06:07')
    (datetime.datetime(2012, 3, 4, 5, 6, 7), None)
    >>> iso8601_input_to_datetime(u'2012-03-04T05:06:07')
    (datetime.datetime(2012, 3, 4, 5, 6, 7), None)
    >>> iso8601_input_to_datetime(u'2012-03-04 05:06:07+01:00')
    (datetime.datetime(2012, 3, 4, 4, 6, 7), None)
    >>> iso8601_input_to_datetime(u'2012-03-04 05:06:07-02:00')
    (datetime.datetime(2012, 3, 4, 7, 6, 7), None)
    >>> iso8601_input_to_datetime(u'2012-03-04 05:06:07 +01:00')
    (datetime.datetime(2012, 3, 4, 4, 6, 7), None)
    >>> iso8601_input_to_datetime(u'2012-03-04 05:06:07 -02:00')
    (datetime.datetime(2012, 3, 4, 7, 6, 7), None)
    >>> iso8601_input_to_datetime(u'20120304 05:06:07')
    (datetime.datetime(2012, 3, 4, 5, 6, 7), None)
    >>> iso8601_input_to_datetime(u'   2012-03-04 05:06:07   ')
    (datetime.datetime(2012, 3, 4, 5, 6, 7), None)
    >>> iso8601_input_to_datetime(u'now')
    (u'now', u'Value must be a date-time in ISO 8601 format')
    >>> iso8601_input_to_datetime(u'   ')
    (None, None)
    >>> iso8601_input_to_datetime(None)
    (None, None)
    """

iso8601_input_to_time = pipe(cleanup_line, iso8601_str_to_time)
"""Convert a string in ISO 8601 format to a time.

    >>> iso8601_input_to_time(u'05:06:07')
    (datetime.time(5, 6, 7), None)
    >>> iso8601_input_to_time(u'T05:06:07')
    (datetime.time(5, 6, 7), None)
    >>> iso8601_input_to_time(u'05:06:07+01:00')
    (datetime.time(4, 6, 7), None)
    >>> iso8601_input_to_time(u'05:06:07-02:00')
    (datetime.time(7, 6, 7), None)
    >>> iso8601_input_to_time(u'05:06:07 +01:00')
    (datetime.time(4, 6, 7), None)
    >>> iso8601_input_to_time(u'05:06:07 -02:00')
    (datetime.time(7, 6, 7), None)
    >>> iso8601_input_to_time(u'05:06:07')
    (datetime.time(5, 6, 7), None)
    >>> iso8601_input_to_time(u'   05:06:07   ')
    (datetime.time(5, 6, 7), None)
    >>> iso8601_input_to_time(u'now')
    (u'now', u'Value must be a time in ISO 8601 format')
    >>> iso8601_input_to_time(u'   ')
    (None, None)
    >>> iso8601_input_to_time(None)
    (None, None)
    """
