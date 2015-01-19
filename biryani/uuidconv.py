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


"""UUID Related Converters"""


import re
import uuid

from .baseconv import cleanup_line, function, pipe, test


__all__ = [
    'input_to_uuid',
    'input_to_uuid_str',
    'str_to_uuid',
    'str_to_uuid_str',
    ]

N_ = lambda message: message
uuid_re = re.compile(ur'[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}$')


# Level-1 Converters


str_to_uuid_str = test(uuid_re.match, error = N_(u'Invalid UUID'))
"""Verify that a clean string is a valid UUID string.

    .. note:: For a converter that doesn't require a clean string, see :func:`input_to_uuid_str`.

    >>> str_to_uuid_str(u'12345678-9abc-def0-1234-56789abcdef0')
    (u'12345678-9abc-def0-1234-56789abcdef0', None)
    >>> str_to_uuid_str(u'Hello World')
    (u'Hello World', u'Invalid UUID')
    >>> str_to_uuid_str(u'')
    (u'', u'Invalid UUID')
    >>> str_to_uuid_str(None)
    (None, None)
    """


# Level-2 Converters


input_to_uuid_str = pipe(cleanup_line, str_to_uuid_str)
"""Verify that a string contains a valid UUID string.

    >>> input_to_uuid_str(u'12345678-9abc-def0-1234-56789abcdef0')
    (u'12345678-9abc-def0-1234-56789abcdef0', None)
    >>> input_to_uuid_str(u'   12345678-9abc-def0-1234-56789abcdef0   ')
    (u'12345678-9abc-def0-1234-56789abcdef0', None)
    >>> input_to_uuid_str(u'12345678 - 9abc - def0 - 1234 - 56789abcdef0')
    (u'12345678 - 9abc - def0 - 1234 - 56789abcdef0', u'Invalid UUID')
    >>> input_to_uuid_str(u'Hello World')
    (u'Hello World', u'Invalid UUID')
    >>> input_to_uuid_str(u'')
    (None, None)
    >>> input_to_uuid_str(None)
    (None, None)
    """


str_to_uuid = pipe(str_to_uuid_str, function(uuid.UUID))
"""Convert a clean string to an UUID.

    .. note:: For a converter that doesn't require a clean string, see :func:`input_to_uuid`.

    >>> str_to_uuid(u'12345678-9abc-def0-1234-56789abcdef0')
    (UUID('12345678-9abc-def0-1234-56789abcdef0'), None)
    >>> str_to_uuid(u'Hello World')
    (u'Hello World', u'Invalid UUID')
    >>> str_to_uuid(u'')
    (u'', u'Invalid UUID')
    >>> str_to_uuid(None)
    (None, None)
    """


# Level-3 Converters


input_to_uuid = pipe(cleanup_line, str_to_uuid)
"""Convert a string to an UUID.

    >>> input_to_uuid(u'12345678-9abc-def0-1234-56789abcdef0')
    (UUID('12345678-9abc-def0-1234-56789abcdef0'), None)
    >>> input_to_uuid(u'   12345678-9abc-def0-1234-56789abcdef0   ')
    (UUID('12345678-9abc-def0-1234-56789abcdef0'), None)
    >>> input_to_uuid(u'12345678 - 9abc - def0 - 1234 - 56789abcdef0')
    (u'12345678 - 9abc - def0 - 1234 - 56789abcdef0', u'Invalid UUID')
    >>> input_to_uuid(u'Hello World')
    (u'Hello World', u'Invalid UUID')
    >>> input_to_uuid(u'')
    (None, None)
    >>> input_to_uuid(None)
    (None, None)
    """
