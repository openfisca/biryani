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


"""Babel related Converters

See http://babel.edgewall.org/
"""


import babel

from .baseconv import cleanup_line, pipe
from . import states


__all__ = [
    'input_to_lang',
    'str_to_lang',
    ]


def str_to_lang(value, state = None):
    """Convert a clean string to a language code.

    .. note:: For a converter that doesn't require a clean string, see :func:`input_to_lang`.

    >>> str_to_lang(u'fr')
    (u'fr', None)
    >>> str_to_lang(u'fr_FR')
    (u'fr_FR', None)
    >>> str_to_lang(u'fr-FR')
    (u'fr-FR', u'Invalid value')
    >>> str_to_lang(u'francais')
    (u'francais', u'Invalid value')
    >>> str_to_lang(None)
    (None, None)
    """
    if value is None:
        return value, None
    if state is None:
        state = states.default_state
    if not babel.localedata.exists(value):
        return value, state._(u'Invalid value')
    return value, None


input_to_lang = pipe(cleanup_line, str_to_lang)
"""Convert a string to a language code.

    >>> input_to_lang(u'fr')
    (u'fr', None)
    >>> input_to_lang(u'fr_FR')
    (u'fr_FR', None)
    >>> input_to_lang(u'   fr_FR   ')
    (u'fr_FR', None)
    >>> input_to_lang(u'fr-FR')
    (u'fr-FR', u'Invalid value')
    >>> input_to_lang(u'francais')
    (u'francais', u'Invalid value')
    >>> input_to_lang(u'   ')
    (None, None)
    >>> input_to_lang(None)
    (None, None)
    """
