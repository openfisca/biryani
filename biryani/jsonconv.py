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


"""JSON Related Converters"""


import json

from .baseconv import cleanup_line, pipe
from . import states


__all__ = [
    'make_input_to_json',
    'make_json_to_str',
    'make_str_to_json',
    ]


# Level-1 Converters


def make_json_to_str(*args, **kwargs):
    """Return a converter that encodes a JSON data to a string.

    >>> make_json_to_str()({u'a': 1, u'b': [2, u'three']})
    (u'{"a": 1, "b": [2, "three"]}', None)
    >>> make_json_to_str()(u'Hello World')
    (u'"Hello World"', None)
    >>> make_json_to_str(ensure_ascii = False, indent = 2, sort_keys = True)({u'a': 1, u'b': [2, u'three']})
    (u'{\\n  "a": 1, \\n  "b": [\\n    2, \\n    "three"\\n  ]\\n}', None)
    >>> make_json_to_str()(set([1, 2, 3]))
    (set([1, 2, 3]), u'Invalid JSON')
    >>> make_json_to_str()(u'')
    (u'""', None)
    >>> make_json_to_str()(None)
    (None, None)
    """
    def json_to_str(value, state = None):
        if value is None:
            return value, None
        if state is None:
            state = states.default_state
        try:
            value_str = unicode(json.dumps(value, *args, **kwargs))
        except TypeError:
            return value, state._(u'Invalid JSON')
        return value_str, None
    return json_to_str


def make_str_to_json(*args, **kwargs):
    """Return a converter that decodes a clean string to a JSON data.

    .. note:: For a converter that doesn't require a clean string, see :func:`make_input_to_json`.

    >>> make_str_to_json()(u'{"a": 1, "b": [2, "three"]}')
    ({u'a': 1, u'b': [2, u'three']}, None)
    >>> make_str_to_json()(u'null')
    (None, None)
    >>> make_str_to_json()(u'Hello World')
    (u'Hello World', u'Invalid JSON')
    >>> make_str_to_json()(u'{"a": 1, "b":')
    (u'{"a": 1, "b":', u'Invalid JSON')
    >>> make_str_to_json()(u'')
    (u'', u'Invalid JSON')
    >>> make_str_to_json()(None)
    (None, None)
    """
    def str_to_json(value, state = None):
        if value is None:
            return value, None
        if state is None:
            state = states.default_state
        if isinstance(value, str):
            # Ensure that json.loads() uses unicode strings.
            try:
                value = value.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    value = value.decode('cp1252')
                except UnicodeDecodeError:
                    return value, state._(u'''JSON doesn't use "utf-8" encoding''')
        try:
            return json.loads(value, *args, **kwargs), None
        except ValueError:
            return value, state._(u'Invalid JSON')
    return str_to_json


# Level-2 Converters


def make_input_to_json(*args, **kwargs):
    """Return a converter that decodes a string to a JSON data.

    >>> make_input_to_json()(u'{"a": 1, "b": [2, "three"]}')
    ({u'a': 1, u'b': [2, u'three']}, None)
    >>> make_input_to_json()(u'null')
    (None, None)
    >>> make_input_to_json()(u'Hello World')
    (u'Hello World', u'Invalid JSON')
    >>> make_input_to_json()(u'{"a": 1, "b":')
    (u'{"a": 1, "b":', u'Invalid JSON')
    >>> make_input_to_json()(u'')
    (None, None)
    >>> make_input_to_json()(None)
    (None, None)
    """
    return pipe(
        cleanup_line,
        make_str_to_json(*args, **kwargs),
        )
