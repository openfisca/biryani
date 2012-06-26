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

from . import states
from .base64conv import base64_to_bytes, make_base64url_to_bytes, make_bytes_to_base64url
from .baseconv import (check, cleanup_line, get, make_input_to_url, N_, noop, not_none, pipe, struct, test,
    test_greater_or_equal, test_in, test_isinstance, test_less_or_equal, uniform_sequence)
from .jsonconv import make_json_to_str, make_input_to_json
from .jwkconv import json_to_json_web_key


__all__ = [
    'decode_json_web_token',
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
#    u'ECDH-ES',
    u'RSA1_5',
    u'RSA-OAEP',
    )
valid_encryption_methods = (
    u'A128CBC',
    u'A256CBC',
#    u'A128GCM',
#    u'A256GCM',
    )
valid_integrity_algorithms = (
    u'HS256',
    u'HS384',
    u'HS512',
    )
valid_signature_algorithms = (
#    u'ES256',
    u'HS256',
    u'HS384',
    u'HS512',
    u'RS256',
    u'RS384',
    u'RS512',
    )


def decode_json_web_token(token, state = None):
    if token is None:
        return None, None
    if state is None:
        state = states.default_state

    errors = {}
    value = dict(token = token)
    try:
        value['secured_input'], value['encoded_signature'] = str(token).rsplit('.', 1)
        value['encoded_header'], value['encoded_payload'] = value['secured_input'].split('.', 1)
    except:
        return value, dict(token = state._(u'Invalid format'))

    errors = {}
    header, error = pipe(
        make_base64url_to_bytes(add_padding = True),
        make_input_to_json(),
        )(value['encoded_header'], state = state)
    if error is None:
        value['header'] = header
    else:
        errors['encoded_header'] = state._(u'Invalid format')
    claims, error = pipe(
        make_base64url_to_bytes(add_padding = True),
        make_input_to_json(),
        not_none,
        )(value['encoded_payload'], state = state)
    if error is not None:
        claims = None
        errors['encoded_payload'] = state._(u'Invalid format')
    signature, error = make_base64url_to_bytes(add_padding = True)(value['encoded_signature'], state = state)
    if error is None:
        value['signature'] = signature
    else:
        errors['encoded_signature'] = state._(u'Invalid format')
    if value['header'].get('typ', u'JWT') not in (u'application/jwt', u'JWT'):
        return value, dict(header = dict(typ = state._(u'Not a signed JSON Web Token (JWS)')))
    if claims is not None:
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
                keep_empty = True,
                ),
            )(claims, state = state)
        if claims_errors is not None:
            errors['claims'] = claims_errors
    return value, errors or None


decoded_json_web_token_to_json = get('claims')


