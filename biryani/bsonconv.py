# -*- coding: utf-8 -*-


# Biryani -- A conversion and validation toolbox
# By: Emmanuel Raviart <eraviart@easter-eggs.com>
#
# Copyright (C) 2009, 2010, 2011 Easter-eggs
# http://packages.python.org/biryani/
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
    'clean_unicode_to_object_id',
    'object_id_re',
    'object_id_to_unicode',
    'python_data_to_object_id',
    'unicode_to_object_id',
    ]


object_id_re = re.compile(r'[\da-f]{24}$')


# Level-1 Converters


def clean_unicode_to_object_id(value, state = states.default_state):
    """Convert a clean unicode string to MongoDB ObjectId."""
    if value is None:
        return None, None
    else:
        id = value.lower()
        if object_id_re.match(id) is None:
            return None, state._('Invalid value')
        return bson.objectid.ObjectId(id), None


def object_id_to_unicode(value, state = states.default_state):
    """Convert a MongoDB ObjectId to unicode."""
    if value is None:
        return None, None
    else:
        return unicode(value), None


unicode_to_object_id = conv.pipe(conv.cleanup_line, clean_unicode_to_object_id)


# Level-2 Converters


python_data_to_object_id = conv.first_valid(
    conv.test_isinstance(bson.objectid.ObjectId),
    conv.pipe(
        conv.test_isinstance(basestring),
        unicode_to_object_id,
        ),
    )

