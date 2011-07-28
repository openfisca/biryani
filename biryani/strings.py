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


"""Strings simplification functions"""


import unicodedata


__all__ = ['deep_decode', 'deep_encode', 'normalize', 'slugify']

ASCII_TRANSLATIONS = {
    u'\N{NO-BREAK SPACE}': ' ',
    u'\N{LATIN CAPITAL LETTER A WITH ACUTE}': 'A',
    u'\N{LATIN CAPITAL LETTER A WITH CIRCUMFLEX}': 'A',
    u'\N{LATIN CAPITAL LETTER A WITH DIAERESIS}': 'A',
    u'\N{LATIN CAPITAL LETTER A WITH GRAVE}': 'A',
    u'\N{LATIN CAPITAL LETTER A WITH RING ABOVE}': 'A',
    u'\N{LATIN CAPITAL LETTER A WITH TILDE}': 'A',
    u'\N{LATIN CAPITAL LETTER AE}': 'Ae',
    u'\N{LATIN CAPITAL LETTER C WITH CEDILLA}': 'C',
    u'\N{LATIN CAPITAL LETTER E WITH ACUTE}': 'E',
    u'\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}': 'E',
    u'\N{LATIN CAPITAL LETTER E WITH DIAERESIS}': 'E',
    u'\N{LATIN CAPITAL LETTER E WITH GRAVE}': 'E',
    u'\N{LATIN CAPITAL LETTER ETH}': 'Th',
    u'\N{LATIN CAPITAL LETTER I WITH ACUTE}': 'I',
    u'\N{LATIN CAPITAL LETTER I WITH CIRCUMFLEX}': 'I',
    u'\N{LATIN CAPITAL LETTER I WITH DIAERESIS}': 'I',
    u'\N{LATIN CAPITAL LETTER I WITH GRAVE}': 'I',
    u'\N{LATIN CAPITAL LETTER N WITH TILDE}': 'N',
    u'\N{LATIN CAPITAL LETTER O WITH ACUTE}': 'O',
    u'\N{LATIN CAPITAL LETTER O WITH CIRCUMFLEX}': 'O',
    u'\N{LATIN CAPITAL LETTER O WITH DIAERESIS}': 'O',
    u'\N{LATIN CAPITAL LETTER O WITH GRAVE}': 'O',
    u'\N{LATIN CAPITAL LETTER O WITH STROKE}': 'O',
    u'\N{LATIN CAPITAL LETTER O WITH TILDE}': 'O',
    u'\N{LATIN CAPITAL LIGATURE OE}': 'Oe',
    u'\N{LATIN CAPITAL LETTER THORN}': 'th',
    u'\N{LATIN CAPITAL LETTER U WITH ACUTE}': 'U',
    u'\N{LATIN CAPITAL LETTER U WITH CIRCUMFLEX}': 'U',
    u'\N{LATIN CAPITAL LETTER U WITH DIAERESIS}': 'U',
    u'\N{LATIN CAPITAL LETTER U WITH GRAVE}': 'U',
    u'\N{LATIN CAPITAL LETTER Y WITH ACUTE}': 'Y',
    u'\N{LATIN SMALL LETTER A WITH ACUTE}': 'a',
    u'\N{LATIN SMALL LETTER A WITH CIRCUMFLEX}': 'a',
    u'\N{LATIN SMALL LETTER A WITH DIAERESIS}': 'a',
    u'\N{LATIN SMALL LETTER A WITH GRAVE}': 'a',
    u'\N{LATIN SMALL LETTER A WITH RING ABOVE}': 'a',
    u'\N{LATIN SMALL LETTER A WITH TILDE}': 'a',
    u'\N{LATIN SMALL LETTER AE}': 'ae',
    u'\N{LATIN SMALL LETTER C WITH CEDILLA}': 'c',
    u'\N{LATIN SMALL LETTER E WITH ACUTE}': 'e',
    u'\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}': 'e',
    u'\N{LATIN SMALL LETTER E WITH DIAERESIS}': 'e',
    u'\N{LATIN SMALL LETTER E WITH GRAVE}': 'e',
    u'\N{LATIN SMALL LETTER ETH}': 'th',
    u'\N{LATIN SMALL LETTER I WITH ACUTE}': 'i',
    u'\N{LATIN SMALL LETTER I WITH CIRCUMFLEX}': 'i',
    u'\N{LATIN SMALL LETTER I WITH DIAERESIS}': 'i',
    u'\N{LATIN SMALL LETTER I WITH GRAVE}': 'i',
    u'\N{LATIN SMALL LETTER N WITH TILDE}': 'n',
    u'\N{LATIN SMALL LETTER O WITH ACUTE}': 'o',
    u'\N{LATIN SMALL LETTER O WITH CIRCUMFLEX}': 'o',
    u'\N{LATIN SMALL LETTER O WITH DIAERESIS}': 'o',
    u'\N{LATIN SMALL LETTER O WITH GRAVE}': 'o',
    u'\N{LATIN SMALL LETTER O WITH STROKE}': 'o',
    u'\N{LATIN SMALL LETTER O WITH TILDE}': 'o',
    u'\N{LATIN SMALL LIGATURE OE}': 'oe',
    u'\N{LATIN SMALL LETTER SHARP S}': 'ss',
    u'\N{LATIN SMALL LETTER THORN}': 'th',
    u'\N{LATIN SMALL LETTER U WITH ACUTE}': 'u',
    u'\N{LATIN SMALL LETTER U WITH CIRCUMFLEX}': 'u',
    u'\N{LATIN SMALL LETTER U WITH DIAERESIS}': 'u',
    u'\N{LATIN SMALL LETTER U WITH GRAVE}': 'u',
    u'\N{LATIN SMALL LETTER Y WITH ACUTE}': 'y',
    u'\N{LATIN SMALL LETTER Y WITH DIAERESIS}': 'y',
    u'\N{LEFT SINGLE QUOTATION MARK}': "'",
    u'\N{RIGHT SINGLE QUOTATION MARK}': "'",
    }


