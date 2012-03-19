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


import re

from .baseconv import cleanup_line, function, make_str_to_slug, N_, noop, pipe, struct, test
from . import strings, states


__all__ = [
    'clean_str_to_phone',
    'expand_postal_routing',
    'repair_postal_routing',
    'shrink_postal_routing',
    'split_postal_distribution',
    'str_to_depcom',
    'str_to_lenient_depcom',
    'str_to_lenient_postal_code',
    'str_to_phone',
    'str_to_postal_code',
    'str_to_postal_distribution',
    'str_to_postal_routing',
    ]

depcom_re = re.compile(ur'\d[\dAB]\d{3}$')


# Level-1 Converters


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
            return value, state._(u'Wrong number of digits for phone number of {0}').format(state._(country))
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


def expand_postal_routing(value, state = states.default_state):
    """Replace abbreviations with their full name in a postal routing

    .. note:: Postal routing must already be converted to uppercase ASCII.

    >>> expand_postal_routing(u'ST NAZAIRE')
    (u'SAINT NAZAIRE', None)
    >>> expand_postal_routing(u'SAINT ETIENNE')
    (u'SAINT ETIENNE', None)
    >>> expand_postal_routing(u'STILL')
    (u'STILL', None)
    >>> expand_postal_routing(u'STES')
    (u'SAINTES', None)
    >>> expand_postal_routing(None)
    (None, None)
    """
    if value is None:
        return value, None
    postal_routing_fragments = []
    for word in value.split():
        if word == 'ST':
            word = 'SAINT'
        elif word == 'STE':
            word = 'SAINTE'
        elif word == 'STES':
            # STES is not a valid abbreviation for SAINTES, bu we accept it.
            word = 'SAINTES'
        postal_routing_fragments.append(word)
    return u' '.join(postal_routing_fragments) or None, None


def repair_postal_routing(value, state = states.default_state):
    """Correct mispelled words in a postal routing.

    .. note:: Postal routing must already be converted to uppercase ASCII.

    .. note:: This converter doesn't handle abbreviations. See :func:`shrink_postal_routing`
        or :func:`expand_postal_routing` to handle them.

    >>> repair_postal_routing(u'SAINT NAZAIRE CED')
    (u'SAINT NAZAIRE CEDEX', None)
    >>> repair_postal_routing(u'ST NAZAIRE CED')
    (u'ST NAZAIRE CEDEX', None)
    >>> repair_postal_routing(None)
    (None, None)
    """
    if value is None:
        return value, None
    postal_routing_fragments = []
    for word in value.split():
        if word == 'CED':
            word = 'CEDEX'
        postal_routing_fragments.append(word)
    return u' '.join(postal_routing_fragments) or None, None


def shrink_postal_routing(value, state = states.default_state):
    """Replace words in a postal routing with their abbreviation.

    .. note:: Postal routing must already be converted to uppercase ASCII.

    >>> shrink_postal_routing(u'SAINT NAZAIRE')
    (u'ST NAZAIRE', None)
    >>> shrink_postal_routing(u'ST ETIENNE')
    (u'ST ETIENNE', None)
    >>> shrink_postal_routing(u'SAINTES')
    (u'SAINTES', None)
    >>> shrink_postal_routing(None)
    (None, None)
    """
    if value is None:
        return value, None
    postal_routing_fragments = []
    for word in value.split():
        if word == 'SAINT':
            word = 'ST'
        elif word == 'SAINTE':
            word = 'STE'
        postal_routing_fragments.append(word)
    return u' '.join(postal_routing_fragments) or None, None