def decrypt_json_web_token(private_key = None, require_encrypted_token = False, shared_secret = None):
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
                        make_input_to_url(add_prefix = None, error_if_fragment = True, full = True, schemes = ['https']),
                        ),
                    jwk = pipe(
                        test_isinstance(basestring),
                        make_input_to_json(),
                        json_to_json_web_key,
                        ),
                    kid = test_isinstance(basestring),
                    typ = pipe(
                        test_isinstance(basestring),
                        test_in([
                            u'application/jwe',
                            u'application/jwt',
                            u'JWE',
                            u'JWT',
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
                        make_input_to_url(add_prefix = None, error_if_fragment = True, full = True, schemes = ['https']),
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
                keep_none_values = True,
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
            rsa_private_key = RSA.importKey(private_key)
            cipher = Cipher_PKCS1_v1_5.new(rsa_private_key)
            # Build a sentinel that has the same size of the plaintext (ie the content master key).
            sentinel = Random.get_random_bytes(256 >> 3)
            try:
                content_master_key = cipher.decrypt(encrypted_key, sentinel)
            except:
                return token, state._(u'Invalid content master key')
        elif algorithm == u'RSA-OAEP':
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
            encoded_signature = ''
        else:
            if header['int'] is None:
                return token, state._(
                    u'Missing "int" header, required by non AEAD algorithm {0}').format(algorithm)
            method_size = int(method[1:4])
            encryption_key_length = method_size >> 3  # method_size is in bits, but length is in bytes.
            content_encryption_key = derive_key(content_master_key, 'Encryption', encryption_key_length)
            integrity = header['int']
            integrity_size = int(integrity[2:])
            integrity_key_length = integrity_size >> 3
            content_integrity_key = derive_key(content_master_key, 'Integrity', integrity_key_length)
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
        else:
            TODO
        try:
            compressed_plaintext = cipher.decrypt(cyphertext)
        except:
            return token, state._(u'Invalid cyphertext')
        # Remove PKCS #5 padding.
        padding_number = ord(compressed_plaintext[-1])
        compressed_plaintext = compressed_plaintext[:-padding_number]

        compression = header['zip']
        if compression == u'DEF':
            try:
                plaintext = zlib.decompress(compressed_plaintext)
            except zlib.error:
                return token, state._(u'Invalid compressed plaintext')
        else:
            assert compression in (None, u'none'), compression
            plaintext = compressed_plaintext

        if header['typ'] in (u'application/jwe', u'JWE'):
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
        encoded_payload, error = check(make_bytes_to_base64url(remove_padding = True))(plaintext, state = state)
        return '{0}.{1}.'.format(encoded_header, encoded_payload), None
    return decrypt_json_web_token_converter


def derive_key(master_key, label, key_length):
    """Concatenation Key Derivation Function

    This is a simplified version of the algorithm described in  section "5.8.1 Concatenation Key Derivation Function
    (Approved Alternative 1)" of "Recommendation for Pair-Wise Key Establishment Schemes Using Discrete Logarithm
    Cryptography" (NIST SP 800-56 A).
    http://csrc.nist.gov/publications/nistpubs/800-56A/SP800-56A_Revision1_Mar08-2007.pdf

    .. note:: ``key_length`` is the length in bytes (not bits).

    >>> cmk1_bytes_list = [4, 211, 31, 197, 84, 157, 252, 254, 11, 100, 157, 250, 63, 170, 106, 206,
    ...     107, 124, 212, 45, 111, 107, 9, 219, 200, 177, 0, 240, 143, 156, 44, 207]
    >>> cmk1 = ''.join(chr(byte) for byte in cmk1_bytes_list)
    >>> cek1 = derive_key(cmk1, 'Encryption', 32)
    >>> cek1_bytes_list = [ord(c) for c in cek1]
    >>> cek1_bytes_list
    [249, 255, 87, 218, 224, 223, 221, 53, 204, 121, 166, 130, 195, 184, 50, 69, \
11, 237, 202, 71, 10, 96, 59, 199, 140, 88, 126, 147, 146, 113, 222, 41]
    >>> cik1 = derive_key(cmk1, 'Integrity', 32)
    >>> cik1_bytes_list = [ord(c) for c in cik1]
    >>> cik1_bytes_list
    [218, 209, 130, 50, 169, 45, 70, 214, 29, 187, 123, 20, 3, 158, 111, 122, \
182, 94, 57, 133, 245, 76, 97, 44, 193, 80, 81, 246, 115, 177, 225, 159]

    >>> cmk2_bytes_list = [148, 116, 199, 126, 2, 117, 233, 76, 150, 149, 89, 193, 61, 34, 239, 226,
    ...     109, 71, 59, 160, 192, 140, 150, 235, 106, 204, 49, 176, 68, 119, 13, 34,
    ...     49, 19, 41, 69, 5, 20, 252, 145, 104, 129, 137, 138, 67, 23, 153, 83,
    ...     81, 234, 82, 247, 48, 211, 41, 130, 35, 124, 45, 156, 249, 7, 225, 168]
    >>> cmk2 = ''.join(chr(byte) for byte in cmk2_bytes_list)
    >>> cek2 = derive_key(cmk2, 'Encryption', 16)
    >>> cek2_bytes_list = [ord(c) for c in cek2]
    >>> cek2_bytes_list
    [137, 5, 92, 9, 17, 47, 17, 86, 253, 235, 34, 247, 121, 78, 11, 144]
    >>> cik2 = derive_key(cmk2, 'Integrity', 64)
    >>> cik2_bytes_list = [ord(c) for c in cik2]
    >>> cik2_bytes_list
    [11, 179, 132, 177, 171, 24, 126, 19, 113, 1, 200, 102, 100, 74, 88, 149, \
31, 41, 71, 57, 51, 179, 106, 242, 113, 211, 56, 56, 37, 198, 57, 17, \
149, 209, 221, 113, 40, 191, 95, 252, 142, 254, 141, 230, 39, 113, 139, 84, \
44, 156, 247, 47, 223, 101, 229, 180, 82, 231, 38, 96, 170, 119, 236, 81]
    """
    assert isinstance(master_key, str)
    assert isinstance(label, str)
    hashes = []
    for index in range(key_length >> 5):  # SHA256 hash has a length of 32 bytes == 2**5.
        hash_object = SHA256.new(pack('>I', index + 1))
        hash_object.update(master_key)
        hash_object.update(label)
        hashes.append(hash_object.digest())
    remaining_length = key_length & 0x1F
    if remaining_length != 0:
        # Generated key length is not a multiple of 256 bits (= 32 bytes).
        hash_object = SHA256.new(pack('>I', len(hashes) + 1))
        hash_object.update(master_key)
        hash_object.update(label)
        hashes.append(hash_object.digest()[:remaining_length])
    return ''.join(hashes)


def encrypt_json_web_token(algorithm = None, compression = None, integrity = None, json_web_key_url = None,
        key_id = None, method = None, public_key_as_encoded_str = None, public_key_as_json_web_key = None,
        shared_secret = None):
    assert algorithm is None or algorithm in valid_encryption_algorithms, algorithm
    assert integrity is None or integrity in valid_integrity_algorithms, integrity
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
        content_master_key = Random.get_random_bytes(max(encryption_key_length, integrity_key_length))
        if algorithm.startswith(u'RSA'):
            if public_key_as_encoded_str is None:
                assert public_key_as_json_web_key is not None
                public_key_dict = public_key_as_json_web_key['jwk'][-1]  # TODO
                assert public_key_dict['alg'] == u'RSA', public_key_as_json_web_key  # TODO
                rsa_public_key = RSA.construct((
                    number.bytes_to_long(check(make_base64url_to_bytes(add_padding = True))(public_key_dict['mod'])),
                    number.bytes_to_long(check(make_base64url_to_bytes(add_padding = True))(public_key_dict['exp'])),
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
            TODO
        encoded_encrypted_key = check(make_bytes_to_base64url(remove_padding = True))(encrypted_key)

        # Generate a random Initialization Vector (IV) (if required for the algorithm).
        if method in (u'A128CBC', u'A256CBC'):
            # All AES ciphers use 128 bits (= 16 bytes) blocks
            initialization_vector = Random.get_random_bytes(16)
        else:
            initialization_vector = None

        if method.endswith('GCM'):
            # Algorithm is an AEAD algorithm.
            content_encryption_key = content_master_key
            content_integrity_key = None
        else:
            content_encryption_key = derive_key(content_master_key, 'Encryption', encryption_key_length)
            content_integrity_key = derive_key(content_master_key, 'Integrity', integrity_key_length)

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
            encoded_payload, encoded_signature = token_without_header.split('.', 1)
            if encoded_signature:
                return token, state._(u'Unexpected signature in plaintext token')
            plaintext, error = make_base64url_to_bytes(add_padding = True)(encoded_payload, state = state)
            if error is not None:
                return token, state._(u'Invalid encoded payload: {0}').format(error)
        else:
            # Token is already signed or encrypted. Use nested signing.
            header = dict(
                typ = u'JWE',
                )
            plaintext = token

        if compression == u'DEF':
            compressed_plaintext = zlib.compress(plaintext, level = 9)
        else:
            assert compression in (None, u'none'), compression
            compressed_plaintext = plaintext

        if method.startswith(u'A') and method.endswith(u'CBC'):
            cipher = Cipher_AES.new(content_encryption_key, mode = Cipher_AES.MODE_CBC, IV = initialization_vector)
        else:
            TODO
        # Add PKCS #5 padding.
        padding_number = 16 - len(compressed_plaintext) % 16
        compressed_plaintext += chr(padding_number) * padding_number
        cyphertext = cipher.encrypt(compressed_plaintext)
        encoded_cyphertext = check(make_bytes_to_base64url(remove_padding = True))(cyphertext, state = state)

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

        secured_input = '{0}.{1}.{2}'.format(encoded_header, encoded_encrypted_key, encoded_cyphertext)

        if integrity is None:
            encoded_signature = ''
        else:
            digest_constructor = digest_constructor_by_size[integrity_size]
            signature = HMAC.new(content_integrity_key, msg = secured_input, digestmod = digest_constructor).digest()
            encoded_signature = check(make_bytes_to_base64url(remove_padding = True))(signature, state = state)

        token = '{0}.{1}'.format(secured_input, encoded_signature)
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
                typ = u'JWS',
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
                    exp = test(lambda timestamp: now_timestamp - 300 < timestamp,  # Allow 5 minutes drift.
                        error = N_(u'Expired JSON web token'),
                        ),
                    iat = test_less_or_equal(now_timestamp + 300,  # Allow 5 minutes drift.
                        error = N_(u'JSON web token issued in the future'),
                        ),
                    nbf = test(lambda timestamp: now_timestamp + 300 >= timestamp,  # Allow 5 minutes drift.
                        error = N_(u'JSON web token not yet valid'),
                        ),
                    ),
                default = noop,
                ),
            ),
        default = noop,
        )
