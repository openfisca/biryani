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


"""Converters for credit card types, numbers and expiration dates

.. note:: The idea of this module and its algorithms have been borrowed from `FormEncode <http://formencode.org/>`_.

Sample usage:

>>> import pprint
>>> from biryani import baseconv, creditcardconv, custom_conv, states
...
>>> conv = custom_conv(baseconv, creditcardconv)
>>> N_ = lambda message: message
...
>>> def validate_credit_card(value, state = None):
...     import datetime
...
...     if value is None:
...         return None, None
...     if state is None:
...         state = states.default_state
...     errors = {}
...     today = datetime.date.today()
...     converted_value, error = conv.struct(
...         dict(
...             credit_card_type = conv.pipe(conv.input_to_credit_card_type, conv.not_none),
...             expiration_month = conv.pipe(
...                 conv.input_to_int,
...                 conv.test_between(1, 12, error = N_(u'Invalid expiration month')),
...                 conv.not_none,
...                 ),
...             expiration_year = conv.pipe(
...                 conv.input_to_int,
...                 conv.test_greater_or_equal(today.year, error = N_(u'Invalid expiration year')),
...                 conv.not_none,
...                 ),
...             ),
...         default = conv.noop,
...         )(value, state = state)
...     if error is not None:
...         errors.update(error)
...     if 'expiration_month' not in errors and 'expiration_year' not in errors:
...         expiration_year = converted_value['expiration_year']
...         expiration_month = converted_value['expiration_month'] + 1
...         if expiration_month > 12:
...             expiration_month = 1
...             expiration_year += 1
...         if datetime.date(expiration_year, expiration_month, 1) <= today:
...             errors['expiration_month'] = state._(u'Invalid expiration date')
...     if 'credit_card_type' in errors:
...         return converted_value, errors
...     credit_card_type = converted_value['credit_card_type']
...     converted_value, error = conv.struct(
...         dict(
...             credit_card_number = conv.pipe(
...                 conv.make_input_to_credit_card_number(credit_card_type),
...                 conv.not_none,
...                 ),
...             credit_card_security_code = conv.pipe(
...                 conv.make_input_to_credit_card_security_code(credit_card_type),
...                 conv.not_none,
...                 ),
...             ),
...         default = conv.noop,
...         )(converted_value, state = state)
...     if error is not None:
...         errors.update(error)
...     return converted_value, errors or None

>>> pprint.pprint(validate_credit_card(dict(
...     credit_card_type = u'Visa',
...     credit_card_number = u'4111 1111 1111 1111',
...     credit_card_security_code = u'123',
...     expiration_month = u'12',
...     expiration_year = u'2021',
...     )))
({'credit_card_number': u'4111111111111111',
  'credit_card_security_code': 123,
  'credit_card_type': u'visa',
  'expiration_month': 12,
  'expiration_year': 2021},
 None)
>>> pprint.pprint(validate_credit_card(dict(
...     credit_card_type = u'Visa',
...     credit_card_number = u'4111-1111-1111-1112',
...     credit_card_security_code = u'123',
...     expiration_month = u'12',
...     expiration_year = u'2021',
...     )))
({'credit_card_number': u'4111111111111112',
  'credit_card_security_code': 123,
  'credit_card_type': u'visa',
  'expiration_month': 12,
  'expiration_year': 2021},
 {'credit_card_number': u'Invalid credit card number (wrong checksum)'})
>>> pprint.pprint(validate_credit_card(dict(
...     credit_card_type = u'Visa',
...     credit_card_number = u'4111_1111_1111',
...     credit_card_security_code = u'1234',
...     expiration_month = u'7',
...     expiration_year = u'2011',
...     )))
({'credit_card_number': u'411111111111',
  'credit_card_security_code': u'1234',
  'credit_card_type': u'visa',
  'expiration_month': 7,
  'expiration_year': 2011},
 {'credit_card_number': u'Wrong number of digits in credit card number',
  'credit_card_security_code': u'Invalid security code for credit card',
  'expiration_year': u'Invalid expiration year'})
"""


