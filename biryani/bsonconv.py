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


"""BSON related Converters"""


import re

import bson

from . import baseconv as conv
from . import states


__all__ = [
    'clean_str_to_object_id',
    'object_id_re',
    'object_id_to_str',
    'python_data_to_object_id',
    'str_to_object_id',
    ]


object_id_re = re.compile(r'[\da-f]{24}$')


# Level-1 Converters


def clean_str_to_object_id(value, state = states.default_state):
    """Convert a clean string to MongoDB ObjectId."""
    if value is None:
        return value, None
    id = value.lower()
    if object_id_re.match(id) is None:
        return value, state._(u'Invalid value')
    return bson.objectid.ObjectId(id), None


def object_id_to_str(value, state = states.default_state):
    """Convert a MongoDB ObjectId to unicode."""
    if value is None:
        return value, None
    return unicode(value), None


str_to_object_id = conv.pipe(conv.cleanup_line, clean_str_to_object_id)


# Level-2 Converters


python_data_to_object_id = conv.first_match(
    conv.test_isinstance(bson.objectid.ObjectId),
    conv.pipe(
        conv.test_isinstance(basestring),
        str_to_object_id,
        ),
    )