def split_postal_distribution(value, state = states.default_state):
    """Extract french postal code and postal routing (aka locality) from a string

    .. note:: Input value must already be converted to uppercase ASCII.

    >>> split_postal_distribution(u'75014 PARIS')
    ((u'75014', u'PARIS'), None)
    >>> split_postal_distribution(u'75014 PARIS 14')
    ((u'75014', u'PARIS 14'), None)
    >>> split_postal_distribution(u'42000 ST ETIENNE')
    ((u'42000', u'ST ETIENNE'), None)
    >>> split_postal_distribution(u'   44690 SAINT FIACRE SUR MAINE')
    ((u'44690', u'SAINT FIACRE SUR MAINE'), None)
    >>> split_postal_distribution(u'88151 THAON LES VOSGES CED')
    ((u'88151', u'THAON LES VOSGES CED'), None)
    >>> split_postal_distribution(u'17100 SAINTES')
    ((u'17100', u'SAINTES'), None)
    >>> split_postal_distribution('   ')
    (None, None)
    >>> split_postal_distribution(None)
    (None, None)
    """
    if value is None:
        return value, None
    postal_code = None
    postal_routing_fragments = []
    for word in value.split():
        if postal_code is None:
            if word.isdigit():
                if not postal_routing_fragments \
                        or postal_routing_fragments[0] not in ('LYON', 'MARSEILLE', 'PARIS') \
                        or not (1 <= int(word) <= 20):
                    postal_code = unicode(word)
                    continue
        postal_routing_fragments.append(word)
    postal_routing = u' '.join(postal_routing_fragments) or None
    if postal_code is None and postal_routing is None:
        return None, None
    return (postal_code, postal_routing), None


str_to_lenient_depcom = pipe(
    make_str_to_slug(separator = u'', transform = strings.upper),
    function(lambda depcom: u'0{0}'.format(depcom) if len(depcom) == 4 else depcom),
    )
"""Convert a string to an INSEE commune code (aka depcom). Don't fail when depcom is not valid.

    .. note:: To validate depcom, use :func:`str_to_depcom` instead.

    >>> str_to_lenient_depcom(u'   75156   ')
    (u'75156', None)
    >>> str_to_lenient_depcom(u'   2A100   ')
    (u'2A100', None)
    >>> str_to_lenient_depcom(u'   2b100   ')
    (u'2B100', None)
    >>> str_to_lenient_depcom(u'   1234   ')
    (u'01234', None)
    >>> str_to_lenient_depcom(u'   123   ')
    (u'123', None)
    >>> str_to_lenient_depcom(u'   123  456   ')
    (u'123456', None)
    >>> str_to_lenient_depcom('   ')
    (None, None)
    >>> str_to_lenient_depcom(None)
    (None, None)
    """


str_to_depcom = pipe(
    str_to_lenient_depcom,
    test(lambda depcom: depcom_re.match(depcom) is not None,
        error = N_(u'INSEE code must contain only 5 digits or "A" or "B"')),
    )
"""Convert a string to aan INSEE commune code (aka depcom). Generate an error when depcom is not valid.

    .. note:: To allow an invalid depcom without error, use :func:`str_to_lenient_depcom` instead.

    >>> str_to_depcom(u'   75156   ')
    (u'75156', None)
    >>> str_to_depcom(u'   2A100   ')
    (u'2A100', None)
    >>> str_to_depcom(u'   2b100   ')
    (u'2B100', None)
    >>> str_to_depcom(u'   1234   ')
    (u'01234', None)
    >>> str_to_depcom(u'   123   ')
    (u'123', u'INSEE code must contain only 5 digits or "A" or "B"')
    >>> str_to_depcom(u'   123  456   ')
    (u'123456', u'INSEE code must contain only 5 digits or "A" or "B"')
    >>> str_to_depcom('   ')
    (None, None)
    >>> str_to_depcom(None)
    (None, None)
    """


str_to_lenient_postal_code = pipe(
    make_str_to_slug(separator = u''),
    function(lambda postal_code: u'0{0}'.format(postal_code) if len(postal_code) == 4 else postal_code),
    )
"""Convert a string to a postal code. Don't fail when postal code is not valid.

    .. note:: To validate postal code, use :func:`str_to_postal_code` instead.

    >>> str_to_lenient_postal_code(u'   75014   ')
    (u'75014', None)
    >>> str_to_lenient_postal_code(u'   1234   ')
    (u'01234', None)
    >>> str_to_lenient_postal_code(u'   123   ')
    (u'123', None)
    >>> str_to_lenient_postal_code(u'   123  456   ')
    (u'123456', None)
    >>> str_to_lenient_postal_code('   ')
    (None, None)
    >>> str_to_lenient_postal_code(None)
    (None, None)
    """


