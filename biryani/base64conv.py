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


"""Base64 Related Converters"""


import base64

from . import states


__all__ = [
    'base64_to_bytes',
    'bytes_to_base64',
    'make_base64url_to_bytes',
    'make_bytes_to_base64url',
    ]


def base64_to_bytes(value, state = None):
    """Decode data from a base64 encoding.

    >>> base64_to_bytes(u'SGVsbG8gV29ybGQ=')
    ('Hello World', None)
    >>> base64_to_bytes(u'SGVsbG8gV29ybGQ')
    (u'SGVsbG8gV29ybGQ', u'Invalid base64 string')
    >>> base64_to_bytes(u'Hello World')
    (u'Hello World', u'Invalid base64 string')
    >>> base64_to_bytes(u'')
    ('', None)
    >>> base64_to_bytes(None)
    (None, None)
    """
    if value is None:
        return value, None
    if state is None:
        state = states.default_state
    value_str = str(value) if isinstance(value, unicode) else value
    try:
        decoded_value = base64.b64decode(value_str)
    except TypeError:
        return value, state._(u'Invalid base64 string')
    return decoded_value, None


def bytes_to_base64(value, state = None):
    """Converts a string or bytes to a base64 encoding.

    >>> bytes_to_base64('Hello World')
    (u'SGVsbG8gV29ybGQ=', None)
    >>> bytes_to_base64(u'Hello World')
    (u'SGVsbG8gV29ybGQ=', None)
    >>> bytes_to_base64(u'')
    (u'', None)
    >>> bytes_to_base64(None)
    (None, None)
    """
    if value is None:
        return value, None
    if isinstance(value, unicode):
        value = value.encode('utf-8')
    encoded_value = base64.b64encode(value)
    return unicode(encoded_value), None


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
    def base64url_to_bytes(value, state = None):
        if value is None:
            return value, None
        if state is None:
            state = states.default_state
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
    return base64url_to_bytes


def make_bytes_to_base64url(remove_padding = False):
    """Return a converter that converts a string or bytes to an URL-safe base64 encoding.

    .. note:: To remove trailing (non URL-safe) "=", set ``remove_padding`` to ``True``.

    >>> make_bytes_to_base64url()('Hello World')
    (u'SGVsbG8gV29ybGQ=', None)
    >>> make_bytes_to_base64url()(u'Hello World')
    (u'SGVsbG8gV29ybGQ=', None)
    >>> make_bytes_to_base64url(remove_padding = True)(u'Hello World')
    (u'SGVsbG8gV29ybGQ', None)
    >>> make_bytes_to_base64url()(u'')
    (u'', None)
    >>> make_bytes_to_base64url()(None)
    (None, None)
    """
    def bytes_to_base64url(value, state = None):
        if value is None:
            return value, None
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        encoded_value = base64.urlsafe_b64encode(value)
        if remove_padding:
            encoded_value = encoded_value.rstrip('=')
        return unicode(encoded_value), None
    return bytes_to_base64url
