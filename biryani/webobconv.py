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


"""WebOb related Converters

See http://webob.org/
"""


from .baseconv import function


__all__ = [
    'multidict_get',
    'multidict_getall',
    'multidict_getone',
    ]


def multidict_get(key, default = None):
    """Return a converter that retrieves the value of a MultiDict item.

    .. note:: When several values exists for the same key, only the last one is returned.

    >>> import webob
    >>> req = webob.Request.blank('/?a=1&tag=hello&tag=World!&z=')
    >>> multidict_get('a')(req.GET)
    (u'1', None)
    >>> multidict_get('a', default = 2)(req.GET)
    (u'1', None)
    >>> multidict_get('b')(req.GET)
    (None, None)
    >>> multidict_get('b', default = 2)(req.GET)
    (2, None)
    >>> multidict_get('z')(req.GET)
    (u'', None)
    >>> multidict_get('z', default = 3)(req.GET)
    (u'', None)
    >>> pipe(multidict_get('z'), cleanup_line, default(3))(req.GET)
    (3, None)
    >>> multidict_get('tag')(req.GET)
    (u'World!', None)
    >>> new_struct(dict(
    ...     a = multidict_get('a'),
    ...     b = multidict_get('b'),
    ...     ))(req.GET)
    ({'a': u'1', 'b': None}, None)
    """
    return function(lambda multidict: multidict.get(key, default = default))


def multidict_getall(key):
    """Return a converter that retrieves all values of a MultiDict item.

    >>> import webob
    >>> req = webob.Request.blank('/?a=1&tag=hello&tag=World!&z=')
    >>> multidict_getall('a')(req.GET)
    ([u'1'], None)
    >>> multidict_getall('b')(req.GET)
    (None, None)
    >>> multidict_getall('z')(req.GET)
    ([u''], None)
    >>> multidict_getall('tag')(req.GET)
    ([u'hello', u'World!'], None)
    >>> new_struct(dict(
    ...     b = multidict_getall('b'),
    ...     tags = multidict_getall('tag'),
    ...     ))(req.GET)
    ({'b': None, 'tags': [u'hello', u'World!']}, None)
    """
    return function(lambda multidict: multidict.getall(key) or None)


def multidict_getone(key):
    """Return a converter that retrieves one and only one value of a MultiDict item.

    .. note:: When no value exists or several values exists for the same key, an exception is raised. Most of the times,
       this is not the desired behaviour, so use :func:`multidict_get` instead.

    >>> import webob
    >>> req = webob.Request.blank('/?a=1&tag=hello&tag=World!&z=')
    >>> multidict_getone('a')(req.GET)
    (u'1', None)
    >>> multidict_getone('b')(req.GET)
    Traceback (most recent call last):
    KeyError:
    >>> multidict_getone('')(req.GET)
    Traceback (most recent call last):
    KeyError:
    >>> multidict_getone('tag')(req.GET)
    Traceback (most recent call last):
    KeyError:
    """
    return function(lambda multidict: multidict.getone(key))
