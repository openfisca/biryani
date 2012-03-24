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


"""Converters for JSON Web Tokens (JWT)"""


import calendar
import datetime

from Crypto.Hash import HMAC, SHA256, SHA384, SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from .base64conv import make_base64url_to_bytes, make_bytes_to_base64url
from .baseconv import (check, cleanup_line, exists, get, noop, pipe, struct, test, test_greater_or_equal,
    test_isinstance, test_less_or_equal)
from .jsonconv import make_json_to_str, make_str_to_json
from .states import default_state


__all__ = [
    'clean_str_to_decoded_json_web_token',
    'decoded_json_web_token_to_json',
    'make_json_to_signed_json_web_token',
    'str_to_decoded_json_web_token',
    'verify_decoded_json_web_token_signature',
    ]

digest_constructor_by_size = {
    256: SHA256,
    384: SHA384,
    512: SHA512,
    }
valid_signature_algorithms = (
#    u'ES256',
    u'HS256',
    u'HS384',
    u'HS512',
    u'RS256',
    u'RS384',
    u'RS512',
    )


def clean_str_to_decoded_json_web_token(token, state = default_state):
    if token is None:
        return None, None

    errors = {}
    value = dict(token = token)
    try:
        value['secured_input'], value['encoded_signature'] = str(token).rsplit('.', 1)
        value['encoded_header'], value['encoded_payload'] = value['secured_input'].split('.', 1)
    except:
        return value, dict(token = state._('Invalid format'))

    errors = {}
    header, error = pipe(
        make_base64url_to_bytes(add_padding = True),
        make_str_to_json(),
        )(value['encoded_header'], state = state)
    if error is None:
        value['header'] = header
    else:
        errors['encoded_header'] = state._('Invalid format')
    claims, error = pipe(
        make_base64url_to_bytes(add_padding = True),
        make_str_to_json(),
        exists,
        )(value['encoded_payload'], state = state)
    if error is not None:
        claims = None
        errors['encoded_payload'] = state._('Invalid format')
    signature, error = make_base64url_to_bytes(add_padding = True)(value['encoded_signature'], state = state)
    if error is None:
        value['signature'] = signature
    else:
        errors['encoded_signature'] = state._('Invalid format')
    if value['header'].get('typ', u'JWT') != u'JWT':
        return value, dict(header = dict(typ = state._('Not a signed JSON Web Token (JWS)')))
    if claims is not None:
        now_timestamp = calendar.timegm(datetime.datetime.utcnow().timetuple())
        value['claims'], claims_errors = pipe(
            test_isinstance(dict),
            struct(
                dict(
                    aud = pipe(
                        test_isinstance(basestring),
                        cleanup_line,
                        ),
                    exp = pipe(
                        test_isinstance((int, long)),
                        test(lambda timestamp: now_timestamp - 300 < timestamp, # Allow 5 minutes drift.
                            error = state._('Expired JSON web token'),
                            ),
                        ),
                    iat = pipe(
                        test_isinstance((int, long)),
                        test_greater_or_equal(0),
                        test_less_or_equal(now_timestamp + 300, # Allow 5 minutes drift.
                            error = state._('JSON web token issued in the future'),
                            ),
                        ),
                    iss = pipe(
                        test_isinstance(basestring),
                        cleanup_line,
                        ),
                    jti = pipe(
                        test_isinstance(basestring),
                        cleanup_line,
                        ),
                    nbf = pipe(
                        test_isinstance((int, long)),
                        test_greater_or_equal(0),
                        test(lambda timestamp: now_timestamp + 300 >= timestamp, # Allow 5 minutes drift.
                            error = state._('JSON web token not yet valid'),
                            ),
                        ),
                    prn = pipe(
                        test_isinstance(basestring),
                        cleanup_line,
                        ),
                    typ = pipe(
                        test_isinstance(basestring),
                        cleanup_line,
                        ),
                    ),
                default = noop,
                keep_empty = True,
                ),
            )(claims, state = state)
        if claims_errors is not None:
            errors['claims'] = claims_errors
    return value, errors or None


decoded_json_web_token_to_json = get('claims')


def make_json_to_signed_json_web_token(algorithm = None, json_web_key_url = None, key_id = None, private_key = None,
        shared_secret = None):
    """Return a converter that wraps JSON data into a signed JSON web token.

    cf http://tools.ietf.org/html/draft-jones-json-web-token
    """
    if algorithm is None:
        algorithm = u'none'
    assert algorithm == u'none' or algorithm in valid_signature_algorithms
    header = dict(
        alg = algorithm,
        typ = u'JWT', # type: signed JSON Web Token
        )
    if algorithm != u'none':
        algorithm_prefix = algorithm[:2]
        algorithm_size = int(algorithm[2:])
        digest_constructor = digest_constructor_by_size[algorithm_size]
