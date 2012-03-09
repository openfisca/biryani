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


"""Web Related Converters

.. note:: Web converters are not in :mod:`biryani.baseconv`, because they use web-specific modules.
"""


import base64
import json

from . import baseconv as conv
from . import states


__all__ = [
    'make_base64url_to_bytes',
    'make_bytes_to_base64url',
    'make_json_to_str',
    'make_str_to_json',
    ]


def make_base64url_to_bytes(add_padding = False):
    """Return a converter that decodes data from an URL-safe base64 encoding.

    .. note:: To handle values without padding "=", set ``add_padding`` to ``True``.

    >>> make_base64url_to_bytes()(u'SGVsbG8gV29ybGQ=')
    ('Hello World', None)
    >>> make_base64url_to_bytes(add_padding = True)(u'SGVsbG8gV29ybGQ')
    ('Hello World', None)
    >>> make_base64url_to_bytes(add_padding = True)(u'SGVsbG8gV29ybGQ=')
    ('Hello World', None)
    >>> make_base64url_to_bytes()(u'SGVsbG8gV29ybGQ')
    (u'SGVsbG8gV29ybGQ', u'Invalid base64url string')
    >>> make_base64url_to_bytes()(u'Hello World')
    (u'Hello World', u'Invalid base64url string')
    >>> make_base64url_to_bytes()(u'')
    ('', None)
    >>> make_base64url_to_bytes()(None)
    (None, None)
    """
    def base64url_to_str(value, state = states.default_state):
        if value is None:
            return value, None
        value_str = str(value) if isinstance(value, unicode) else value
        if add_padding:
            len_mod4 = len(value_str) % 4
            if len_mod4 == 1:
                return value, state._(u'Invalid base64url string')
            if len_mod4 > 0:
                value_str += '=' * (4 - len_mod4)
        try:
            decoded_value = base64.urlsafe_b64decode(value_str)
        except TypeError:
            return value, state._(u'Invalid base64url string')
        return decoded_value, None
    return base64url_to_str


def make_bytes_to_base64url(remove_padding = False):
    """Return a converter that converts a string or bytes to an URL-safe base64 encoding.

    .. note:: To remove trailing (non URL-safe) "=", set ``remove_padding`` to ``True``.

    >>> make_bytes_to_base64url()(u'Hello World')
    (u'SGVsbG8gV29ybGQ=', None)
    >>> make_bytes_to_base64url(remove_padding = True)(u'Hello World')
    (u'SGVsbG8gV29ybGQ', None)
    >>> make_bytes_to_base64url()(u'')
    (u'', None)
    >>> make_bytes_to_base64url()(None)
    (None, None)
    """
    def str_to_base64url(value, state = states.default_state):
        if value is None:
            return value, None
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        encoded_value = base64.urlsafe_b64encode(value)
        if remove_padding:
            encoded_value = encoded_value.rstrip('=')
        return unicode(encoded_value), None
    return str_to_base64url


def make_json_to_str(*args, **kwargs):
    """Return a converter that encodes a JSON data to a string.

    >>> make_json_to_str()({u'a': 1, u'b': [2, u'three']})
    (u'{"a": 1, "b": [2, "three"]}', None)
    >>> make_json_to_str()(u'Hello World')
    (u'"Hello World"', None)
    >>> make_json_to_str()(set([1, 2, 3]))
    (set([1, 2, 3]), u'Invalid JSON')
    >>> make_json_to_str()(u'')
    (u'""', None)
    >>> make_json_to_str()(None)
    (None, None)
    """
    def json_to_str(value, state = states.default_state):
        if value is None:
            return value, None
        try:
            value_str = unicode(json.dumps(value, *args, **kwargs))
        except TypeError, error:
            return value, state._(u'Invalid JSON')
        return value_str, None
    return json_to_str


def make_str_to_json(*args, **kwargs):
    """Return a converter that decodes a string to a JSON data.

    >>> make_str_to_json()(u'{"a": 1, "b": [2, "three"]}')
    ({u'a': 1, u'b': [2, u'three']}, None)
    >>> make_str_to_json()(u'Hello World')
    (u'Hello World', u'Invalid JSON')
    >>> make_str_to_json()(u'{"a": 1, "b":')
    (u'{"a": 1, "b":', u'Invalid JSON')
    >>> make_str_to_json()(u'')
    (u'', u'Invalid JSON')
    >>> make_str_to_json()(None)
    (None, None)
    """
    def str_to_json(value, state = states.default_state):
        if value is None:
            return value, None
        try:
            value_json = json.loads(value, *args, **kwargs)
        except ValueError, error:
            return value, state._(u'Invalid JSON')
        return value_json, None
    return str_to_json

