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


"""Converters for JSON Web Tokens (JWT)

cf http://tools.ietf.org/html/draft-jones-json-web-token
"""


import calendar
import datetime
from struct import pack
import zlib

from Crypto import Random
from Crypto.Cipher import AES as Cipher_AES, PKCS1_v1_5 as Cipher_PKCS1_v1_5, PKCS1_OAEP as Cipher_PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5 as Signature_PKCS1_v1_5
from Crypto.Hash import HMAC, SHA256, SHA384, SHA512
from Crypto.PublicKey import RSA
from Crypto.Util import number

from . import gcm, states
from .base64conv import base64_to_bytes, make_base64url_to_bytes, make_bytes_to_base64url
from .baseconv import (check, cleanup_line, get, make_input_to_url, N_, noop, not_none, pipe, struct, test,
    test_greater_or_equal, test_in, test_isinstance, test_less_or_equal, uniform_sequence)
from .jsonconv import make_json_to_str, make_input_to_json
from .jwkconv import json_to_json_web_key


__all__ = [
    'decode_json_web_token',
    'decode_json_web_token_claims',
    'decoded_json_web_token_to_json',
    'decrypt_json_web_token',
    'derive_key',
    'encrypt_json_web_token',
    'input_to_json_web_token',
    'make_json_to_json_web_token',
    'make_payload_to_json_web_token',
    'sign_json_web_token',
    'verify_decoded_json_web_token_signature',
    'verify_decoded_json_web_token_time',
    ]

digest_constructor_by_size = {
    256: SHA256,
    384: SHA384,
    512: SHA512,
    }
valid_encryption_algorithms = (
    u'A128KW',
    u'A256KW',
    # u'ECDH-ES',
    u'RSA1_5',
    u'RSA-OAEP',
    )
valid_encryption_methods = (
    u'A128CBC',
    u'A256CBC',
    u'A128GCM',
    u'A256GCM',
    )
valid_integrity_algorithms = (
    u'HS256',
    u'HS384',
    u'HS512',
    )
valid_key_derivation_functions = (
    u'CS256',
    u'CS384',
    u'CS512',
    )
valid_signature_algorithms = (
    # u'ES256',
    u'HS256',
    u'HS384',
    u'HS512',
    u'RS256',
    u'RS384',
    u'RS512',
    )


def decode_json_web_token(token, state = None):
    """Decode a JSON Web Token, without converting payload to JSON claims, nor verifying its content."""
    if token is None:
        return None, None
    if state is None:
        state = states.default_state

    errors = {}
    decoded_token = dict(token = token)
    try:
        decoded_token['secured_input'], decoded_token['encoded_signature'] = str(token).rsplit('.', 1)
        decoded_token['encoded_header'], decoded_token['encoded_payload'] = decoded_token['secured_input'].split('.', 1)
    except:
        return decoded_token, dict(token = state._(u'Invalid format'))

    errors = {}
    header, error = pipe(
        make_base64url_to_bytes(add_padding = True),
        make_input_to_json(),
        )(decoded_token['encoded_header'], state = state)
    if error is None:
        decoded_token['header'] = header
    else:
        errors['encoded_header'] = state._(u'Invalid format')
    payload, error = pipe(
        make_base64url_to_bytes(add_padding = True),
        not_none,
        )(decoded_token['encoded_payload'], state = state)
    if error is None:
        decoded_token['payload'] = payload
    else:
        payload = None
        errors['encoded_payload'] = state._(u'Invalid format')
    signature, error = make_base64url_to_bytes(add_padding = True)(decoded_token['encoded_signature'], state = state)
    if error is None:
        decoded_token['signature'] = signature
    else:
        errors['encoded_signature'] = state._(u'Invalid format')
    if decoded_token['header'].get('typ', u'JWT') not in (u'JWT', u'urn:ietf:params:oauth:token-type:jwt'):
        return decoded_token, dict(header = dict(typ = state._(u'Not a JSON Web Token')))
    return decoded_token, errors or None


