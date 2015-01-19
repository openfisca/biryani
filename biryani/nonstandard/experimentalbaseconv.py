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


"""Experimental Converters

.. warning:: Since these converters may change at any time, don't import this module, but copy and paste the functions
   you need in your application.
"""


from .. import states

__all__ = [
    'mapping_replace_sequence',
    ]

N_ = lambda message: message


def mapping_replace_sequence(keys, converter, sequence_constructor = list):
    """Return a converter that extracts a sequence from a mapping, converts it and reinjects it into the mapping.
    """
    def mapping_replace_sequence_converter(value, state = None):
        if value is None:
            return value, None
        if state is None:
            state = states.default_state
        sequence = sequence_constructor(
            value.get(key)
            for key in keys
            )
        converted_sequence, sequence_error = converter(sequence, state = state)
        if sequence_error is not None:
            if isinstance(sequence_error, dict):
                return value, dict(
                    (key, sequence_error[index])
                    for index, key in enumerate(keys)
                    if index in sequence_error
                    )
            return value, sequence_error
        converted_value = value.copy()
        if converted_sequence is None:
            for key in keys:
                if key in converted_value:
                    del converted_value[key]
        else:
            assert len(keys) == len(converted_sequence), "Sequence and keys have a different length: {0}, {1}".format(
                converted_sequence, keys)
            for key, item_value in zip(keys, converted_sequence):
                if item_value is None:
                    if key in converted_value:
                        del converted_value[key]
                else:
                    converted_value[key] = item_value
        return converted_value or None, None
    return mapping_replace_sequence_converter
