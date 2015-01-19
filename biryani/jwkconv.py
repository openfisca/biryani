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


"""Converters for JSON Web Keys (JWK)"""


from .base64conv import make_base64url_to_bytes
from .baseconv import (function, noop, not_none, pipe, struct, switch, test_conv, test_in, test_isinstance,
    uniform_sequence)


__all__ = [
    'json_to_json_web_key',
    'json_to_json_web_key_set',
    ]


json_to_json_web_key = pipe(
    test_isinstance(dict),
    struct(
        dict(
            alg = pipe(
                test_isinstance(basestring),
                test_in([
                    u'EC',
                    u'RSA',
                    ]),
                not_none,
                ),
            kid = test_isinstance(basestring),
            use = pipe(
                test_isinstance(basestring),
                test_in([
                    u'enc',
                    u'sig',
                    ]),
                ),
            ),
        default = noop,
        ),
    switch(
        function(lambda key_object: key_object['alg']),
        dict(
            EC = struct(dict(
                alg = noop,
                crv = pipe(
                    test_isinstance(basestring),
                    test_in([
                        u'P-256',
                        u'P-384',
                        u'P-521',
                        ]),
                    not_none,
                    ),
                kid = noop,
                use = noop,
                x = pipe(
                    test_isinstance(basestring),
                    test_conv(make_base64url_to_bytes(add_padding = True)),
                    not_none,
                    ),
                y = pipe(
                    test_isinstance(basestring),
                    test_conv(make_base64url_to_bytes(add_padding = True)),
                    not_none,
                    ),
                )),
            RSA = struct(dict(
                alg = noop,
                exp = pipe(
                    test_isinstance(basestring),
                    test_conv(make_base64url_to_bytes(add_padding = True)),
                    not_none,
                    ),
                kid = noop,
                mod = pipe(
                    test_isinstance(basestring),
                    test_conv(make_base64url_to_bytes(add_padding = True)),
                    not_none,
                    ),
                use = noop,
                )),
            ),
        ),
    )
"""Verify that given JSON is a valid JSON Web Key object.

    A JWK Key Object is a JSON object that represents a single public key.
    """


json_to_json_web_key_set = pipe(
    test_isinstance(dict),
    struct(
        dict(
            jwk = pipe(
                test_isinstance(list),
                uniform_sequence(json_to_json_web_key),
                not_none,
                ),
            ),
        ),
    )
"""Verify that given JSON is a valid JSON Web Key.

    >>> from pprint import pprint
    >>> pprint(json_to_json_web_key_set({'jwk': [{
    ...     'alg': u'EC',
    ...     'crv': u'P-256',
    ...     'kid': u'1',
    ...     'use': u'enc',
    ...     'x': u'MKBCTNIcKUSDii11ySs3526iDZ8AiTo7Tu6KPAqv7D4',
    ...     'y': u'4Etl6SRW2YiLUrN5vfvVHuhp7x8PxltmWWlbbM4IFyM',
    ...     }]}))
    ({'jwk': [{'alg': u'EC',
               'crv': u'P-256',
               'kid': u'1',
               'use': u'enc',
               'x': u'MKBCTNIcKUSDii11ySs3526iDZ8AiTo7Tu6KPAqv7D4',
               'y': u'4Etl6SRW2YiLUrN5vfvVHuhp7x8PxltmWWlbbM4IFyM'}]},
     None)

    >>> from biryani.jsonconv import make_input_to_json
    >>> pprint(conv.pipe(make_input_to_json(), json_to_json_web_key_set)('''
    ... {"jwk":
    ...   [
    ...     {"alg":"EC",
    ...      "crv":"P-256",
    ...      "x":"MKBCTNIcKUSDii11ySs3526iDZ8AiTo7Tu6KPAqv7D4",
    ...      "y":"4Etl6SRW2YiLUrN5vfvVHuhp7x8PxltmWWlbbM4IFyM",
    ...      "use":"enc",
    ...      "kid":"1"},
    ...     {"alg":"RSA",
    ...      "mod": "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw",
    ...      "exp":"AQAB",
    ...      "kid":"2011-04-29"}
    ...   ]
    ... }
    ... '''))
    ({'jwk': [{'alg': u'EC',
               'crv': u'P-256',
               'kid': u'1',
               'use': u'enc',
               'x': u'MKBCTNIcKUSDii11ySs3526iDZ8AiTo7Tu6KPAqv7D4',
               'y': u'4Etl6SRW2YiLUrN5vfvVHuhp7x8PxltmWWlbbM4IFyM'},
              {'alg': u'RSA',
               'exp': u'AQAB',
               'kid': u'2011-04-29',
               'mod': u'0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw',
               'use': None}]},
     None)
    """