def decode_json_web_token_claims(decoded_token, state = None):
    if decoded_token is None:
        return None, None
    if state is None:
        state = states.default_state

    claims, errors = pipe(
        make_input_to_json(),
        test_isinstance(dict),
        struct(
            dict(
                aud = pipe(
                    test_isinstance(basestring),
                    cleanup_line,
                    ),
                exp = pipe(
                    test_isinstance((int, long)),
                    test_greater_or_equal(0),
                    ),
                iat = pipe(
                    test_isinstance((int, long)),
                    test_greater_or_equal(0),
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
            ),
        )(decoded_token.get('payload'), state = state)
    if errors is not None:
        return decoded_token, dict(claims = errors)
    decoded_token['claims'] = claims
    return decoded_token, None


decoded_json_web_token_to_json = get('claims')


def decrypt_json_web_token(private_key = None, require_encrypted_token = False, shared_secret = None):
    """Return a converter that decrypts a JSON Web Token and returns a non crypted JSON Web Token.

    >>> from Crypto.PublicKey import RSA
    >>> from Crypto.Util import number

    >>> # Mike Jones Test 1

    >>> plaintext_bytes_list = [78, 111, 119, 32, 105, 115, 32, 116, 104, 101, 32, 116, 105, 109, 101, 32,
    ...    102, 111, 114, 32, 97, 108, 108, 32, 103, 111, 111, 100, 32, 109, 101, 110,
    ...    32, 116, 111, 32, 99, 111, 109, 101, 32, 116, 111, 32, 116, 104, 101, 32,
    ...    97, 105, 100, 32, 111, 102, 32, 116, 104, 101, 105, 114, 32, 99, 111, 117,
    ...    110, 116, 114, 121, 46]
    >>> plaintext = ''.join(chr(byte) for byte in plaintext_bytes_list)
    >>> jwt = check(make_payload_to_json_web_token())(plaintext)
    >>> jwt
    'eyJhbGciOiJub25lIn0.Tm93IGlzIHRoZSB0aW1lIGZvciBhbGwgZ29vZCBtZW4gdG8gY29tZSB0byB0aGUgYWlkIG9mIHRoZWlyIGNvdW50cnku.'

    >>> cmk_bytes_list = [4, 211, 31, 197, 84, 157, 252, 254, 11, 100, 157, 250, 63, 170, 106, 206,
    ...     107, 124, 212, 45, 111, 107, 9, 219, 200, 177, 0, 240, 143, 156, 44, 207]
    >>> cmk = ''.join(chr(byte) for byte in cmk_bytes_list)
    >>> iv_bytes_list = [3, 22, 60, 12, 43, 67, 104, 105, 108, 108, 105, 99, 111, 116, 104, 101]
    >>> iv = ''.join(chr(byte) for byte in iv_bytes_list)
    >>> key_modulus_bytes_list = [177, 119, 33, 13, 164, 30, 108, 121, 207, 136, 107, 242, 12, 224, 19, 226,
    ...    198, 134, 17, 71, 173, 75, 42, 61, 48, 162, 206, 161, 97, 108, 185, 234,
    ...    226, 219, 118, 206, 118, 5, 169, 224, 60, 181, 90, 85, 51, 123, 6, 224,
    ...    4, 122, 29, 230, 151, 12, 244, 127, 121, 25, 4, 85, 220, 144, 215, 110,
    ...    130, 17, 68, 228, 129, 138, 7, 130, 231, 40, 212, 214, 17, 179, 28, 124,
    ...    151, 178, 207, 20, 14, 154, 222, 113, 176, 24, 198, 73, 211, 113, 9, 33,
    ...    178, 80, 13, 25, 21, 25, 153, 212, 206, 67, 154, 147, 70, 194, 192, 183,
    ...    160, 83, 98, 236, 175, 85, 23, 97, 75, 199, 177, 73, 145, 50, 253, 206,
    ...    32, 179, 254, 236, 190, 82, 73, 67, 129, 253, 252, 220, 108, 136, 138, 11,
    ...    192, 1, 36, 239, 228, 55, 81, 113, 17, 25, 140, 63, 239, 146, 3, 172,
    ...    96, 60, 227, 233, 64, 255, 224, 173, 225, 228, 229, 92, 112, 72, 99, 97,
    ...    26, 87, 187, 123, 46, 50, 90, 202, 117, 73, 10, 153, 47, 224, 178, 163,
    ...    77, 48, 46, 154, 33, 148, 34, 228, 33, 172, 216, 89, 46, 225, 127, 68,
    ...    146, 234, 30, 147, 54, 146, 5, 133, 45, 78, 254, 85, 55, 75, 213, 86,
    ...    194, 218, 215, 163, 189, 194, 54, 6, 83, 36, 18, 153, 53, 7, 48, 89,
    ...    35, 66, 144, 7, 65, 154, 13, 97, 75, 55, 230, 132, 3, 13, 239, 71]
    >>> key_modulus = ''.join(chr(byte) for byte in key_modulus_bytes_list)
    >>> key_public_exponent_bytes_list = [1, 0, 1]
    >>> key_public_exponent = ''.join(chr(byte) for byte in key_public_exponent_bytes_list)
    >>> public_key = RSA.construct((number.bytes_to_long(key_modulus),
    ...     number.bytes_to_long(key_public_exponent)))
    >>> public_key_as_encoded_str = public_key.exportKey()
    >>> print public_key_as_encoded_str
    -----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsXchDaQebHnPiGvyDOAT
    4saGEUetSyo9MKLOoWFsueri23bOdgWp4Dy1WlUzewbgBHod5pcM9H95GQRV3JDX
    boIRROSBigeC5yjU1hGzHHyXss8UDprecbAYxknTcQkhslANGRUZmdTOQ5qTRsLA
    t6BTYuyvVRdhS8exSZEy/c4gs/7svlJJQ4H9/NxsiIoLwAEk7+Q3UXERGYw/75ID
    rGA84+lA/+Ct4eTlXHBIY2EaV7t7LjJaynVJCpkv4LKjTTAumiGUIuQhrNhZLuF/
    RJLqHpM2kgWFLU7+VTdL1VbC2tejvcI2BlMkEpk1BzBZI0KQB0GaDWFLN+aEAw3v
    RwIDAQAB
    -----END PUBLIC KEY-----
    >>> encrypted_key_bytes_list = [32, 242, 63, 207, 94, 246, 133, 37, 135, 48, 88, 4, 15, 193, 6, 244,
    ...     51, 58, 132, 133, 212, 255, 163, 90, 59, 80, 200, 152, 41, 244, 188, 215,
    ...     174, 160, 26, 188, 227, 180, 165, 234, 172, 63, 24, 116, 152, 28, 149, 16,
    ...     94, 213, 201, 171, 180, 191, 11, 21, 149, 172, 143, 54, 194, 58, 206, 201,
    ...     164, 28, 107, 155, 75, 101, 22, 92, 227, 144, 95, 40, 119, 170, 7, 36,
    ...     225, 40, 141, 186, 213, 7, 175, 16, 174, 122, 75, 32, 48, 193, 119, 202,
    ...     41, 152, 210, 190, 68, 57, 119, 4, 197, 74, 7, 242, 239, 170, 204, 73,
    ...     75, 213, 202, 113, 216, 18, 23, 66, 106, 208, 69, 244, 117, 147, 2, 37,
    ...     207, 199, 184, 96, 102, 44, 70, 212, 87, 143, 253, 0, 166, 59, 41, 115,
    ...     217, 80, 165, 87, 38, 5, 9, 184, 202, 68, 67, 176, 4, 87, 254, 166,
    ...     227, 88, 124, 238, 249, 75, 114, 205, 148, 149, 45, 78, 193, 134, 64, 189,
    ...     168, 76, 170, 76, 176, 72, 148, 77, 215, 159, 146, 55, 189, 213, 85, 253,
    ...     135, 200, 59, 247, 79, 37, 22, 200, 32, 110, 53, 123, 54, 39, 9, 178,
    ...     231, 238, 95, 25, 211, 143, 87, 220, 88, 138, 209, 13, 227, 72, 58, 102,
    ...     164, 136, 241, 14, 14, 45, 32, 77, 44, 244, 162, 239, 150, 248, 181, 138,
    ...     251, 116, 245, 205, 137, 78, 34, 34, 10, 6, 59, 4, 197, 2, 153, 251]
    >>> encrypted_key = ''.join(chr(byte) for byte in encrypted_key_bytes_list)
    >>> encryptor = encrypt_json_web_token(algorithm = 'RSA1_5', content_master_key = cmk,
    ...     encrypted_key = encrypted_key, initialization_vector = iv, integrity = 'HS256', method = 'A128CBC',
    ...     public_key_as_encoded_str = public_key_as_encoded_str)
    >>> jwe = check(encryptor)(jwt)
    >>> jwe
    'eyJhbGciOiJSU0ExXzUiLCJlbmMiOiJBMTI4Q0JDIiwiaW50IjoiSFMyNTYiLCJpdiI6IkF4WThEQ3REYUdsc2JHbGpiM1JvWlEifQ.IPI_z172h\
SWHMFgED8EG9DM6hIXU_6NaO1DImCn0vNeuoBq847Sl6qw_GHSYHJUQXtXJq7S_CxWVrI82wjrOyaQca5tLZRZc45BfKHeqByThKI261QevEK56SyAwwX\
fKKZjSvkQ5dwTFSgfy76rMSUvVynHYEhdCatBF9HWTAiXPx7hgZixG1FeP_QCmOylz2VClVyYFCbjKREOwBFf-puNYfO75S3LNlJUtTsGGQL2oTKpMsEi\
UTdefkje91VX9h8g7908lFsggbjV7NicJsufuXxnTj1fcWIrRDeNIOmakiPEODi0gTSz0ou-W-LWK-3T1zYlOIiIKBjsExQKZ-w._Z_djlIoC4MDSCKir\
eWS2beti4Q6iSG2UjFujQvdz-_PQdUcFNkOulegD6BgjgdFLjeB4HHOO7UHvP8PEDu0a0sA2a_-CI0w2YQQ2QQe35M.c41k4T4eAgCCt63m8ZNmiOinMc\
iFFypOFpvid7i6D0k'

    >>> key_private_exponent_bytes_list = [84, 80, 150, 58, 165, 235, 242, 123, 217, 55, 38, 154, 36, 181, 221, 156,
    ...    211, 215, 100, 164, 90, 88, 40, 228, 83, 148, 54, 122, 4, 16, 165, 48,
    ...    76, 194, 26, 107, 51, 53, 179, 165, 31, 18, 198, 173, 78, 61, 56, 97,
    ...    252, 158, 140, 80, 63, 25, 223, 156, 36, 203, 214, 252, 120, 67, 180, 167,
    ...    3, 82, 243, 25, 97, 214, 83, 133, 69, 16, 104, 54, 160, 200, 41, 83,
    ...    164, 187, 70, 153, 111, 234, 242, 158, 175, 28, 198, 48, 211, 45, 148, 58,
    ...    23, 62, 227, 74, 52, 117, 42, 90, 41, 249, 130, 154, 80, 119, 61, 26,
    ...    193, 40, 125, 10, 152, 174, 227, 225, 205, 32, 62, 66, 6, 163, 100, 99,
    ...    219, 19, 253, 25, 105, 80, 201, 29, 252, 157, 237, 69, 1, 80, 171, 167,
    ...    20, 196, 156, 109, 249, 88, 0, 3, 152, 38, 165, 72, 87, 6, 152, 71,
    ...    156, 214, 16, 71, 30, 82, 51, 103, 76, 218, 63, 9, 84, 163, 249, 91,
    ...    215, 44, 238, 85, 101, 240, 148, 1, 82, 224, 91, 135, 105, 127, 84, 171,
    ...    181, 152, 210, 183, 126, 24, 46, 196, 90, 173, 38, 245, 219, 186, 222, 27,
    ...    240, 212, 194, 15, 66, 135, 226, 178, 190, 52, 245, 74, 65, 224, 81, 100,
    ...    85, 25, 204, 165, 203, 187, 175, 84, 100, 82, 15, 11, 23, 202, 151, 107,
    ...    54, 41, 207, 3, 136, 229, 134, 131, 93, 139, 50, 182, 204, 93, 130, 89]
    >>> key_private_exponent = ''.join(chr(byte) for byte in key_private_exponent_bytes_list)
    >>> private_key = RSA.construct((number.bytes_to_long(key_modulus),
    ...     number.bytes_to_long(key_public_exponent), number.bytes_to_long(key_private_exponent)))
    >>> private_key_as_encoded_str = private_key.exportKey()
    >>> print private_key_as_encoded_str
    -----BEGIN RSA PRIVATE KEY-----
    MIIEpAIBAAKCAQEAsXchDaQebHnPiGvyDOAT4saGEUetSyo9MKLOoWFsueri23bO
    dgWp4Dy1WlUzewbgBHod5pcM9H95GQRV3JDXboIRROSBigeC5yjU1hGzHHyXss8U
    DprecbAYxknTcQkhslANGRUZmdTOQ5qTRsLAt6BTYuyvVRdhS8exSZEy/c4gs/7s
    vlJJQ4H9/NxsiIoLwAEk7+Q3UXERGYw/75IDrGA84+lA/+Ct4eTlXHBIY2EaV7t7
    LjJaynVJCpkv4LKjTTAumiGUIuQhrNhZLuF/RJLqHpM2kgWFLU7+VTdL1VbC2tej
    vcI2BlMkEpk1BzBZI0KQB0GaDWFLN+aEAw3vRwIDAQABAoIBAFRQljql6/J72Tcm
    miS13ZzT12SkWlgo5FOUNnoEEKUwTMIaazM1s6UfEsatTj04YfyejFA/Gd+cJMvW
    /HhDtKcDUvMZYdZThUUQaDagyClTpLtGmW/q8p6vHMYw0y2UOhc+40o0dSpaKfmC
    mlB3PRrBKH0KmK7j4c0gPkIGo2Rj2xP9GWlQyR38ne1FAVCrpxTEnG35WAADmCal
    SFcGmEec1hBHHlIzZ0zaPwlUo/lb1yzuVWXwlAFS4FuHaX9Uq7WY0rd+GC7EWq0m
    9du63hvw1MIPQofisr409UpB4FFkVRnMpcu7r1RkUg8LF8qXazYpzwOI5YaDXYsy
    tsxdglkCgYEAuKlCKvKv/ZJMVcdIs5vVSU/6cPtYI1ljWytExV/skstvRSNi9r66
    jdd9+yBhVfuG4shsp2j7rGnIio901RBeHo6TPKWVVykPu1iYhQXw1jIABfw+MVsN
    +3bQ76WLdt2SDxsHs7q7zPyUyHXmps7ycZ5c72wGkUwNOjYelmkiNS0CgYEA9gY2
    w6I6S6L0juEKsbeDAwpd9WMfgqFoeA9vEyEUuk4kLwBKcoe1x4HG68ik918hdDSE
    9vDQSccA3xXHOAFOPJ8R9EeIAbTi1VwBYnbTp87X+xcPWlEPkrdoUKW60tgs1aNd
    /Nnc9LEVVPMS390zbFxt8TN/biaBgelNgbC95sMCgYEAo/8V14SezckO6CNLKs/b
    tPdFiO9/kC1DsuUTd2LAfIIVeMZ7jn1Gus/Ff7B7IVx3p5KuBGOVF8L+qifLb6nQ
    nLysgHDh132NDioZkhH7mI7hPG+PYE/odApKdnqECHWw0J+F0JWnUd6D2B/1TvF9
    mXA2Qx+iGYn8OVV1Bsmp6qUCgYEAw0kZbV63cVRvVX6yk3C8cMxo2qCM4Y8nsq1l
    mMSYhG4EcL6FWbX5h9yuvngs4iLEFk6eALoUS4vIWEwcL4txw9LsWH/zKI+hwoRe
    oP77cOdSL4AVcraHawlkpyd2TWjE5evgbhWtOxnZee3cXJBkAi64Ik6jZxbvk+RR
    3pEhnCsCgYBd9Pl1dGQ/4PlGika1bezRFWlnNnPxIHPWrnWRxBCKYr+lycWOUPk1
    clEAVQXzLHVIigANNKdVH6h4PfI/mgcrzkQnYCaBv68CjX2Rv9r42T6P2DALQfT+
    2vQxZSMnRNS2mCV8et5ZnWcjHV9kN1aEjVU/o8fDuia+fAaDbe190g==
    -----END RSA PRIVATE KEY-----
    >>> decryptor = decrypt_json_web_token(private_key = private_key_as_encoded_str)
    >>> decrypted_jwt = check(decryptor)(jwe)
    >>> decrypted_jwt
    'eyJhbGciOiJub25lIn0.Tm93IGlzIHRoZSB0aW1lIGZvciBhbGwgZ29vZCBtZW4gdG8gY29tZSB0byB0aGUgYWlkIG9mIHRoZWlyIGNvdW50cnku.'
    >>> decrypted_jwt == jwt
    True
    >>> decoded_jwt = check(decode_json_web_token)(decrypted_jwt)
    >>> decoded_jwt['payload']
    'Now is the time for all good men to come to the aid of their country.'
    >>> decoded_jwt['payload'] == plaintext
    True

    >>> # Same test with random keys.

    >>> encryptor = encrypt_json_web_token(algorithm = 'RSA1_5', integrity = 'HS256', method = 'A128CBC',
    ...     public_key_as_encoded_str = public_key_as_encoded_str)
    >>> jwe = check(encryptor)(jwt)
    >>> decryptor = decrypt_json_web_token(private_key = private_key_as_encoded_str)
    >>> decrypted_jwt = check(decryptor)(jwe)
    >>> decrypted_jwt
    'eyJhbGciOiJub25lIn0.Tm93IGlzIHRoZSB0aW1lIGZvciBhbGwgZ29vZCBtZW4gdG8gY29tZSB0byB0aGUgYWlkIG9mIHRoZWlyIGNvdW50cnku.'
    >>> decrypted_jwt == jwt
    True

    >>> # Mike Jones Test 2

    >>> plaintext_bytes_list = [76, 105, 118, 101, 32, 108, 111, 110, 103, 32, 97, 110, 100, 32, 112, 114,
    ...     111, 115, 112, 101, 114, 46]
    >>> plaintext = ''.join(chr(byte) for byte in plaintext_bytes_list)
    >>> jwt = check(make_payload_to_json_web_token())(plaintext)
    >>> cmk_bytes_list = [177, 161, 244, 128, 84, 143, 225, 115, 63, 180, 3, 255, 107, 154, 212, 246,
    ...     138, 7, 110, 91, 112, 46, 34, 105, 47, 130, 203, 46, 122, 234, 64, 252]
    >>> cmk = ''.join(chr(byte) for byte in cmk_bytes_list)
    >>> iv_bytes_list = [227, 197, 117, 252, 2, 219, 233, 68, 180, 225, 77, 219]
    >>> iv = ''.join(chr(byte) for byte in iv_bytes_list)
    >>> key_modulus_bytes_list = [161, 168, 84, 34, 133, 176, 208, 173, 46, 176, 163, 110, 57, 30, 135, 227,
    ...     9, 31, 226, 128, 84, 92, 116, 241, 70, 248, 27, 227, 193, 62, 5, 91,
    ...     241, 145, 224, 205, 141, 176, 184, 133, 239, 43, 81, 103, 9, 161, 153, 157,
    ...     179, 104, 123, 51, 189, 34, 152, 69, 97, 69, 78, 93, 140, 131, 87, 182,
    ...     169, 101, 92, 142, 3, 22, 167, 8, 212, 56, 35, 79, 210, 222, 192, 208,
    ...     252, 49, 109, 138, 173, 253, 210, 166, 201, 63, 102, 74, 5, 158, 41, 90,
    ...     144, 108, 160, 79, 10, 89, 222, 231, 172, 31, 227, 197, 0, 19, 72, 81,
    ...     138, 78, 136, 221, 121, 118, 196, 17, 146, 10, 244, 188, 72, 113, 55, 221,
    ...     162, 217, 171, 27, 57, 233, 210, 101, 236, 154, 199, 56, 138, 239, 101, 48,
    ...     198, 186, 202, 160, 76, 111, 234, 71, 57, 183, 5, 211, 171, 136, 126, 64,
    ...     40, 75, 58, 89, 244, 254, 107, 84, 103, 7, 236, 69, 163, 18, 180, 251,
    ...     58, 153, 46, 151, 174, 12, 103, 197, 181, 161, 162, 55, 250, 235, 123, 110,
    ...     17, 11, 158, 24, 47, 133, 8, 199, 235, 107, 126, 130, 246, 73, 195, 20,
    ...     108, 202, 176, 214, 187, 45, 146, 182, 118, 54, 32, 200, 61, 201, 71, 243,
    ...     1, 255, 131, 84, 37, 111, 211, 168, 228, 45, 192, 118, 27, 197, 235, 232,
    ...     36, 10, 230, 248, 190, 82, 182, 140, 35, 204, 108, 190, 253, 186, 186, 27]
    >>> key_modulus = ''.join(chr(byte) for byte in key_modulus_bytes_list)
    >>> key_public_exponent_bytes_list = [1, 0, 1]
    >>> key_public_exponent = ''.join(chr(byte) for byte in key_public_exponent_bytes_list)
    >>> public_key = RSA.construct((number.bytes_to_long(key_modulus),
    ...     number.bytes_to_long(key_public_exponent)))
    >>> public_key_as_encoded_str = public_key.exportKey()
    >>> encrypted_key_bytes_list = [142, 252, 40, 202, 21, 177, 56, 198, 232, 7, 151, 49, 95, 169, 220, 2,
    ...     46, 214, 167, 116, 57, 20, 164, 109, 150, 98, 49, 223, 154, 95, 71, 209,
    ...     233, 17, 174, 142, 203, 232, 132, 167, 17, 42, 51, 125, 22, 221, 135, 17,
    ...     67, 197, 148, 246, 139, 145, 160, 238, 99, 119, 171, 95, 117, 202, 87, 251,
    ...     101, 254, 58, 215, 135, 195, 135, 103, 49, 119, 76, 46, 49, 198, 27, 31,
    ...     58, 44, 192, 222, 21, 16, 13, 216, 161, 179, 236, 65, 143, 38, 43, 218,
    ...     195, 76, 140, 243, 71, 243, 79, 124, 216, 208, 242, 171, 34, 245, 57, 154,
    ...     93, 76, 230, 204, 234, 82, 117, 248, 39, 13, 62, 60, 215, 8, 51, 248,
    ...     254, 47, 150, 36, 46, 27, 247, 98, 77, 56, 92, 44, 19, 39, 12, 77,
    ...     54, 101, 194, 126, 86, 0, 64, 239, 95, 211, 64, 26, 219, 93, 211, 36,
    ...     154, 250, 117, 177, 213, 232, 142, 184, 216, 92, 20, 248, 69, 175, 180, 71,
    ...     205, 221, 235, 224, 95, 113, 5, 33, 86, 18, 157, 61, 199, 8, 121, 0,
    ...     0, 135, 65, 67, 220, 164, 15, 230, 155, 71, 53, 64, 253, 209, 169, 255,
    ...     34, 64, 101, 7, 43, 102, 227, 83, 171, 52, 225, 119, 253, 182, 96, 195,
    ...     225, 34, 156, 211, 202, 7, 194, 255, 137, 59, 170, 172, 72, 234, 222, 203,
    ...     123, 249, 121, 254, 143, 173, 105, 65, 187, 189, 163, 64, 151, 145, 99, 17]
    >>> encrypted_key = ''.join(chr(byte) for byte in encrypted_key_bytes_list)
    >>> encryptor = encrypt_json_web_token(algorithm = 'RSA-OAEP', content_master_key = cmk,
    ...     encrypted_key = encrypted_key, initialization_vector = iv, method = 'A256GCM',
    ...     public_key_as_encoded_str = public_key_as_encoded_str)
    >>> jwe = check(encryptor)(jwt)
    >>> jwe
    'eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJpdiI6IjQ4VjFfQUxiNlVTMDRVM2IifQ.jvwoyhWxOMboB5cxX6ncAi7Wp3Q5FKRtl\
mIx35pfR9HpEa6Oy-iEpxEqM30W3YcRQ8WU9ouRoO5jd6tfdcpX-2X-OteHw4dnMXdMLjHGGx86LMDeFRAN2KGz7EGPJivaw0yM80fzT3zY0PKrIvU5ml\
1M5szqUnX4Jw0-PNcIM_j-L5YkLhv3Yk04XCwTJwxNNmXCflYAQO9f00Aa213TJJr6dbHV6I642FwU-EWvtEfN3evgX3EFIVYSnT3HCHkAAIdBQ9ykD-a\
bRzVA_dGp_yJAZQcrZuNTqzThd_22YMPhIpzTygfC_4k7qqxI6t7Le_l5_o-taUG7vaNAl5FjEQ._e21tGGhac_peEFkLXr2dMPUZiUkrw.YbZSeHCNDZ\
BqAdzpROlyiw'

    >>> key_private_exponent_bytes_list = [144, 183, 109, 34, 62, 134, 108, 57, 44, 252, 10, 66, 73, 54, 16, 181,
    ...     233, 92, 54, 219, 101, 42, 35, 178, 63, 51, 43, 92, 119, 136, 251, 41,
    ...     53, 23, 191, 164, 164, 60, 88, 227, 229, 152, 228, 213, 149, 228, 169, 237,
    ...     104, 71, 151, 75, 88, 252, 216, 77, 251, 231, 28, 97, 88, 193, 215, 202,
    ...     248, 216, 121, 195, 211, 245, 250, 112, 71, 243, 61, 129, 95, 39, 244, 122,
    ...     225, 217, 169, 211, 165, 48, 253, 220, 59, 122, 219, 42, 86, 223, 32, 236,
    ...     39, 48, 103, 78, 122, 216, 187, 88, 176, 89, 24, 1, 42, 177, 24, 99,
    ...     142, 170, 1, 146, 43, 3, 108, 64, 194, 121, 182, 95, 187, 134, 71, 88,
    ...     96, 134, 74, 131, 167, 69, 106, 143, 121, 27, 72, 44, 245, 95, 39, 194,
    ...     179, 175, 203, 122, 16, 112, 183, 17, 200, 202, 31, 17, 138, 156, 184, 210,
    ...     157, 184, 154, 131, 128, 110, 12, 85, 195, 122, 241, 79, 251, 229, 183, 117,
    ...     21, 123, 133, 142, 220, 153, 9, 59, 57, 105, 81, 255, 138, 77, 82, 54,
    ...     62, 216, 38, 249, 208, 17, 197, 49, 45, 19, 232, 157, 251, 131, 137, 175,
    ...     72, 126, 43, 229, 69, 179, 117, 82, 157, 213, 83, 35, 57, 210, 197, 252,
    ...     171, 143, 194, 11, 47, 163, 6, 253, 75, 252, 96, 11, 187, 84, 130, 210,
    ...     7, 121, 78, 91, 79, 57, 251, 138, 132, 220, 60, 224, 173, 56, 224, 201]
    >>> key_private_exponent = ''.join(chr(byte) for byte in key_private_exponent_bytes_list)
    >>> private_key = RSA.construct((number.bytes_to_long(key_modulus),
    ...     number.bytes_to_long(key_public_exponent), number.bytes_to_long(key_private_exponent)))
    >>> private_key_as_encoded_str = private_key.exportKey()
    >>> decryptor = decrypt_json_web_token(private_key = private_key_as_encoded_str)
    >>> decrypted_jwt = check(decryptor)(jwe)
    >>> decrypted_jwt == jwt
    True
    >>> decoded_jwt = check(decode_json_web_token)(decrypted_jwt)
    >>> decoded_jwt['payload']
    'Live long and prosper.'
    >>> decoded_jwt['payload'] == plaintext
    True

    >>> # Mike Jones Test 3:  RSA-OAEP/AES-GSM

    >>> jwe = 'eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJpdiI6Il9fNzlfUHY2LWZqMzl2WDAifQ.LX4rQictZUJSYrVH3-TmCeH\
08qlpMrbFpKhEBVyAFX6h4V3Xt6omuTyMmkeiMIR6gbkn9ww4A0xDRnRu2GuM-v30Ri6OHx04fP1l1osYRngALuzMplcreyFCErm5asXTghweg_oI2y6f\
fhgR8P0ONWSlv0Bg-y58nAiNMi9Z51P42sx1f2JknAhG_oJ2u4Dy-6xY3tWCS4hXolMt5NMZm1dUN56RKvGlp-nspa9mYONfV-CITnjA3zMVWGdpTF4SX\
Nq0fK5gWM3CgxJEtuW1gk69q9k_zOAEqCph_urnx0T7_6ZaBa90nV3TvX0cC5bq75alEqGWkqJLwTMsEnAg-A.ykqmBHvu8Yhqf5jafmUKcgDY8kZ0vw.\
_3cYrFHM7X640lLd_QoUKw'
    >>> key_modulus_bytes_list = [152, 66, 27, 221, 242, 12, 205, 109, 3, 3, 73, 191, 7, 43, 214, 144,
    ...     254, 253, 173, 139, 211, 33, 139, 34, 95, 176, 106, 246, 5, 176, 94, 78,
    ...     150, 102, 87, 240, 113, 118, 40, 137, 1, 245, 201, 181, 133, 9, 175, 161,
    ...     119, 134, 19, 81, 38, 21, 100, 25, 214, 68, 37, 66, 189, 149, 75, 143,
    ...     148, 24, 249, 69, 38, 236, 119, 81, 118, 149, 244, 115, 242, 43, 3, 90,
    ...     107, 238, 42, 3, 9, 90, 173, 192, 72, 175, 165, 17, 77, 92, 175, 8,
    ...     22, 252, 201, 168, 30, 109, 167, 12, 23, 56, 114, 122, 217, 30, 241, 127,
    ...     233, 130, 119, 100, 190, 121, 77, 95, 106, 107, 109, 19, 5, 103, 110, 0,
    ...     208, 248, 166, 68, 213, 22, 203, 25, 50, 35, 207, 165, 188, 185, 62, 103,
    ...     164, 45, 172, 183, 49, 132, 72, 72, 159, 223, 180, 22, 157, 253, 197, 185,
    ...     77, 67, 236, 72, 99, 14, 155, 255, 100, 159, 208, 199, 50, 4, 232, 132,
    ...     147, 61, 84, 150, 56, 13, 109, 17, 6, 247, 76, 172, 122, 185, 142, 120,
    ...     207, 117, 90, 94, 96, 161, 216, 2, 221, 17, 89, 107, 229, 214, 154, 97,
    ...     2, 17, 14, 222, 116, 61, 249, 198, 194, 55, 187, 13, 243, 34, 151, 65,
    ...     197, 17, 145, 225, 124, 238, 155, 235, 84, 192, 107, 107, 118, 185, 67, 196,
    ...     4, 75, 15, 89, 140, 30, 169, 51, 94, 160, 20, 98, 153, 156, 216, 51]
    >>> key_modulus = ''.join(chr(byte) for byte in key_modulus_bytes_list)
    >>> key_public_exponent_bytes_list = [1, 0, 1]
    >>> key_public_exponent = ''.join(chr(byte) for byte in key_public_exponent_bytes_list)
    >>> key_private_exponent_bytes_list = [107, 210, 84, 253, 165, 77, 95, 164, 21, 0, 29, 23, 68, 50, 205, 45,
    ...     189, 5, 84, 2, 178, 175, 12, 98, 121, 52, 235, 105, 241, 185, 101, 239,
    ...     109, 30, 104, 164, 3, 21, 83, 187, 66, 66, 22, 103, 143, 32, 190, 217,
    ...     47, 85, 41, 20, 204, 77, 85, 167, 222, 78, 63, 188, 181, 152, 165, 251,
    ...     181, 58, 194, 59, 48, 71, 64, 111, 213, 244, 119, 58, 44, 130, 61, 75,
    ...     169, 38, 237, 101, 93, 24, 115, 246, 185, 2, 121, 120, 121, 58, 107, 80,
    ...     229, 70, 122, 95, 173, 188, 165, 17, 48, 216, 110, 105, 132, 156, 31, 21,
    ...     31, 253, 158, 35, 31, 167, 179, 29, 32, 181, 150, 118, 99, 219, 76, 207,
    ...     251, 137, 174, 83, 77, 177, 19, 244, 49, 154, 248, 255, 112, 107, 231, 233,
    ...     96, 24, 96, 218, 77, 28, 47, 208, 75, 221, 69, 210, 226, 175, 61, 65,
    ...     106, 13, 8, 127, 96, 188, 205, 210, 251, 101, 176, 46, 22, 245, 249, 13,
    ...     174, 22, 109, 117, 255, 141, 126, 39, 90, 231, 44, 51, 49, 54, 95, 99,
    ...     149, 61, 238, 4, 17, 48, 239, 76, 198, 16, 193, 252, 160, 213, 155, 98,
    ...     51, 21, 155, 203, 163, 238, 112, 23, 29, 231, 76, 141, 93, 115, 91, 83,
    ...     103, 66, 110, 227, 188, 231, 105, 78, 23, 172, 126, 196, 130, 181, 226, 214,
    ...     178, 46, 56, 1, 181, 180, 154, 182, 80, 186, 154, 158, 79, 15, 177, 65]
    >>> key_private_exponent = ''.join(chr(byte) for byte in key_private_exponent_bytes_list)
    >>> private_key = RSA.construct((number.bytes_to_long(key_modulus),
    ...     number.bytes_to_long(key_public_exponent), number.bytes_to_long(key_private_exponent)))
    >>> private_key_as_encoded_str = private_key.exportKey()
    >>> decryptor = decrypt_json_web_token(private_key = private_key_as_encoded_str)
    >>> decrypted_jwt = check(decryptor)(jwe)
    >>> decoded_jwt = check(decode_json_web_token)(decrypted_jwt)
    >>> decoded_jwt['payload']
    'What hath God wrought?'
    """
    if shared_secret is not None:
        assert isinstance(shared_secret, str)  # Shared secret must not be unicode.

    def decrypt_json_web_token_converter(token, state = None):
        if token is None:
            return None, None
        if state is None:
            state = states.default_state

        if token.count('.') != 3:
            if require_encrypted_token:
                return token, state._(u'Invalid crypted JSON web token')
            return token, None
        encoded_header, encoded_encrypted_key, encoded_cyphertext, encoded_integrity_value = token.split('.')

        header, error = pipe(
            make_base64url_to_bytes(add_padding = True),
            make_input_to_json(),
            test_isinstance(dict),
            struct(
                dict(
                    alg = pipe(
                        test_isinstance(basestring),
                        test_in(valid_encryption_algorithms),
                        not_none,
                        ),
                    cty = pipe(
                        test_isinstance(basestring),
                        test_in([
                            u'JWT',
                            # u'urn:ietf:params:oauth:token-type:jwt',
                            ]),
                        ),
                    enc = pipe(
                        test_isinstance(basestring),
                        test_in(valid_encryption_methods),
                        not_none,
                        ),
                    # epk = TODO to support ECDH-ES
                    int = pipe(
                        test_isinstance(basestring),
                        test_in(valid_integrity_algorithms),
                        ),
                    iv = pipe(
                        test_isinstance(basestring),
                        make_base64url_to_bytes(add_padding = True),
                        ),
                    jku = pipe(
                        test_isinstance(basestring),
                        make_input_to_url(add_prefix = None, error_if_fragment = True, full = True,
                            schemes = ['https']),
                        ),
                    jwk = pipe(
                        test_isinstance(basestring),
                        make_input_to_json(),
                        json_to_json_web_key,
                        ),
                    kdf = pipe(
                        test_isinstance(basestring),
                        test_in(valid_key_derivation_functions),
                        ),
                    kid = test_isinstance(basestring),
                    typ = pipe(
                        test_isinstance(basestring),
                        test_in([
                            u'JWE',
                            ]),
                        ),
                    x5c = pipe(
                        test_isinstance(list),
                        uniform_sequence(pipe(
                            test_isinstance(basestring),
                            base64_to_bytes,
                            # TODO
                            )),
                        ),
                    x5t = pipe(
                        test_isinstance(basestring),
                        make_base64url_to_bytes(add_padding = True),
                        # TODO
                        ),
                    x5u = pipe(
                        test_isinstance(basestring),
                        make_input_to_url(add_prefix = None, error_if_fragment = True, full = True,
                            schemes = ['https']),
                        ),
                    zip = pipe(
                        test_isinstance(basestring),
                        test_in([
                            u'DEF',
                            u'none',
                            ]),
                        ),
                    ),
                # default = None,  # For security reasons a header can only contain known attributes.
                ),
            not_none,
            )(encoded_header, state = state)
        if error is not None:
            return token, state._(u'Invalid header: {0}').format(error)
        encrypted_key, error = make_base64url_to_bytes(add_padding = True)(encoded_encrypted_key, state = state)
        if error is not None:
            return token, state._(u'Invalid encrypted key: {0}').format(error)
        cyphertext, error = make_base64url_to_bytes(add_padding = True)(encoded_cyphertext, state = state)
        if error is not None:
            return token, state._(u'Invalid cyphertext: {0}').format(error)
        integrity_value, error = make_base64url_to_bytes(add_padding = True)(encoded_integrity_value, state = state)
        if error is not None:
            return token, state._(u'Invalid integrity value: {0}').format(error)

        # TODO: Verify that the JWE Header references a key known to the recipient.

        algorithm = header['alg']
        if algorithm == u'RSA1_5':
            assert private_key is not None
            rsa_private_key = RSA.importKey(private_key)
            cipher = Cipher_PKCS1_v1_5.new(rsa_private_key)
            # Build a sentinel that has the same size of the plaintext (ie the content master key).
            sentinel = Random.get_random_bytes(256 >> 3)
            try:
                content_master_key = cipher.decrypt(encrypted_key, sentinel)
            except:
                return token, state._(u'Invalid content master key')
        elif algorithm == u'RSA-OAEP':
            assert private_key is not None
            rsa_private_key = RSA.importKey(private_key)
            cipher = Cipher_PKCS1_OAEP.new(rsa_private_key)
            try:
                content_master_key = cipher.decrypt(encrypted_key)
            except:
                return token, state._(u'Invalid content master key')

        method = header['enc']
        if method.endswith('GCM'):
            # Algorithm is an AEAD algorithm.
            if header['int'] is not None:
                return token, state._(
                    u'Unexpected "int" header forbidden by AEAD algorithm {0}').format(algorithm)
            content_encryption_key = content_master_key
        else:
            # Algorithm is not an AEAD algorithm.
            if header['int'] is None:
                return token, state._(
                    u'Missing "int" header, required by non AEAD algorithm {0}').format(algorithm)
            method_size = int(method[1:4])
            key_derivation_digest_size = int((header['kdf'] or u'CS256')[2:])
            content_encryption_key = derive_key(content_master_key, 'Encryption',
                digest_size = key_derivation_digest_size, key_size = method_size)
            integrity = header['int']
            integrity_size = int(integrity[2:])
            content_integrity_key = derive_key(content_master_key, 'Integrity',
                digest_size = key_derivation_digest_size, key_size = integrity_size)
            secured_input = token.rsplit('.', 1)[0]
            digest_constructor = digest_constructor_by_size[integrity_size]
            signature = HMAC.new(content_integrity_key, msg = secured_input, digestmod = digest_constructor).digest()
            encoded_signature = check(make_bytes_to_base64url(remove_padding = True))(signature, state = state)
            if encoded_integrity_value != encoded_signature:
                return token, state._(u'Non authentic signature')

        if method.startswith(u'A') and method.endswith(u'CBC'):
            if header['iv'] is None:
                return token, state._(
                    u'Invalid header: "iv" required for {0} encryption method').format(method)
            cipher = Cipher_AES.new(content_encryption_key, mode = Cipher_AES.MODE_CBC, IV = header['iv'])
            try:
                compressed_plaintext = cipher.decrypt(cyphertext)
            except:
                return token, state._(u'Invalid cyphertext')

            # Remove PKCS #5 padding.
            padding_number = ord(compressed_plaintext[-1])
            compressed_plaintext = compressed_plaintext[:-padding_number]
        elif method.startswith(u'A') and method.endswith(u'GCM'):
            if header['iv'] is None:
                return token, state._(
                    u'Invalid header: "iv" required for {0} encryption method').format(method)
            additional_authenticated_data = '{0}.{1}'.format(encoded_header, encoded_encrypted_key)
            try:
                compressed_plaintext = gcm.gcm_decrypt(content_encryption_key, header['iv'],
                    cyphertext, additional_authenticated_data, integrity_value)
            except:
                return token, state._(u'Invalid cyphertext')
        else:
            raise 'TODO'

        compression = header['zip']
        if compression == u'DEF':
            try:
                plaintext = zlib.decompress(compressed_plaintext)
            except zlib.error:
                return token, state._(u'Invalid compressed plaintext')
        else:
            assert compression in (None, u'none'), compression
            plaintext = compressed_plaintext

        if header['cty'] == u'JWT':
            # Token was a nested token and plaintext is also a token.
            return plaintext, None

        # Create a new (unencrypted and unsigned) token containing plaintext.
        header = dict(
            alg = u'none',
            )
        encoded_header = check(pipe(
            make_json_to_str(encoding = 'utf-8', ensure_ascii = False, separators = (',', ':'), sort_keys = True),
            make_bytes_to_base64url(remove_padding = True),
            ))(header)
        encoded_payload = check(make_bytes_to_base64url(remove_padding = True))(plaintext, state = state)
        return '{0}.{1}.'.format(encoded_header, encoded_payload), None
    return decrypt_json_web_token_converter


def derive_key(master_key, label, digest_size = None, key_size = None):
    """Concatenation Key Derivation Function

    This is a simplified version of the algorithm described in  section "5.8.1 Concatenation Key Derivation Function
    (Approved Alternative 1)" of "Recommendation for Pair-Wise Key Establishment Schemes Using Discrete Logarithm
    Cryptography" (NIST SP 800-56 A).
    http://csrc.nist.gov/publications/nistpubs/800-56A/SP800-56A_Revision1_Mar08-2007.pdf

    .. note:: ``key_size`` & ``digest_size`` are the length in bits (not bytes).

    >>> # Mike Jones Tests

    >>> cmk1_bytes_list = [4, 211, 31, 197, 84, 157, 252, 254, 11, 100, 157, 250, 63, 170, 106, 206,
    ...     107, 124, 212, 45, 111, 107, 9, 219, 200, 177, 0, 240, 143, 156, 44, 207]
    >>> cmk1 = ''.join(chr(byte) for byte in cmk1_bytes_list)
    >>> cek1 = derive_key(cmk1, 'Encryption', key_size = 256)
    >>> cek1_bytes_list = [ord(c) for c in cek1]
    >>> cek1_bytes_list
    [249, 255, 87, 218, 224, 223, 221, 53, 204, 121, 166, 130, 195, 184, 50, 69, \
11, 237, 202, 71, 10, 96, 59, 199, 140, 88, 126, 147, 146, 113, 222, 41]
    >>> cik1 = derive_key(cmk1, 'Integrity', key_size = 256)
    >>> cik1_bytes_list = [ord(c) for c in cik1]
    >>> cik1_bytes_list
    [218, 209, 130, 50, 169, 45, 70, 214, 29, 187, 123, 20, 3, 158, 111, 122, \
182, 94, 57, 133, 245, 76, 97, 44, 193, 80, 81, 246, 115, 177, 225, 159]

    >>> cmk2_bytes_list = [148, 116, 199, 126, 2, 117, 233, 76, 150, 149, 89, 193, 61, 34, 239, 226,
    ...     109, 71, 59, 160, 192, 140, 150, 235, 106, 204, 49, 176, 68, 119, 13, 34,
    ...     49, 19, 41, 69, 5, 20, 252, 145, 104, 129, 137, 138, 67, 23, 153, 83,
    ...     81, 234, 82, 247, 48, 211, 41, 130, 35, 124, 45, 156, 249, 7, 225, 168]
    >>> cmk2 = ''.join(chr(byte) for byte in cmk2_bytes_list)
    >>> cek2 = derive_key(cmk2, 'Encryption', key_size = 128)
    >>> cek2_bytes_list = [ord(c) for c in cek2]
    >>> cek2_bytes_list
    [137, 5, 92, 9, 17, 47, 17, 86, 253, 235, 34, 247, 121, 78, 11, 144]
    >>> cik2 = derive_key(cmk2, 'Integrity', key_size = 512)
    >>> cik2_bytes_list = [ord(c) for c in cik2]
    >>> cik2_bytes_list
    [11, 179, 132, 177, 171, 24, 126, 19, 113, 1, 200, 102, 100, 74, 88, 149, \
31, 41, 71, 57, 51, 179, 106, 242, 113, 211, 56, 56, 37, 198, 57, 17, \
149, 209, 221, 113, 40, 191, 95, 252, 142, 254, 141, 230, 39, 113, 139, 84, \
44, 156, 247, 47, 223, 101, 229, 180, 82, 231, 38, 96, 170, 119, 236, 81]
    """
    assert isinstance(master_key, str)
    assert isinstance(label, str)
    if digest_size is None:
        digest_size = 256
    digest_constructor = digest_constructor_by_size[digest_size]
    if key_size is None:
        key_size = 256
    hashes = []
    block_count, remaining_length = divmod(key_size >> 3, digest_size >> 3)
    for index in range(block_count):
        hash_object = digest_constructor.new(pack('>I', index + 1))
        hash_object.update(master_key)
        hash_object.update(label)
        hashes.append(hash_object.digest())
    if remaining_length != 0:
        # Generated key length is not a multiple of digest length.
        hash_object = digest_constructor.new(pack('>I', len(hashes) + 1))
        hash_object.update(master_key)
        hash_object.update(label)
        hashes.append(hash_object.digest()[:remaining_length])
    return ''.join(hashes)


def encrypt_json_web_token(algorithm = None, compression = None, content_master_key = None, encrypted_key = None,
        integrity = None, initialization_vector = None, json_web_key_url = None, key_derivation_function = None,
        key_id = None, method = None, public_key_as_encoded_str = None, public_key_as_json_web_key = None,
        shared_secret = None):
    """Return a converter that encrypts a JSON Web Token.

    .. note:: ``content_master_key``, ``encrypted_key`` & ``initialization_vector`` parameters should be kept to
       ``None``, except for testing.

    >>> # Mike Jones Test 1

    >>> from Crypto.PublicKey import RSA
    >>> from Crypto.Util import number

    >>> plaintext_bytes_list = [78, 111, 119, 32, 105, 115, 32, 116, 104, 101, 32, 116, 105, 109, 101, 32,
    ...    102, 111, 114, 32, 97, 108, 108, 32, 103, 111, 111, 100, 32, 109, 101, 110,
    ...    32, 116, 111, 32, 99, 111, 109, 101, 32, 116, 111, 32, 116, 104, 101, 32,
    ...    97, 105, 100, 32, 111, 102, 32, 116, 104, 101, 105, 114, 32, 99, 111, 117,
    ...    110, 116, 114, 121, 46]
    >>> plaintext = ''.join(chr(byte) for byte in plaintext_bytes_list)
    >>> jwt = check(make_payload_to_json_web_token())(plaintext)
    >>> jwt
    'eyJhbGciOiJub25lIn0.Tm93IGlzIHRoZSB0aW1lIGZvciBhbGwgZ29vZCBtZW4gdG8gY29tZSB0byB0aGUgYWlkIG9mIHRoZWlyIGNvdW50cnku.'
    >>> cmk_bytes_list = [4, 211, 31, 197, 84, 157, 252, 254, 11, 100, 157, 250, 63, 170, 106, 206,
    ...     107, 124, 212, 45, 111, 107, 9, 219, 200, 177, 0, 240, 143, 156, 44, 207]
    >>> cmk = ''.join(chr(byte) for byte in cmk_bytes_list)
    >>> iv_bytes_list = [3, 22, 60, 12, 43, 67, 104, 105, 108, 108, 105, 99, 111, 116, 104, 101]
    >>> iv = ''.join(chr(byte) for byte in iv_bytes_list)
    >>> key_modulus_bytes_list = [177, 119, 33, 13, 164, 30, 108, 121, 207, 136, 107, 242, 12, 224, 19, 226,
    ...    198, 134, 17, 71, 173, 75, 42, 61, 48, 162, 206, 161, 97, 108, 185, 234,
    ...    226, 219, 118, 206, 118, 5, 169, 224, 60, 181, 90, 85, 51, 123, 6, 224,
    ...    4, 122, 29, 230, 151, 12, 244, 127, 121, 25, 4, 85, 220, 144, 215, 110,
    ...    130, 17, 68, 228, 129, 138, 7, 130, 231, 40, 212, 214, 17, 179, 28, 124,
    ...    151, 178, 207, 20, 14, 154, 222, 113, 176, 24, 198, 73, 211, 113, 9, 33,
    ...    178, 80, 13, 25, 21, 25, 153, 212, 206, 67, 154, 147, 70, 194, 192, 183,
    ...    160, 83, 98, 236, 175, 85, 23, 97, 75, 199, 177, 73, 145, 50, 253, 206,
    ...    32, 179, 254, 236, 190, 82, 73, 67, 129, 253, 252, 220, 108, 136, 138, 11,
    ...    192, 1, 36, 239, 228, 55, 81, 113, 17, 25, 140, 63, 239, 146, 3, 172,
    ...    96, 60, 227, 233, 64, 255, 224, 173, 225, 228, 229, 92, 112, 72, 99, 97,
    ...    26, 87, 187, 123, 46, 50, 90, 202, 117, 73, 10, 153, 47, 224, 178, 163,
    ...    77, 48, 46, 154, 33, 148, 34, 228, 33, 172, 216, 89, 46, 225, 127, 68,
    ...    146, 234, 30, 147, 54, 146, 5, 133, 45, 78, 254, 85, 55, 75, 213, 86,
    ...    194, 218, 215, 163, 189, 194, 54, 6, 83, 36, 18, 153, 53, 7, 48, 89,
    ...    35, 66, 144, 7, 65, 154, 13, 97, 75, 55, 230, 132, 3, 13, 239, 71]
    >>> key_modulus = ''.join(chr(byte) for byte in key_modulus_bytes_list)
    >>> key_public_exponent_bytes_list = [1, 0, 1]
    >>> key_public_exponent = ''.join(chr(byte) for byte in key_public_exponent_bytes_list)
    >>> public_key = RSA.construct((number.bytes_to_long(key_modulus),
    ...     number.bytes_to_long(key_public_exponent)))
    >>> public_key_as_encoded_str = public_key.exportKey()
    >>> print public_key_as_encoded_str
    -----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsXchDaQebHnPiGvyDOAT
    4saGEUetSyo9MKLOoWFsueri23bOdgWp4Dy1WlUzewbgBHod5pcM9H95GQRV3JDX
    boIRROSBigeC5yjU1hGzHHyXss8UDprecbAYxknTcQkhslANGRUZmdTOQ5qTRsLA
    t6BTYuyvVRdhS8exSZEy/c4gs/7svlJJQ4H9/NxsiIoLwAEk7+Q3UXERGYw/75ID
    rGA84+lA/+Ct4eTlXHBIY2EaV7t7LjJaynVJCpkv4LKjTTAumiGUIuQhrNhZLuF/
    RJLqHpM2kgWFLU7+VTdL1VbC2tejvcI2BlMkEpk1BzBZI0KQB0GaDWFLN+aEAw3v
    RwIDAQAB
    -----END PUBLIC KEY-----
    >>> encrypted_key_bytes_list = [32, 242, 63, 207, 94, 246, 133, 37, 135, 48, 88, 4, 15, 193, 6, 244,
    ...     51, 58, 132, 133, 212, 255, 163, 90, 59, 80, 200, 152, 41, 244, 188, 215,
    ...     174, 160, 26, 188, 227, 180, 165, 234, 172, 63, 24, 116, 152, 28, 149, 16,
    ...     94, 213, 201, 171, 180, 191, 11, 21, 149, 172, 143, 54, 194, 58, 206, 201,
    ...     164, 28, 107, 155, 75, 101, 22, 92, 227, 144, 95, 40, 119, 170, 7, 36,
    ...     225, 40, 141, 186, 213, 7, 175, 16, 174, 122, 75, 32, 48, 193, 119, 202,
    ...     41, 152, 210, 190, 68, 57, 119, 4, 197, 74, 7, 242, 239, 170, 204, 73,
    ...     75, 213, 202, 113, 216, 18, 23, 66, 106, 208, 69, 244, 117, 147, 2, 37,
    ...     207, 199, 184, 96, 102, 44, 70, 212, 87, 143, 253, 0, 166, 59, 41, 115,
    ...     217, 80, 165, 87, 38, 5, 9, 184, 202, 68, 67, 176, 4, 87, 254, 166,
    ...     227, 88, 124, 238, 249, 75, 114, 205, 148, 149, 45, 78, 193, 134, 64, 189,
    ...     168, 76, 170, 76, 176, 72, 148, 77, 215, 159, 146, 55, 189, 213, 85, 253,
    ...     135, 200, 59, 247, 79, 37, 22, 200, 32, 110, 53, 123, 54, 39, 9, 178,
    ...     231, 238, 95, 25, 211, 143, 87, 220, 88, 138, 209, 13, 227, 72, 58, 102,
    ...     164, 136, 241, 14, 14, 45, 32, 77, 44, 244, 162, 239, 150, 248, 181, 138,
    ...     251, 116, 245, 205, 137, 78, 34, 34, 10, 6, 59, 4, 197, 2, 153, 251]
    >>> encrypted_key = ''.join(chr(byte) for byte in encrypted_key_bytes_list)
    >>> encryptor = encrypt_json_web_token(algorithm = 'RSA1_5', content_master_key = cmk,
    ...     encrypted_key = encrypted_key, initialization_vector = iv, integrity = 'HS256', method = 'A128CBC',
    ...     public_key_as_encoded_str = public_key_as_encoded_str)
    >>> check(encryptor)(jwt)
    'eyJhbGciOiJSU0ExXzUiLCJlbmMiOiJBMTI4Q0JDIiwiaW50IjoiSFMyNTYiLCJpdiI6IkF4WThEQ3REYUdsc2JHbGpiM1JvWlEifQ.IPI_z172h\
SWHMFgED8EG9DM6hIXU_6NaO1DImCn0vNeuoBq847Sl6qw_GHSYHJUQXtXJq7S_CxWVrI82wjrOyaQca5tLZRZc45BfKHeqByThKI261QevEK56SyAwwX\
fKKZjSvkQ5dwTFSgfy76rMSUvVynHYEhdCatBF9HWTAiXPx7hgZixG1FeP_QCmOylz2VClVyYFCbjKREOwBFf-puNYfO75S3LNlJUtTsGGQL2oTKpMsEi\
UTdefkje91VX9h8g7908lFsggbjV7NicJsufuXxnTj1fcWIrRDeNIOmakiPEODi0gTSz0ou-W-LWK-3T1zYlOIiIKBjsExQKZ-w._Z_djlIoC4MDSCKir\
eWS2beti4Q6iSG2UjFujQvdz-_PQdUcFNkOulegD6BgjgdFLjeB4HHOO7UHvP8PEDu0a0sA2a_-CI0w2YQQ2QQe35M.c41k4T4eAgCCt63m8ZNmiOinMc\
iFFypOFpvid7i6D0k'

    >>> # Mike Jones Test 2

    >>> plaintext_bytes_list = [76, 105, 118, 101, 32, 108, 111, 110, 103, 32, 97, 110, 100, 32, 112, 114,
    ...     111, 115, 112, 101, 114, 46]
    >>> plaintext = ''.join(chr(byte) for byte in plaintext_bytes_list)
    >>> jwt = check(make_payload_to_json_web_token())(plaintext)
    >>> cmk_bytes_list = [177, 161, 244, 128, 84, 143, 225, 115, 63, 180, 3, 255, 107, 154, 212, 246,
    ...     138, 7, 110, 91, 112, 46, 34, 105, 47, 130, 203, 46, 122, 234, 64, 252]
    >>> cmk = ''.join(chr(byte) for byte in cmk_bytes_list)
    >>> iv_bytes_list = [227, 197, 117, 252, 2, 219, 233, 68, 180, 225, 77, 219]
    >>> iv = ''.join(chr(byte) for byte in iv_bytes_list)
    >>> key_modulus_bytes_list = [161, 168, 84, 34, 133, 176, 208, 173, 46, 176, 163, 110, 57, 30, 135, 227,
    ...     9, 31, 226, 128, 84, 92, 116, 241, 70, 248, 27, 227, 193, 62, 5, 91,
    ...     241, 145, 224, 205, 141, 176, 184, 133, 239, 43, 81, 103, 9, 161, 153, 157,
    ...     179, 104, 123, 51, 189, 34, 152, 69, 97, 69, 78, 93, 140, 131, 87, 182,
    ...     169, 101, 92, 142, 3, 22, 167, 8, 212, 56, 35, 79, 210, 222, 192, 208,
    ...     252, 49, 109, 138, 173, 253, 210, 166, 201, 63, 102, 74, 5, 158, 41, 90,
    ...     144, 108, 160, 79, 10, 89, 222, 231, 172, 31, 227, 197, 0, 19, 72, 81,
    ...     138, 78, 136, 221, 121, 118, 196, 17, 146, 10, 244, 188, 72, 113, 55, 221,
    ...     162, 217, 171, 27, 57, 233, 210, 101, 236, 154, 199, 56, 138, 239, 101, 48,
    ...     198, 186, 202, 160, 76, 111, 234, 71, 57, 183, 5, 211, 171, 136, 126, 64,
    ...     40, 75, 58, 89, 244, 254, 107, 84, 103, 7, 236, 69, 163, 18, 180, 251,
    ...     58, 153, 46, 151, 174, 12, 103, 197, 181, 161, 162, 55, 250, 235, 123, 110,
    ...     17, 11, 158, 24, 47, 133, 8, 199, 235, 107, 126, 130, 246, 73, 195, 20,
    ...     108, 202, 176, 214, 187, 45, 146, 182, 118, 54, 32, 200, 61, 201, 71, 243,
    ...     1, 255, 131, 84, 37, 111, 211, 168, 228, 45, 192, 118, 27, 197, 235, 232,
    ...     36, 10, 230, 248, 190, 82, 182, 140, 35, 204, 108, 190, 253, 186, 186, 27]
    >>> key_modulus = ''.join(chr(byte) for byte in key_modulus_bytes_list)
    >>> key_public_exponent_bytes_list = [1, 0, 1]
    >>> key_public_exponent = ''.join(chr(byte) for byte in key_public_exponent_bytes_list)
    >>> public_key = RSA.construct((number.bytes_to_long(key_modulus),
    ...     number.bytes_to_long(key_public_exponent)))
    >>> public_key_as_encoded_str = public_key.exportKey()
    >>> encrypted_key_bytes_list = [142, 252, 40, 202, 21, 177, 56, 198, 232, 7, 151, 49, 95, 169, 220, 2,
    ...     46, 214, 167, 116, 57, 20, 164, 109, 150, 98, 49, 223, 154, 95, 71, 209,
    ...     233, 17, 174, 142, 203, 232, 132, 167, 17, 42, 51, 125, 22, 221, 135, 17,
    ...     67, 197, 148, 246, 139, 145, 160, 238, 99, 119, 171, 95, 117, 202, 87, 251,
    ...     101, 254, 58, 215, 135, 195, 135, 103, 49, 119, 76, 46, 49, 198, 27, 31,
    ...     58, 44, 192, 222, 21, 16, 13, 216, 161, 179, 236, 65, 143, 38, 43, 218,
    ...     195, 76, 140, 243, 71, 243, 79, 124, 216, 208, 242, 171, 34, 245, 57, 154,
    ...     93, 76, 230, 204, 234, 82, 117, 248, 39, 13, 62, 60, 215, 8, 51, 248,
    ...     254, 47, 150, 36, 46, 27, 247, 98, 77, 56, 92, 44, 19, 39, 12, 77,
    ...     54, 101, 194, 126, 86, 0, 64, 239, 95, 211, 64, 26, 219, 93, 211, 36,
    ...     154, 250, 117, 177, 213, 232, 142, 184, 216, 92, 20, 248, 69, 175, 180, 71,
    ...     205, 221, 235, 224, 95, 113, 5, 33, 86, 18, 157, 61, 199, 8, 121, 0,
    ...     0, 135, 65, 67, 220, 164, 15, 230, 155, 71, 53, 64, 253, 209, 169, 255,
    ...     34, 64, 101, 7, 43, 102, 227, 83, 171, 52, 225, 119, 253, 182, 96, 195,
    ...     225, 34, 156, 211, 202, 7, 194, 255, 137, 59, 170, 172, 72, 234, 222, 203,
    ...     123, 249, 121, 254, 143, 173, 105, 65, 187, 189, 163, 64, 151, 145, 99, 17]
    >>> encrypted_key = ''.join(chr(byte) for byte in encrypted_key_bytes_list)
    >>> encryptor = encrypt_json_web_token(algorithm = 'RSA-OAEP', content_master_key = cmk,
    ...     encrypted_key = encrypted_key, initialization_vector = iv, method = 'A256GCM',
    ...     public_key_as_encoded_str = public_key_as_encoded_str)
    >>> check(encryptor)(jwt)
    'eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJpdiI6IjQ4VjFfQUxiNlVTMDRVM2IifQ.jvwoyhWxOMboB5cxX6ncAi7Wp3Q5FKRtl\
mIx35pfR9HpEa6Oy-iEpxEqM30W3YcRQ8WU9ouRoO5jd6tfdcpX-2X-OteHw4dnMXdMLjHGGx86LMDeFRAN2KGz7EGPJivaw0yM80fzT3zY0PKrIvU5ml\
1M5szqUnX4Jw0-PNcIM_j-L5YkLhv3Yk04XCwTJwxNNmXCflYAQO9f00Aa213TJJr6dbHV6I642FwU-EWvtEfN3evgX3EFIVYSnT3HCHkAAIdBQ9ykD-a\
bRzVA_dGp_yJAZQcrZuNTqzThd_22YMPhIpzTygfC_4k7qqxI6t7Le_l5_o-taUG7vaNAl5FjEQ._e21tGGhac_peEFkLXr2dMPUZiUkrw.YbZSeHCNDZ\
BqAdzpROlyiw'
    """
    assert algorithm is None or algorithm in valid_encryption_algorithms, algorithm
    assert integrity is None or integrity in valid_integrity_algorithms, integrity
    assert key_derivation_function is None or key_derivation_function in valid_key_derivation_functions, \
        key_derivation_function
    assert method is None or method in valid_encryption_methods, method

    if algorithm is not None:
        assert method is not None
        method_size = int(method[1:4])
        encryption_key_length = method_size >> 3  # method_size is in bits, but length is in bytes.
        if method.endswith('GCM'):
            # AEAD encryption doesn't use a separate integrity algorithm
            integrity = None
            integrity_key_length = 0
        else:
            assert integrity is not None, 'Encryption algorithm requires a separate integrity algorithm'
            integrity_size = int(integrity[2:])
            integrity_key_length = integrity_size >> 3

        # The content master key must be at least as long as the encryption & integrity keys.
        # TODO: Don't create a content master key, when key agreement is employed.
        if content_master_key is None:
            content_master_key = Random.get_random_bytes(max(encryption_key_length, integrity_key_length))
        else:
            assert len(content_master_key) >= max(encryption_key_length, integrity_key_length)
        if encrypted_key is None:
            # Note: ``encrypted_key`` should be ``None`` except for testing.
            if algorithm.startswith(u'RSA'):
                if public_key_as_encoded_str is None:
                    assert public_key_as_json_web_key is not None
                    public_key_dict = public_key_as_json_web_key['jwk'][-1]  # TODO
                    assert public_key_dict['alg'] == u'RSA', public_key_as_json_web_key  # TODO
                    rsa_public_key = RSA.construct((
                        number.bytes_to_long(check(make_base64url_to_bytes(add_padding = True))(
                            public_key_dict['mod'])),
                        number.bytes_to_long(check(make_base64url_to_bytes(add_padding = True))(
                            public_key_dict['exp'])),
                        ))
                else:
                    rsa_public_key = RSA.importKey(public_key_as_encoded_str)
                if algorithm == u'RSA1_5':
                    cipher = Cipher_PKCS1_v1_5.new(rsa_public_key)
                else:
                    assert algorithm == u'RSA-OAEP', algorithm
                    cipher = Cipher_PKCS1_OAEP.new(rsa_public_key)
                encrypted_key = cipher.encrypt(content_master_key)
            else:
                raise 'TODO'
        encoded_encrypted_key = check(make_bytes_to_base64url(remove_padding = True))(encrypted_key)

        # Generate a random Initialization Vector (IV) (if required for the algorithm).
        if method in (u'A128CBC', u'A256CBC'):
            # All AES CBC ciphers use 128 bits (= 16 bytes) blocks
            if initialization_vector is None:
                initialization_vector = Random.get_random_bytes(16)
            else:
                assert len(initialization_vector) == 16
        elif method in (u'A128GCM', u'A256GCM'):
            # All AES GCM ciphers use 96 bits (= 12 bytes) blocks
            if initialization_vector is None:
                initialization_vector = Random.get_random_bytes(12)
            else:
                assert len(initialization_vector) == 12
        else:
            initialization_vector = None

        if method.endswith('GCM'):
            # Algorithm is an AEAD algorithm.
            content_encryption_key = content_master_key
            content_integrity_key = None
            assert key_derivation_function is None
        else:
            key_derivation_digest_size = int((key_derivation_function or u'CS256')[2:])
            content_encryption_key = derive_key(content_master_key, 'Encryption',
                digest_size = key_derivation_digest_size, key_size = method_size)
            content_integrity_key = derive_key(content_master_key, 'Integrity',
                digest_size = key_derivation_digest_size, key_size = integrity_size)

    def encrypt_json_web_token_converter(token, state = None):
        if token is None:
            return None, None
        if algorithm is None:
            return token, None
        if state is None:
            state = states.default_state

        if '.' not in token:
            return token, state._(u'Missing header')
        encoded_header, token_without_header = token.split('.', 1)
        header, error = pipe(
            make_base64url_to_bytes(add_padding = True),
            make_input_to_json(),
            )(encoded_header, state = state)
        if error is not None:
            return token, state._(u'Invalid header: {0}').format(error)

        if header['alg'] == u'none':
            if '.' not in token_without_header:
                return token, state._(u'Missing signature')
            encoded_payload, encoded_integrity_value = token_without_header.split('.', 1)
            if encoded_integrity_value:
                return token, state._(u'Unexpected signature in plaintext token')
            plaintext, error = make_base64url_to_bytes(add_padding = True)(encoded_payload, state = state)
            if error is not None:
                return token, state._(u'Invalid encoded payload: {0}').format(error)
        else:
            # Token is already signed. Use nested encryption.
            header = dict(
                cty = u'JWT',
                typ = u'JWE',  # optional
                )
            plaintext = token

        if compression == u'DEF':
            compressed_plaintext = zlib.compress(plaintext, 9)
        else:
            assert compression in (None, u'none'), compression
            compressed_plaintext = plaintext

        header['alg'] = algorithm
        header['enc'] = method
        if integrity is not None:
            header['int'] = integrity
        # TODO ephemeral_public_key
        # header['epk'] = ephemeral_public_key
        if initialization_vector is not None:
            header['iv'] = check(make_bytes_to_base64url(remove_padding = True))(initialization_vector, state = state)
        # TODO header['jku']
        # TODO header['jwk']
        # TODO header['kid']
        # TODO header['x5c']
        # TODO header['x5t']
        # TODO header['x5u']
        if compression not in (None, 'none'):
            header['zip'] = compression
        encoded_header = check(pipe(
            make_json_to_str(encoding = 'utf-8', ensure_ascii = False, separators = (',', ':'), sort_keys = True),
            make_bytes_to_base64url(remove_padding = True),
            ))(header, state = state)

        if method.startswith(u'A') and method.endswith(u'CBC'):
            # Add PKCS #5 padding.
            padding_number = 16 - len(compressed_plaintext) % 16
            compressed_plaintext += chr(padding_number) * padding_number

            cipher = Cipher_AES.new(content_encryption_key, mode = Cipher_AES.MODE_CBC, IV = initialization_vector)
            cyphertext = cipher.encrypt(compressed_plaintext)
            integrity_value = None
        elif method.startswith(u'A') and method.endswith(u'GCM'):
            additional_authenticated_data = '{0}.{1}'.format(encoded_header, encoded_encrypted_key)
            cyphertext, integrity_value = gcm.gcm_encrypt(content_encryption_key, initialization_vector,
                compressed_plaintext, additional_authenticated_data)
        else:
            raise 'TODO'
        encoded_cyphertext = check(make_bytes_to_base64url(remove_padding = True))(cyphertext, state = state)

        secured_input = '{0}.{1}.{2}'.format(encoded_header, encoded_encrypted_key, encoded_cyphertext)

        if integrity is None:
            assert integrity_value is not None
        else:
            assert integrity_value is None
            digest_constructor = digest_constructor_by_size[integrity_size]
            integrity_value = HMAC.new(content_integrity_key, msg = secured_input,
                digestmod = digest_constructor).digest()
        encoded_integrity_value = check(make_bytes_to_base64url(remove_padding = True))(integrity_value, state = state)

        token = '{0}.{1}'.format(secured_input, encoded_integrity_value)
        return token, None
    return encrypt_json_web_token_converter


input_to_json_web_token = cleanup_line


def make_json_to_json_web_token(typ = None):
    """Return a converter that wraps JSON data into an unsigned and unencrypted JSON web token."""
    return pipe(
        make_json_to_str(encoding = 'utf-8', ensure_ascii = False, separators = (',', ':'), sort_keys = True),
        make_payload_to_json_web_token(typ = typ),
        )


def make_payload_to_json_web_token(typ = None):
    """Return a converter that wraps binary data into an unsigned and unencrypted JSON web token."""
    header = dict(
        alg = u'none',
        )
    if typ is not None:
        header['typ'] = typ
    encoded_header = check(pipe(
        make_json_to_str(encoding = 'utf-8', ensure_ascii = False, separators = (',', ':'), sort_keys = True),
        make_bytes_to_base64url(remove_padding = True),
        ))(header)

    def payload_to_json_web_token(payload, state = None):
        if payload is None:
            return None, None
        if state is None:
            state = states.default_state

        encoded_payload, error = make_bytes_to_base64url(remove_padding = True)(payload, state = state)
        if error is not None:
            return encoded_payload, error
        secured_input = '{0}.{1}'.format(encoded_header, encoded_payload)
        encoded_signature = ''
        token = '{0}.{1}'.format(secured_input, encoded_signature)
        return token, None
    return payload_to_json_web_token


def sign_json_web_token(algorithm = None, json_web_key_url = None, key_id = None, private_key = None,
        shared_secret = None):
    if algorithm is None:
        algorithm = u'none'
    assert algorithm == u'none' or algorithm in valid_signature_algorithms
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
            rsa_private_key = RSA.importKey(private_key)
            signer = Signature_PKCS1_v1_5.new(rsa_private_key)

    def sign_json_web_token_converter(token, state = None):
        if token is None:
            return None, None
        if algorithm == u'none':
            return token, None
        if state is None:
            state = states.default_state
        if '.' not in token:
            return token, state._(u'Missing header')
        encoded_header, token_without_header = token.split('.', 1)
        header, error = pipe(
            make_base64url_to_bytes(add_padding = True),
            make_input_to_json(),
            )(encoded_header, state = state)
        if error is not None:
            return token, state._(u'Invalid header: {0}').format(error)
        if header['alg'] == u'none':
            if '.' not in token_without_header:
                return token, state._(u'Missing signature')
            encoded_payload, encoded_signature = token_without_header.split('.', 1)
            if encoded_signature:
                return token, state._(u'Unexpected signature in plaintext token')
        else:
            # Token is already signed or encrypted. Use nested signing.
            header = dict(
                cty = u'JWT',
                typ = u'JWS',  # optional
                )
            encoded_payload = check(make_bytes_to_base64url(remove_padding = True))(token, state = state)
        header['alg'] = algorithm
        if algorithm_prefix == u'RS':
            if json_web_key_url is not None:
                header['jku'] = json_web_key_url
            if key_id is not None:
                header['kid'] = key_id
        encoded_header = check(pipe(
            make_json_to_str(encoding = 'utf-8', ensure_ascii = False, separators = (',', ':'), sort_keys = True),
            make_bytes_to_base64url(remove_padding = True),
            ))(header)
        secured_input = '{0}.{1}'.format(encoded_header, encoded_payload)
#        if algorithm_prefix == u'ES':
#            TODO
#        elif algorithm_prefix == u'HS':
        if algorithm_prefix == u'HS':
            signature = HMAC.new(shared_secret, msg = secured_input, digestmod = digest_constructor).digest()
        else:
            assert algorithm_prefix == u'RS'
            digest = digest_constructor.new(secured_input)
            signature = signer.sign(digest)
        encoded_signature = check(make_bytes_to_base64url(remove_padding = True))(signature, state = state)
        token = '{0}.{1}'.format(secured_input, encoded_signature)
        return token, None
    return sign_json_web_token_converter


def verify_decoded_json_web_token_signature(allowed_algorithms = None, public_key_as_encoded_str = None,
        public_key_as_json_web_key = None, shared_secret = None):
    if shared_secret is not None:
        assert isinstance(shared_secret, str)  # Shared secret must not be unicode.

    def verify_decoded_json_web_token_signature_converter(value, state = None):
        if value is None:
            return None, None
        if state is None:
            state = states.default_state

        errors = {}
        algorithm = value['header'].get('alg')
        if allowed_algorithms is not None and algorithm not in allowed_algorithms:
            errors['header'] = dict(alg = state._(
                u'Unauthorized digital signature algorithm'))
        elif algorithm in valid_signature_algorithms:
            algorithm_prefix = algorithm[:2]
            algorithm_size = int(algorithm[2:])
            digest_constructor = digest_constructor_by_size[algorithm_size]
#            if algorithm_prefix == u'ES':
#                TODO
#            elif algorithm_prefix == u'HS':
            if algorithm_prefix == u'HS':
                if shared_secret is None:
                    errors['signature'] = state._(
                        u'Unable to check signature: Missing shared secret')
                else:
                    verified = HMAC.new(shared_secret, msg = value['secured_input'],
                        digestmod = digest_constructor).digest() == value['signature']
            else:
                assert algorithm_prefix == u'RS'
                if public_key_as_encoded_str is None:
                    assert public_key_as_json_web_key is not None
                    public_key_dict = public_key_as_json_web_key['jwk'][-1]  # TODO
                    assert public_key_dict['alg'] == u'RSA', public_key_as_json_web_key  # TODO
                    rsa_public_key = RSA.construct((
                        number.bytes_to_long(check(make_base64url_to_bytes(add_padding = True))(
                            public_key_dict['mod'], state = state)),
                        number.bytes_to_long(check(make_base64url_to_bytes(add_padding = True))(
                            public_key_dict['exp'], state = state)),
                        ))
                else:
                    rsa_public_key = RSA.importKey(public_key_as_encoded_str)
                verifier = Signature_PKCS1_v1_5.new(rsa_public_key)
                try:
                    digest = digest_constructor.new(value['secured_input'])
                    verified = verifier.verify(digest, value['signature'])
                except:
                    errors['signature'] = state._(u'Invalid signature')
            if 'signature' not in errors and not verified:
                errors['signature'] = state._(u'Non authentic signature')
        elif algorithm != u'none':
            errors['header'] = dict(alg = state._(
                u'Unimplemented digital signature algorithm'))
        return value, errors or None
    return verify_decoded_json_web_token_signature_converter


def verify_decoded_json_web_token_time():
    now_timestamp = calendar.timegm(datetime.datetime.utcnow().timetuple())
    return struct(
        dict(
            claims = struct(
                dict(
                    exp = test(
                        lambda timestamp: now_timestamp - 300 < timestamp,  # Allow 5 minutes drift.
                        error = N_(u'Expired JSON web token'),
                        ),
                    iat = test_less_or_equal(now_timestamp + 300,  # Allow 5 minutes drift.
                        error = N_(u'JSON web token issued in the future'),
                        ),
                    nbf = test(
                        lambda timestamp: now_timestamp + 300 >= timestamp,  # Allow 5 minutes drift.
                        error = N_(u'JSON web token not yet valid'),
                        ),
                    ),
                default = noop,
                ),
            ),
        default = noop,
        )
