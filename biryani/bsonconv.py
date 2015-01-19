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


"""MongoDB BSON related Converters

See http://api.mongodb.org/python/current/api/bson/index.html
"""


import re

import bson

from .baseconv import cleanup_line, first_match, function, pipe, test_isinstance
from . import states


__all__ = [
    'anything_to_object_id',
    'bson_to_json',
    'input_to_object_id',
    'input_to_object_id_str',
    'json_to_bson',
    'object_id_re',
    'object_id_to_str',
    'str_to_object_id',
    'str_to_object_id_str',
    ]


object_id_re = re.compile(r'[\da-f]{24}$')


# Utility functions


def convert_bson_to_json(value):
    """Recursively convert a BSON value to JSON.

    A MongoDB document can't have an item with a key containing a ".". So they are escaped with "%".
    """
    if value is None:
        return value
    if isinstance(value, dict):
        # Note: Use type(value) instead of dict, to support OrderedDict.
        return type(value)(
            (
                item_key.replace('%2e', '.').replace('%25', '%'),
                convert_bson_to_json(item_value),
                )
            for item_key, item_value in value.iteritems()
            )
    if isinstance(value, list):
        return [
            convert_bson_to_json(item)
            for item in value
            ]
    return value


def convert_json_to_bson(value):
    """Recursively convert a JSON value to BSON.

    A MongoDB document can't have an item with a key containing a ".". So they are escaped with "%".
    """
    if value is None:
        return value
    if isinstance(value, dict):
        # Note: Use type(value) instead of dict, to support OrderedDict.
        return type(value)(
            (
                item_key.replace('%', '%25').replace('.', '%2e'),
                convert_json_to_bson(item_value),
                )
            for item_key, item_value in value.iteritems()
            )
    if isinstance(value, list):
        return [
            convert_json_to_bson(item)
            for item in value
            ]
    return value


# Level-1 Converters


bson_to_json = function(convert_bson_to_json)
"""Convert a BSON value to JSON.

    A MongoDB document can't have an item with a key containing a ".". So they are escaped with "%".

    >>> bson_to_json({'a': 1, 'b': [2, 3], 'c%2ed': {'e': 4}})
    ({'a': 1, 'c.d': {'e': 4}, 'b': [2, 3]}, None)
    >>> bson_to_json({})
    ({}, None)
    >>> bson_to_json(None)
    (None, None)
    """


json_to_bson = function(convert_json_to_bson)
"""Convert a JSON value to BSON.

    A MongoDB document can't have an item with a key containing a ".". So they are escaped with "%".

    >>> json_to_bson({'a': 1, 'b': [2, 3], 'c.d': {'e': 4}})
    ({'a': 1, 'b': [2, 3], 'c%2ed': {'e': 4}}, None)
    >>> json_to_bson({})
    ({}, None)
    >>> json_to_bson(None)
    (None, None)
    """


def object_id_to_str(value, state = None):
    """Convert a BSON ObjectId to unicode.

    .. note:: To ensure that input value is an ObjectId, first use :func:`biryani.baseconv.test_isinstance`.

    >>> from bson.objectid import ObjectId
    >>> object_id_to_str(ObjectId('4e333f53ff42e928000007d8'))
    (u'4e333f53ff42e928000007d8', None)
    >>> object_id_to_str(u'4e333f53ff42e928000007d8')
    (u'4e333f53ff42e928000007d8', None)
    >>> from biryani import baseconv as conv
    >>> conv.pipe(conv.test_isinstance(ObjectId), object_id_to_str)(ObjectId('4e333f53ff42e928000007d8'))
    (u'4e333f53ff42e928000007d8', None)
    >>> conv.pipe(conv.test_isinstance(ObjectId), object_id_to_str)(u'4e333f53ff42e928000007d8')
    (u'4e333f53ff42e928000007d8', u"Value is not an instance of <class 'bson.objectid.ObjectId'>")
    >>> object_id_to_str(None)
    (None, None)
    """
    if value is None:
        return value, None
    return unicode(value), None


def str_to_object_id_str(value, state = None):
    """Convert a clean string to a BSON ObjectId string.

    .. note:: For a converter that doesn't require a clean string, see :func:`input_to_object_id_str`.

    >>> str_to_object_id_str(u'4e333f53ff42e928000007d8')
    (u'4e333f53ff42e928000007d8', None)
    >>> str_to_object_id_str('4e333f53ff42e928000007d8')
    ('4e333f53ff42e928000007d8', None)
    >>> str_to_object_id_str(u'4E333F53FF42E928000007D8')
    (u'4e333f53ff42e928000007d8', None)
    >>> from bson.objectid import ObjectId
    >>> str_to_object_id_str(ObjectId('4e333f53ff42e928000007d8'))
    Traceback (most recent call last):
    AttributeError:
    >>> str_to_object_id_str(u"ObjectId('4e333f53ff42e928000007d8')")
    (u"ObjectId('4e333f53ff42e928000007d8')", u'Invalid value')
    >>> str_to_object_id_str(None)
    (None, None)
    """
    if value is None:
        return value, None
    if state is None:
        state = states.default_state
    id = value.lower()
    if object_id_re.match(id) is None:
        return value, state._(u'Invalid value')
    return id, None


