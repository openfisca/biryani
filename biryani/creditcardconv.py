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


"""Converters for credit card types, numbers and expiration dates

.. note:: The idea of this module and its algorithms have been borrowed from `FormEncode <http://formencode.org/>`_.
"""


from . import baseconv as conv
from . import states, strings


__all__ = [
    'clean_str_to_credit_card_number',
    'str_couple_to_credit_card_type_and_number',
    'str_to_credit_card_number',
    ]


credit_cards_prefix_and_length = {
    "amex": [
        ('34', 15),
        ('37', 15),
        ],
    "dinersclub": [
        ('300', 14),
        ('301', 14),
        ('302', 14),
        ('303', 14),
        ('304', 14),
        ('305', 14),
        ('36', 14),
        ('38', 14)],
    "discover": [
        ('6011', 16),
        ],
    "jcb": [
        ('3', 16),
        ('2131', 15),
        ('1800', 15),
        ],
    "mastercard": [
        ('51', 16),
        ('52', 16),
        ('53', 16),
        ('54', 16),
        ('55', 16),
        ],
    "visa": [
        ('4', 16),
        ('4', 13),
        ],
    }
N_ = conv.N_


def clean_str_to_credit_card_number(type):
    """Return a converter that converts a clean string to a credit card number of a given type.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_credit_card_number`.

    >>> clean_str_to_credit_card_number(u'visa')(u'4111111111111111')
    (u'4111111111111111', None)
    >>> clean_str_to_credit_card_number(u'visa')(u'   4111 1111-1111.,1111   ')
    (u'4111111111111111', None)
    >>> clean_str_to_credit_card_number(u'visa')(u'411111111111111')
    (u'411111111111111', u'Wrong number of digits in credit card number')
    >>> clean_str_to_credit_card_number(u'visa')(u'4111111111111112')
    (u'4111111111111112', u'Invalid credit card number (wrong checksum)')
    >>> clean_str_to_credit_card_number(u'visa')(u'5111111111111111')
    (u'5111111111111111', u'Invalid credit card number (unknown prefix)')
    >>> clean_str_to_credit_card_number(u'visa')(u'')
    (u'', u'Credit card number must contain digits')
    >>> clean_str_to_credit_card_number(u'visa')(u'   ')
    (u'', u'Credit card number must contain digits')
    >>> clean_str_to_credit_card_number(u'visa')(None)
    (None, None)
    """
    def str_to_credit_card_number_converter(credit_card_number, state = states.default_state):
        if credit_card_number is None:
            return credit_card_number, None

        # Check that credit card number contains only digits.
        credit_card_number = strings.slugify(credit_card_number, separator = u'')
        if not credit_card_number:
            return credit_card_number, state._(u'Credit card number must contain digits')
        if not credit_card_number.isdigit():
            return credit_card_number, state._(u'Credit card number must contain only digits')

        # Check prefix and length.
        length_found = False
        for prefix, length in credit_cards_prefix_and_length[type]:
            if len(credit_card_number) == length:
                length_found = True
                if credit_card_number.startswith(prefix):
                    break
        else:
            if not length_found:
                return credit_card_number, state._(u'Wrong number of digits in credit card number')
            return credit_card_number, state._(u'Invalid credit card number (unknown prefix)')

        # Check checksum.
        checksum = 0
        for index, digit in enumerate(reversed(credit_card_number)):
            if index & 1:
                for digit in unicode(2 * int(digit)):
                    checksum += int(digit)
            else:
                checksum += int(digit)
        if checksum % 10 != 0:
            return credit_card_number, state._(u'Invalid credit card number (wrong checksum)')
        return credit_card_number, None

    return str_to_credit_card_number_converter


def str_couple_to_credit_card_type_and_number(value, state = states.default_state):
    """Validate and convert a couple containing the credit card type and credit card number.

    >>> str_couple_to_credit_card_type_and_number((u'visa', u'4111111111111111'))
    ([u'visa', u'4111111111111111'], None)
    >>> str_couple_to_credit_card_type_and_number((u'   VISA   ', u'   4111 1111-1111.,1111   '))
    ([u'visa', u'4111111111111111'], None)
    >>> str_couple_to_credit_card_type_and_number((u'unknown', u'4111111111111111'))
    ([u'unknown', u'4111111111111111'], {0: u'Unknown type of credit card'})
    >>> str_couple_to_credit_card_type_and_number((u'mastercard', u'4111111111111111'))
    ([u'mastercard', u'4111111111111111'], {1: u'Invalid credit card number (unknown prefix)'})
    >>> str_couple_to_credit_card_type_and_number((u'visa', u'411111111111111'))
    ([u'visa', u'411111111111111'], {1: u'Wrong number of digits in credit card number'})
    >>> str_couple_to_credit_card_type_and_number((u'visa', u'4111111111111112'))
    ([u'visa', u'4111111111111112'], {1: u'Invalid credit card number (wrong checksum)'})
    >>> str_couple_to_credit_card_type_and_number((u'visa', u'5111111111111111'))
    ([u'visa', u'5111111111111111'], {1: u'Invalid credit card number (unknown prefix)'})
    >>> str_couple_to_credit_card_type_and_number((u'visa', u''))
    ([u'visa', None], {1: u'Missing value'})
    >>> str_couple_to_credit_card_type_and_number((u'visa', u'   '))
    ([u'visa', None], {1: u'Missing value'})
    >>> str_couple_to_credit_card_type_and_number((u'visa', None))
    ([u'visa', None], {1: u'Missing value'})
    >>> str_couple_to_credit_card_type_and_number((None, None))
    ([None, None], {0: u'Missing value', 1: u'Missing value'})
    >>> str_couple_to_credit_card_type_and_number(None)
    (None, None)
    """
    converted_value, error = conv.struct([
        conv.pipe(
            conv.str_to_slug,
            conv.test_in(credit_cards_prefix_and_length.iterkeys(), error = N_(u'Unknown type of credit card')),
            conv.test_exists,
            ),
        conv.pipe(
            conv.cleanup_line,
            conv.test_exists,
            ),
        ])(value, state = state)
    if converted_value is None or error is not None:
        return converted_value, error
    type, credit_card_number = converted_value
    return conv.struct([
        conv.noop,
        str_to_credit_card_number(type),
        ])(converted_value, state = state)


def str_to_credit_card_number(type):
    """Return a converter that converts a string to a credit card number of a given type.

    >>> str_to_credit_card_number(u'visa')(u'4111111111111111')
    (u'4111111111111111', None)
    >>> str_to_credit_card_number(u'visa')(u'   4111 1111-1111.,1111   ')
    (u'4111111111111111', None)
    >>> str_to_credit_card_number(u'visa')(u'411111111111111')
    (u'411111111111111', u'Wrong number of digits in credit card number')
    >>> str_to_credit_card_number(u'visa')(u'4111111111111112')
    (u'4111111111111112', u'Invalid credit card number (wrong checksum)')
    >>> str_to_credit_card_number(u'visa')(u'5111111111111111')
    (u'5111111111111111', u'Invalid credit card number (unknown prefix)')
    >>> str_to_credit_card_number(u'visa')(u'')
    (None, None)
    >>> str_to_credit_card_number(u'visa')(u'   ')
    (None, None)
    >>> str_to_credit_card_number(u'visa')(None)
    (None, None)
    """
    return conv.pipe(conv.cleanup_line, clean_str_to_credit_card_number(type))