str_to_phone = pipe(cleanup_line, clean_str_to_phone)
"""Convert a string to a phone number.

    .. warning:: This converter is not stable and may change or be removed at any time. If you need it, you shouldn't
       import it, but copy and paste its source code into your application.

    >>> str_to_phone(u'   0123456789   ')
    (u'+33 1 23 45 67 89', None)
    >>> str_to_phone('   0123456789   ')
    (u'+33 1 23 45 67 89', None)
    """


str_to_postal_code = pipe(
    str_to_lenient_postal_code,
    test(lambda postal_code: postal_code.isdigit(), error = N_(u'Postal code must contain only digits')),
    test(lambda postal_code: len(postal_code) == 5, error = N_(u'Postal code must have 5 digits')),
    )
"""Convert a string to a postal code. Generate an error when postal code is not valid.

    .. note:: To allow invalid postal codes without error, use :func:`str_to_lenient_postal_code` instead.

    >>> str_to_postal_code(u'   75014   ')
    (u'75014', None)
    >>> str_to_postal_code(u'   1234   ')
    (u'01234', None)
    >>> str_to_postal_code(u'   123   ')
    (u'123', u'Postal code must have 5 digits')
    >>> str_to_postal_code(u'   123  456   ')
    (u'123456', u'Postal code must have 5 digits')
    >>> str_to_postal_code('   ')
    (None, None)
    >>> str_to_postal_code(None)
    (None, None)
    """


str_to_postal_routing = pipe(
    # Only upper-case ASCII letters, digits and spaces are allowed : http://fr.wikipedia.org/wiki/Adresse_postale#France
    make_str_to_slug(separator = u' ', transform = strings.upper),
    shrink_postal_routing,
    repair_postal_routing,
    )
"""Convert a string to a postal routing (aka locality, ie the part of the address after the postal code).

    >>> str_to_postal_routing(u'   Paris  14   ')
    (u'PARIS 14', None)
    >>> str_to_postal_routing(u'   Paris  xiv   ')
    (u'PARIS XIV', None)
    >>> str_to_postal_routing(u'   SAINT Etienne   ')
    (u'ST ETIENNE', None)
    >>> str_to_postal_routing(u'   SAINT Étienne   ')
    (u'ST ETIENNE', None)
    >>> str_to_postal_routing(u'   Saint-Fiacre-sur-Maine   ')
    (u'ST FIACRE SUR MAINE', None)
    >>> str_to_postal_routing(u'Thaon-les-vosges ced')
    (u'THAON LES VOSGES CEDEX', None)
    >>> str_to_postal_routing(u'Saintes')
    (u'SAINTES', None)
    >>> str_to_postal_routing('   ')
    (None, None)
    >>> str_to_postal_routing(None)
    (None, None)
    """


# Level-2 Converters


str_to_postal_distribution = pipe(
    make_str_to_slug(separator = u' ', transform = strings.upper),
    split_postal_distribution,
    struct(
        [
        noop,
        str_to_postal_routing,
            ],
        constructor = tuple,
        ),
    )
"""Convert a string to a postal routing (aka locality, ie the part of the address after the postal code).

    >>> str_to_postal_distribution(u'   75014  Paris')
    ((u'75014', u'PARIS'), None)
    >>> str_to_postal_distribution(u'   75014 Paris  14   ')
    ((u'75014', u'PARIS 14'), None)
    >>> str_to_postal_distribution(u'   42000 SAINT Etienne   ')
    ((u'42000', u'ST ETIENNE'), None)
    >>> str_to_postal_distribution(u'   42000 SAINT Étienne   ')
    ((u'42000', u'ST ETIENNE'), None)
    >>> str_to_postal_distribution(u'   44690 Saint-Fiacre-sur-Maine   ')
    ((u'44690', u'ST FIACRE SUR MAINE'), None)
    >>> str_to_postal_distribution(u'88151 Thaon-les-vosges ced')
    ((u'88151', u'THAON LES VOSGES CEDEX'), None)
    >>> str_to_postal_distribution(u'17100 Saintes')
    ((u'17100', u'SAINTES'), None)
    >>> str_to_postal_distribution('   ')
    (None, None)
    >>> str_to_postal_distribution(None)
    (None, None)
    """

