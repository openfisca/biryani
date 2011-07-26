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


"""Date and Time Related Converters"""


import calendar
import datetime

import mx.DateTime
import pytz

from . import baseconv as conv
from . import states


__all__ = [
    'clean_iso8601_to_date',
    'clean_iso8601_to_datetime',
    'date_to_datetime',
    'date_to_iso8601',
    'date_to_timestamp',
    'datetime_to_date',
    'datetime_to_iso8601',
    'datetime_to_timestamp',
    'iso8601_to_date',
    'iso8601_to_datetime',
    'timestamp_to_date',
    'timestamp_to_datetime',
    ]


# Level-1 Converters


def clean_iso8601_to_date(value, state = states.default_state):
    """Convert a clean unicode string in ISO 8601 format to a date."""
    if value is None:
        return None, None
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
        return None, state._('Value must be a date in ISO 8601 format')


def clean_iso8601_to_datetime(value, state = states.default_state):
    """Convert a clean unicode string in ISO 8601 format to a datetime."""
    if value is None:
        return None, None
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
        return None, state._('Value must be a date-time in ISO 8601 format')


def date_to_datetime(value, state = states.default_state):
    """Convert a date object to a datetime."""
    if value is None:
        return None, None
    return datetime.datetime(value.year, value.month, value.day), None


def date_to_iso8601(value, state = states.default_state):
    """Convert a date to unicode string using ISO 8601 format."""
    if value is None:
        return None, None
    return unicode(value.strftime('%Y-%m-%d')), None


def date_to_timestamp(value, state = states.default_state):
    """Convert a datetime to a JavaScript timestamp."""
    if value is None:
        return None, None
    return int(calendar.timegm(value.timetuple()) * 1000), None


def datetime_to_date(value, state = states.default_state):
    """Convert a datetime object to a date."""
    if value is None:
        return None, None
    return value.date(), None


def datetime_to_iso8601(value, state = states.default_state):
    """Convert a datetime to unicode string using ISO 8601 format."""
    if value is None:
        return None, None
    return unicode(value.strftime('%Y-%m-%d %H:%M:%S')), None


def datetime_to_timestamp(value, state = states.default_state):
    """Convert a datetime to a JavaScript timestamp."""
    if value is None:
        return None, None
    utcoffset = value.utcoffset()
    if utcoffset is not None:
        value -= utcoffset
    return int(calendar.timegm(value.timetuple()) * 1000 + value.microsecond / 1000), None


def timestamp_to_date(value, state = states.default_state):
    """Convert a JavaScript timestamp to a date."""
    if value is None:
        return None, None
    try:
        return datetime.date.fromtimestamp(value / 1000), None
    except ValueError:
        return None, state._('Value must be a timestamp')


def timestamp_to_datetime(value, state = states.default_state):
    """Convert a JavaScript timestamp to a datetime."""
    if value is None:
        return None, None
    try:
        return datetime.datetime.fromtimestamp(value / 1000, pytz.utc), None
    except ValueError:
        return None, state._('Value must be a timestamp')


# Level-2 Converters


iso8601_to_date = conv.pipe(conv.cleanup_line, clean_iso8601_to_date)
iso8601_to_datetime = conv.pipe(conv.cleanup_line, clean_iso8601_to_datetime)