#        if algorithm_prefix == u'ES':
#            TODO
#        elif algorithm_prefix == u'HS':
        if algorithm_prefix == u'HS':
            assert shared_secret is not None
            assert isinstance(shared_secret, str)
        else:
            assert algorithm_prefix == u'RS'
            assert private_key is not None
            assert isinstance(private_key, str)
            if json_web_key_url is not None:
                header['jku'] = json_web_key_url
            if key_id is not None:
                header['kid'] = key_id
            rsa_private_key = RSA.importKey(private_key)
            signer = PKCS1_v1_5.new(rsa_private_key)
    encoded_header = check(pipe(
        make_json_to_str(encoding = 'utf-8', ensure_ascii = False),
        make_bytes_to_base64url(remove_padding = True),
        ))(header)

    def json_to_signed_json_web_token(claims, state = default_state):
        if claims is None:
            return None, None

        encoded_payload, error = pipe(
            make_json_to_str(encoding = 'utf-8', ensure_ascii = False),
            make_bytes_to_base64url(remove_padding = True),
            )(claims, state = state)
        if error is not None:
            return encoded_payload, error

        secured_input = '{0}.{1}'.format(encoded_header, encoded_payload)
        if algorithm == u'none':
            signature = ''
#        elif algorithm_prefix == u'ES':
#            TODO
        elif algorithm_prefix == u'HS':
            signature = HMAC.new(shared_secret, msg = secured_input, digestmod = digest_constructor).digest()
        else:
            assert algorithm_prefix == u'RS'
            digest = digest_constructor.new(secured_input)
            signature = signer.sign(digest)
        encoded_signature = check(make_bytes_to_base64url(remove_padding = True))(signature, state = state)
        token = '{0}.{1}'.format(secured_input, encoded_signature)
        return token, None
    return json_to_signed_json_web_token


str_to_decoded_json_web_token = pipe(cleanup_line, clean_str_to_decoded_json_web_token)


def verify_decoded_json_web_token_signature(public_key_as_encoded_str = None, public_key_as_json_web_key = None,
        shared_secret = None):
    if shared_secret is not None:
        assert isinstance(shared_secret, str) # Shared secret must not be unicode.

    def verify_decoded_json_web_token_signature_converter(value, state = default_state):
        if value is None:
            return None, None

        errors = {}
        algorithm = value['header'].get('alg')
        if algorithm in valid_signature_algorithms:
            algorithm_prefix = algorithm[:2]
            algorithm_size = int(algorithm[2:])
            digest_constructor = digest_constructor_by_size[algorithm_size]
#            if algorithm_prefix == u'ES':
#                TODO
#            elif algorithm_prefix == u'HS':
            if algorithm_prefix == u'HS':
                if shared_secret is None:
                    errors['signature'] = state._('Unable to check signature: Missing shared secret')
                else:
                    verified = HMAC.new(shared_secret, msg = value['secured_input'],
                        digestmod = digest_constructor).digest() == value['signature']
            else:
                assert algorithm_prefix == u'RS'
                if public_key_as_encoded_str is None:
                    assert public_key_as_json_web_key is not None
                    public_key_dict = public_key_as_json_web_key['jwk'][-1] # TODO
                    assert public_key_dict['alg'] == u'RSA', public_key_as_json_web_key # TODO
                    public_key = RSA.construct((
                        check(make_base64url_to_bytes(add_padding = True))(public_key_dict['mod'], state = state),
                        check(make_base64url_to_bytes(add_padding = True))(public_key_dict['exp'], state = state),
                        ))
                else:
                    public_key = RSA.importKey(public_key_as_encoded_str)
                verifier = PKCS1_v1_5.new(public_key)
                try:
                    digest = digest_constructor.new(value['secured_input'])
                    verified = verifier.verify(digest, value['signature'])
                except:
                    errors['signature'] = state._('Invalid signature')
            if 'signature' not in errors and not verified:
                errors['signature'] = state._('Non authentic signature')
        elif algorithm != u'none':
            errors['header'] = dict(alg = state._('Unimplemented digital signature algorithm'))
        return value, errors or None
    return verify_decoded_json_web_token_signature_converter