from .baseconv import cleanup_line, N_, pipe, input_to_int, input_to_slug, test, test_in
from . import states, strings


__all__ = [
    'input_to_credit_card_type',
    'make_input_to_credit_card_number',
    'make_input_to_credit_card_security_code',
    'make_str_to_credit_card_number',
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
credit_cards_security_code_length = {
    "amex": 4,
    "discover": 3,
    "mastercard": 3,
    "visa": 3,
    }


# Level-1 Converters


input_to_credit_card_type = pipe(
    input_to_slug,
    test_in(credit_cards_prefix_and_length.keys(), error = N_(u'Unknown type of credit card')),
    )


def make_input_to_credit_card_security_code(type):
    """Return a converter that converts a string to a security code for a given type of credit card.
    """
    return pipe(
        cleanup_line,
        test(lambda value: len(value) == credit_cards_security_code_length[type],
            error = N_(u'Invalid security code for credit card')),
        input_to_int,
        )


def make_str_to_credit_card_number(type):
    """Return a converter that converts a clean string to a credit card number of a given type.

    .. note:: For a converter that doesn't require a clean string, see :func:`make_input_to_credit_card_number`.

    >>> make_str_to_credit_card_number(u'visa')(u'4111111111111111')
    (u'4111111111111111', None)
    >>> make_str_to_credit_card_number(u'visa')(u'   4111 1111-1111.,1111   ')
    (u'4111111111111111', None)
    >>> make_str_to_credit_card_number(u'visa')(u'411111111111111')
    (u'411111111111111', u'Wrong number of digits in credit card number')
    >>> make_str_to_credit_card_number(u'visa')(u'4111111111111112')
    (u'4111111111111112', u'Invalid credit card number (wrong checksum)')
    >>> make_str_to_credit_card_number(u'visa')(u'5111111111111111')
    (u'5111111111111111', u'Invalid credit card number (unknown prefix)')
    >>> make_str_to_credit_card_number(u'visa')(u'')
    (u'', u'Credit card number must contain digits')
    >>> make_str_to_credit_card_number(u'visa')(u'   ')
    (u'', u'Credit card number must contain digits')
    >>> make_str_to_credit_card_number(u'visa')(None)
    (None, None)
    """
    def str_to_credit_card_number(credit_card_number, state = None):
        if credit_card_number is None:
            return credit_card_number, None
        if state is None:
            state = states.default_state

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
                return credit_card_number, state._(
                    u'Wrong number of digits in credit card number')
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

    return str_to_credit_card_number


# Level-2 Converters


def make_input_to_credit_card_number(type):
    """Return a converter that converts a string to a credit card number for a given credit card type.

    >>> make_input_to_credit_card_number(u'visa')(u'4111111111111111')
    (u'4111111111111111', None)
    >>> make_input_to_credit_card_number(u'visa')(u'   4111 1111-1111.,1111   ')
    (u'4111111111111111', None)
    >>> make_input_to_credit_card_number(u'visa')(u'411111111111111')
    (u'411111111111111', u'Wrong number of digits in credit card number')
    >>> make_input_to_credit_card_number(u'visa')(u'4111111111111112')
    (u'4111111111111112', u'Invalid credit card number (wrong checksum)')
    >>> make_input_to_credit_card_number(u'visa')(u'5111111111111111')
    (u'5111111111111111', u'Invalid credit card number (unknown prefix)')
    >>> make_input_to_credit_card_number(u'visa')(u'')
    (None, None)
    >>> make_input_to_credit_card_number(u'visa')(u'   ')
    (None, None)
    >>> make_input_to_credit_card_number(u'visa')(None)
    (None, None)
    """
    return pipe(cleanup_line, make_str_to_credit_card_number(type))
