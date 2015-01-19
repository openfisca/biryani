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


"""Object Related Converters"""


from .baseconv import function


__all__ = [
    'make_dict_to_object',
    'object_to_clean_dict',
    'object_to_dict',
    ]


class EmptyClass(object):
    pass


def make_dict_to_object(cls):
    """Return a converter that creates in instance of a class from a dictionary.

    >>> class C(object):
    ...     pass
    >>> make_dict_to_object(C)(dict(a = 1, b = 2))
    (<C object at 0x...>, None)
    >>> c = check(make_dict_to_object(C))(dict(a = 1, b = 2))
    >>> c.a, c.b
    (1, 2)
    >>> make_dict_to_object(C)(None)
    (None, None)
    """
    def dict_to_object(value, state = None):
        if value is None:
            return value, None
        # Dont do the following instructions, to ensure that cls __init__ method is not called.
        # instance = cls()
        # instance.__dict__.update(value)
        instance = EmptyClass()
        instance.__class__ = cls
        instance.__dict__ = value
        return instance, None
    return dict_to_object


object_to_clean_dict = function(lambda instance: dict(
    (name, value)
    for name, value in instance.__dict__.iteritems()
    if getattr(instance.__class__, name, UnboundLocalError) is not value
    ))
"""Convert an object's instance to a dictionary, by extracting the attributes whose value differs from the ones defined
    in the object's class.

    .. note:: Use this converter instead of :func:`object_to_dict` when you want to remove defaut values from generated
       dictionary.

    >>> class C(object):
    ...     a = 1
    ...     z = None
    >>> c = C()
    >>> object_to_clean_dict(c)
    ({}, None)
    >>> c.a = 2
    >>> object_to_clean_dict(c)
    ({'a': 2}, None)
    >>> d = C()
    >>> d.a = 2
    >>> d.b = 3
    >>> object_to_clean_dict(d)
    ({'a': 2, 'b': 3}, None)
    >>> e = C()
    >>> e.a = 1
    >>> object_to_clean_dict(e)
    ({}, None)
    >>> f = C()
    >>> f.a = 1
    >>> f.b = 2
    >>> f.y = None
    >>> f.z = None
    >>> object_to_clean_dict(f)
    ({'y': None, 'b': 2}, None)
    >>> object_to_clean_dict(None)
    (None, None)
    >>> object_to_clean_dict(42)
    Traceback (most recent call last):
    AttributeError:
    """

object_to_dict = function(lambda instance: getattr(instance, '__dict__'))
"""Convert an object's instance to a dictionary, by returning its ``__dict__`` atribute.

    .. note:: Use converter :func:`object_to_clean_dict` when you want to remove defaut values from generated
       dictionary.

    >>> class C(object):
    ...     a = 1
    >>> c = C()
    >>> object_to_dict(c)
    ({}, None)
    >>> c.a = 2
    >>> object_to_dict(c)
    ({'a': 2}, None)
    >>> d = C()
    >>> d.a = 2
    >>> d.b = 3
    >>> object_to_dict(d)
    ({'a': 2, 'b': 3}, None)
    >>> e = C()
    >>> e.a = 1
    >>> object_to_dict(e)
    ({'a': 1}, None)
    >>> f = C()
    >>> f.a = 1
    >>> f.b = 2
    >>> object_to_dict(f)
    ({'a': 1, 'b': 2}, None)
    >>> object_to_dict(None)
    (None, None)
    >>> object_to_dict(42)
    Traceback (most recent call last):
    AttributeError:
    """
