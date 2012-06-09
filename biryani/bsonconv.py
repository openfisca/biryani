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


"""MongoDB BSON related Converters

See http://api.mongodb.org/python/current/api/bson/index.html
"""


import re

import bson

from .baseconv import cleanup_line, first_match, pipe, test_isinstance
from . import states


__all__ = [
    'anything_to_object_id',
    'clean_str_to_object_id',
    'object_id_re',
    'object_id_to_str',
    'str_to_object_id',
    ]


object_id_re = re.compile(r'[\da-f]{24}$')


# Level-1 Converters


def clean_str_to_object_id(value, state = None):
    """Convert a clean string to a BSON ObjectId.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_object_id`.

    .. note:: For a converter that doesn't fail when input data is already an ObjectId,
        use :func:`anything_to_object_id`.

    >>> clean_str_to_object_id(u'4e333f53ff42e928000007d8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> clean_str_to_object_id('4e333f53ff42e928000007d8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> clean_str_to_object_id(u'4E333F53FF42E928000007D8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> from bson.objectid import ObjectId
    >>> clean_str_to_object_id(ObjectId('4e333f53ff42e928000007d8'))
    Traceback (most recent call last):
    AttributeError:
    >>> clean_str_to_object_id(u"ObjectId('4e333f53ff42e928000007d8')")
    (u"ObjectId('4e333f53ff42e928000007d8')", u'Invalid value')
    >>> clean_str_to_object_id(None)
    (None, None)
    """
    if value is None:
        return value, None
    id = value.lower()
    if object_id_re.match(id) is None:
        return value, (state or states.default_state)._(u'Invalid value')
    return bson.objectid.ObjectId(id), None


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


str_to_object_id = pipe(cleanup_line, clean_str_to_object_id)
"""Convert a string to a BSON ObjectId.

    .. note:: For a converter that doesn't fail when input data is already an ObjectId,
        use :func:`anything_to_object_id`.

    >>> str_to_object_id(u'4e333f53ff42e928000007d8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> str_to_object_id('4e333f53ff42e928000007d8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> str_to_object_id(u'4E333F53FF42E928000007D8')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> str_to_object_id(u'   4e333f53ff42e928000007d8   ')
    (ObjectId('4e333f53ff42e928000007d8'), None)
    >>> from bson.objectid import ObjectId
    >>> str_to_object_id(ObjectId('4e333f53ff42e928000007d8'))
    Traceback (most recent call last):
    AttributeError:
    >>> str_to_object_id(u"ObjectId('4e333f53ff42e928000007d8')")
    (u"ObjectId('4e333f53ff42e928000007d8')", u'Invalid value')
    >>> str_to_object_id(u'  ')
    (None, None)
    >>> str_to_object_id(None)
    (None, None)
    """


# Level-2 Converters


anything_to_object_id = first_match(
    test_isinstance(bson.objectid.ObjectId),
    pipe(
        test_isinstance(basestring),
        str_to_object_id,
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