# Level-2 Converters


input_to_object_id_str = pipe(cleanup_line, str_to_object_id_str)
"""Convert a string to a BSON ObjectId string.

    >>> input_to_object_id_str(u'4e333f53ff42e928000007d8')
    (u'4e333f53ff42e928000007d8', None)
    >>> input_to_object_id_str('4e333f53ff42e928000007d8')
    ('4e333f53ff42e928000007d8', None)
    >>> input_to_object_id_str(u'4E333F53FF42E928000007D8')
    (u'4e333f53ff42e928000007d8', None)
    >>> input_to_object_id_str(u'   4e333f53ff42e928000007d8   ')
    (u'4e333f53ff42e928000007d8', None)
    >>> from bson.objectid import ObjectId
    >>> input_to_object_id_str(ObjectId('4e333f53ff42e928000007d8'))
    Traceback (most recent call last):
    AttributeError:
    >>> input_to_object_id_str(u"ObjectId('4e333f53ff42e928000007d8')")
    (u"ObjectId('4e333f53ff42e928000007d8')", u'Invalid value')
    >>> input_to_object_id_str(u'  ')
    (None, None)
    >>> input_to_object_id_str(None)
    (None, None)
    """


str_to_object_id = pipe(str_to_object_id_str, function(bson.objectid.ObjectId))
"""Convert a clean string to a BSON ObjectId.

    .. note:: For a converter that doesn't require a clean string, see :func:`input_to_object_id`.

    .. note:: For a converter that doesn't fail when input data is already an ObjectId,
        use :func:`anything_to_object_id`.

    >>> str_to_object_id(u'4e333f53ff42e928000007d8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> str_to_object_id('4e333f53ff42e928000007d8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> str_to_object_id(u'4E333F53FF42E928000007D8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> from bson.objectid import ObjectId
    >>> str_to_object_id(ObjectId('4e333f53ff42e928000007d8'))
    Traceback (most recent call last):
    AttributeError:
    >>> str_to_object_id(u"ObjectId('4e333f53ff42e928000007d8')")
    (u"ObjectId('4e333f53ff42e928000007d8')", u'Invalid value')
    >>> str_to_object_id(None)
    (None, None)
    """


# Level-3 Converters


input_to_object_id = pipe(cleanup_line, str_to_object_id)
"""Convert a string to a BSON ObjectId.

    .. note:: For a converter that doesn't fail when input data is already an ObjectId,
        use :func:`anything_to_object_id`.

    >>> input_to_object_id(u'4e333f53ff42e928000007d8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> input_to_object_id('4e333f53ff42e928000007d8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> input_to_object_id(u'4E333F53FF42E928000007D8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> input_to_object_id(u'   4e333f53ff42e928000007d8   ')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> from bson.objectid import ObjectId
    >>> input_to_object_id(ObjectId('4e333f53ff42e928000007d8'))
    Traceback (most recent call last):
    AttributeError:
    >>> input_to_object_id(u"ObjectId('4e333f53ff42e928000007d8')")
    (u"ObjectId('4e333f53ff42e928000007d8')", u'Invalid value')
    >>> input_to_object_id(u'  ')
    (None, None)
    >>> input_to_object_id(None)
    (None, None)
    """


# Level-4 Converters


anything_to_object_id = first_match(
    test_isinstance(bson.objectid.ObjectId),
    pipe(
        test_isinstance(basestring),
        input_to_object_id,
        ),
    )
"""Convert any compatible Python data to a BSON ObjectId.

    >>> anything_to_object_id(u'4e333f53ff42e928000007d8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> anything_to_object_id('4e333f53ff42e928000007d8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> anything_to_object_id(u'4E333F53FF42E928000007D8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> anything_to_object_id(u'   4e333f53ff42e928000007d8   ')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> from bson.objectid import ObjectId
    >>> anything_to_object_id(ObjectId('4e333f53ff42e928000007d8'))
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> anything_to_object_id(u"ObjectId('4e333f53ff42e928000007d8')")
    (u"ObjectId('4e333f53ff42e928000007d8')", u'Invalid value')
    >>> anything_to_object_id(u'  ')
    (None, None)
    >>> anything_to_object_id(None)
    (None, None)
    """