def deep_decode(value, encoding = 'utf-8'):
    """Convert recursively bytes strings embedded in Python data to unicode strings."""
    return value if isinstance(value, unicode) else value.decode(encoding) if isinstance(value, str) \
        else dict(
            (to_unicode(name, encoding = encoding), to_unicode(item, encoding = encoding))
            for name, item in value.iteritems()
            ) if isinstance(value, dict) \
        else [
            to_unicode(item, encoding = encoding)
            for item in value
            ] if isinstance(value, list) \
        else tuple(
            to_unicode(item, encoding = encoding)
            for item in value
            ) if isinstance(value, tuple) \
        else value


def deep_encode(value, encoding = 'utf-8'):
    """Convert recursively unicode strings embedded in Python data to encoded strings."""
    return value if isinstance(value, str) else value.encode(encoding) if isinstance(value, unicode) \
        else dict(
            (to_string(name, encoding = encoding), to_string(item, encoding = encoding))
            for name, item in value.iteritems()
            ) if isinstance(value, dict) \
        else [
            to_string(item, encoding = encoding)
            for item in value
            ] if isinstance(value, list) \
        else tuple(
            to_string(item, encoding = encoding)
            for item in value
            ) if isinstance(value, tuple) \
        else value


def lower(s):
    return s.lower()


def normalize(s, encoding = 'utf-8', separator = u' ', transform = lower):
    """Convert a string to its normal form using compatibility decomposition and removing combining characters."""
    if isinstance(s, str):
        s = s.decode(encoding)
    assert isinstance(s, unicode), str((s,))
    normalized = u''.join(c for c in unicodedata.normalize('NFKD', s) if unicodedata.combining(c) == 0)
    normalized = separator.join(normalized.strip().split())
    if transform is not None:
        normalized = transform(normalized)
    return normalized


def slugify(s, encoding = 'utf-8', separator = '-', transform = lower):
    """Simplify a string, converting it to a lowercase ASCII subset."""
    if isinstance(s, str):
        s = s.decode(encoding)
    assert isinstance(s, unicode), str((s,))
    simplified = ''.join([slugify_char(unicode_char) for unicode_char in s])
    while '  ' in simplified:
        simplified = simplified.replace('  ', ' ')
    simplified = simplified.strip()
    if separator != ' ':
        simplified = simplified.replace(' ', separator)
    if transform is not None:
        simplified = transform(simplified)
    return simplified


def slugify_char(unicode_char):
    """Convert an unicode character to a subset of uppercase ASCII characters or an empty string.

    The result can be composed of several characters (for example, 'œ' becomes 'OE').
    """
    chars = unicode_char_to_ascii(unicode_char)
    if chars:
        chars = chars.upper()
        split_chars = []
        for char in chars:
            if char not in ' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                char = ' '
            split_chars.append(char)
        chars = ''.join(split_chars)
    return chars


def unicode_char_to_ascii(unicode_char):
    """Convert an unicode character to several ASCII characters"""
    chars = ASCII_TRANSLATIONS.get(unicode_char)
    if chars is None:
        if ord(unicode_char) < 0x80:
            chars = str(unicode_char)
        else:
            chars = ''
    return chars


def upper(s):
    return s.upper()

