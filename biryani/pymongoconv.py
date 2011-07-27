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


"""Pymongo Related Converters"""


import bson

from . import baseconv as conv
from . import states


__all__ = [
    'mongodb_query_to_object',
    'object_id_to_object',
    'python_data_to_geo',
    ]


def mongodb_query_to_object(object_class):
    def mongodb_query_to_object_converter(value, state = states.default_state):
        """Convert a MongoDB query expression to an object wrapped to a MongoDB document."""
        if value is None:
            return value, None
        instance = object_class.find_one(value)
        if instance is None:
            return value, state._('No document of class {0} for query {1}').format(object_class.__name__, value)
        return instance, None
    return mongodb_query_to_object_converter


def object_id_to_object(object_class, cache = None):
    def object_id_to_object_converter(value, state = states.default_state):
        """Convert an ID to an object wrapped to a MongoDB document."""
        if value is None:
            return value, None
        assert isinstance(value, bson.objectid.ObjectId), str((value,))
        if cache is not None and value in cache:
            return cache[value], None
        instance = object_class.find_one(value)
        if instance is None:
            return value, state._('No document of class {0} with ID {1}').format(object_class.__name__, value)
        return instance, None
    return object_id_to_object_converter


python_data_to_geo = conv.pipe(
    conv.test_isinstance((list, tuple)),
    conv.structured_sequence(
        [
            conv.pipe(conv.python_data_to_float, conv.test_between(-90, 90)), # latitude
            conv.pipe(conv.python_data_to_float, conv.test_between(-180, 180)), # longitude
            conv.pipe(conv.python_data_to_int, conv.test_between(0, 9)), # accuracy
            ],
        default = 'ignore'),
    )

