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


"""French related Converters"""


from . import baseconv as conv
from . import strings, states


__all__ = [
    'clean_str_to_phone',
    'str_to_phone',
    ]

N_ = conv.N_


def clean_str_to_phone(value, state = states.default_state):
    """Convert a clean string to a phone number.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_phone`.

    .. warning:: This converter is not stable and may change or be removed at any time. If you need it, you shouldn't
       import it, but copy and paste its source code into your application.

    >>> clean_str_to_phone(u'0123456789')
    (u'+33 1 23 45 67 89', None)
    >>> clean_str_to_phone('0123456789')
    (u'+33 1 23 45 67 89', None)
    """
    if value is None:
        return value, None
    if value.startswith('+'):
        value = value.replace('+', '00', 1)
    value = strings.slugify(value, separator = '')
    if not value:
        return value, None
    if not value.isdigit():
        return value, state._(u'Unexpected non numerical characters in phone number')

    if value.startswith('0033'):
        value = value[2:]
    if value.startswith('330'):
        value = value[2:]
    elif value.startswith('33'):
        value = u'0' + value[2:]

    if value.startswith(u'00'):
        # International phone number
        country = {
            u'594': N_(u'French Guyana'),
            u'681': N_(u'Wallis and Futuna'),
            u'687': N_(u'New Caledonia'),
            u'689': N_(u'French Polynesia'),
            }.get(value[2:5])
        if country is not None:
            if len(value) == 11:
                return u'+{0} {1} {2} {3}'.format(value[2:5], value[5:7], value[7:9], value[9:11]), None
            return value, state._(u'Wrong number of digits for phone number of {0}').format(_(country))
        return value, state._(u'Unknown international phone number')
    if len(value) == 4:
        return value, None
    if len(value) == 9 and value[0] != '0':
        value = u'0{0}'.format(value)
    if len(value) == 10:
        if value[0] != '0':
            return value, state._(u'Unexpected first digit in phone number: {0} instead of 0').format(value[0])
        mask = u'+33 {0}{1} {2} {3} {4}' if value[1] == '8' else u'+33 {0} {1} {2} {3} {4}'
        return mask.format(value[1], value[2:4], value[4:6], value[6:8], value[8:10]), None
    return value, state._(u'Wrong number of digits in phone number')


str_to_phone = conv.pipe(conv.cleanup_line, clean_str_to_phone)
"""Convert a string to a phone number.

    .. warning:: This converter is not stable and may change or be removed at any time. If you need it, you shouldn't
       import it, but copy and paste its source code into your application.

    >>> str_to_phone(u'   0123456789   ')
    (u'+33 1 23 45 67 89', None)
    >>> str_to_phone('   0123456789   ')
    (u'+33 1 23 45 67 89', None)
    """
