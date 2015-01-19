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


"""Deprecated Converters

.. warning:: Since these converters may change or be removed at any time, don't import this module, but copy and paste
   the functions you need in your application.
"""


from .. import baseconv, custom_conv, objectconv


conv = custom_conv(baseconv, objectconv)
N_ = lambda message: message


def attribute(name):
    """Return a converter that retrieves an existing attribute from an object.

    This converter is non-standard, because:

    * It is a simple one-liner.
    * It needs an option to specify what to do when attribute doesn't exist.

    >>> class C(object):
    ...     pass
    >>> conv.pipe(conv.make_dict_to_object(C), attribute('a'))(dict(a = 1, b = 2))
    (1, None)
    """
    return conv.function(lambda value: getattr(value, name))


def mapping_value(key, default = None):
    """Return a converter that retrieves an item value from a mapping.

    This converter is non-standard, because:

    * It is a simple one-liner.
    * It needs an option to specify what to do when attribute doesn't exist.

    >>> mapping_value('a')(dict(a = 1, b = 2))
    (1, None)
    >>> mapping_value('c')(dict(a = 1, b = 2))
    (None, None)
    >>> mapping_value('c', u'Hello world!')(dict(a = 1, b = 2))
    (u'Hello world!', None)
    """
    return conv.function(lambda value: value.get(key, default))


def sort(cmp = None, key = None, reverse = False):
    """Return a converter that sorts an iterable.

    This converter is non-standard, because:

    * It is a simple one-liner. Most of the times, ``conv.function(sorted)`` is sufficient.

    >>> sort()([3, 2, 1])
    ([1, 2, 3], None)
    >>> sort()(None)
    (None, None)
    """
    return conv.function(lambda values: sorted(values, cmp = cmp, key = key, reverse = reverse))


def split(separator = None):
    """Returns a converter that splits a string.

    This converter is non-standard, because:

    * It is a simple one-liner.

    >>> split()(u'a bc  def')
    ([u'a', u'bc', u'def'], None)
    >>> split(u',')(u'a,bc,,def')
    ([u'a', u'bc', u'', u'def'], None)
    >>> split()(None)
    (None, None)
    """
    return conv.function(lambda value: value.split(separator))


def strip(chars = None):
    """Returns a converter that removes leading and trailing characters from string.

    This converter is non-standard, because:

    * It is a simple one-liner.
    * Most of the times, converters :func:`biryani.baseconv.cleanup_line` or :func:`biryani.baseconv.cleanup_text` are
      used instead.

    >>> strip()(u'   Hello world!   ')
    (u'Hello world!', None)
    >>> strip(u'+-!')(u'+-+Hello world!-+-')
    (u'Hello world', None)
    >>> strip()(None)
    (None, None)
    """
    return conv.function(lambda value: value.strip(chars))


def test_match(regex, error = N_('Invalid value format')):
    """Return a converter that accepts only values that match given (compiled) regular expression.

    This converter is non-standard, because:

    * It is a simple one-liner.
    * The error message must always be given, so that error is explicit.
    * Often, knowing that there is a match is not sufficient and data must be extracted from match object.

    >>> import re
    >>> test_match(re.compile(u'OK$'))(u'OK')
    (u'OK', None)
    >>> test_match(re.compile(u'ok$'))(u'not OK')
    (u'not OK', 'Invalid value format')
    """
    return conv.test(lambda value: regex.match(value), error = error)
