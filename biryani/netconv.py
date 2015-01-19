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


"""Network Related Converters

.. note:: Network converters are not in :mod:`biryani.baseconv`, because they use non-standard network libraries.
"""


import socket
import urllib2

import DNS  # from pyDNS
DNS.DiscoverNameServers()

from . import states


__all__ = [
    'test_email',
    'test_http_url',
    ]


def test_email():
    """Try to ensure than a (already validated) email address really exists.

    .. warning:: Like most converters, a ``None`` value is not tested.

    >>> test_email()(u'info@easter-eggs.com')
    (u'info@easter-eggs.com', None)
    >>> test_email()(u'unknown-user@unknown-server.easter-eggs.com')
    (u'unknown-user@unknown-server.easter-eggs.com', u'Domain "unknown-server.easter-eggs.com" doesn\\'t exist')
    >>> test_email()(u'unknown-user@easter-eggs.com')
    (u'unknown-user@easter-eggs.com', None)
    >>> test_email()(u'')
    Traceback (most recent call last):
    ValueError:
    >>> pipe(
    ...     input_to_email,
    ...     test_email(),
    ...     )(u'')
    (None, None)
    >>> test_email()(None)
    (None, None)
    """
    def test_email_converter(value, state = None):
        if value is None:
            return value, None
        if state is None:
            state = states.default_state
        username, domain = value.split('@', 1)
        try:
            # For an email domain to be considered valid, either A or MX request should work (both are not needed).
            answers = DNS.DnsRequest(domain, qtype= 'a', timeout = 10).req().answers
            if not answers:
                answers = DNS.DnsRequest(domain, qtype = 'mx', timeout = 10).req().answers
        except (socket.error, DNS.DNSError), e:
            return value, state._(
                u'An error occured when trying to connect to the email server: {0}').format(e)
        if not answers:
            return value, state._(u'''Domain "{0}" doesn't exist''').format(domain)
        return value, None
    return test_email_converter


def test_http_url(valid_status_codes = None):
    """Return a converters that tries to ensure than a (already validated) URL really works.

    .. warning:: Like most converters, a ``None`` value is not tested.

    >>> test_http_url()(u'http://www.easter-eggs.com/')
    (u'http://www.easter-eggs.com/', None)
    >>> test_http_url()(u'http://www.comarquage.fr/unkown-page.html')
    (u'http://www.comarquage.fr/unkown-page.html', u'The web server responded with a bad status code: 404 Not Found')
    >>> test_http_url(valid_status_codes = [404])(u'http://www.comarquage.fr/unkown-page.html')
    (u'http://www.comarquage.fr/unkown-page.html', None)
    >>> test_http_url()(u'http://unknown-server.easter-eggs.com/')
    (u'http://unknown-server.easter-eggs.com/', \
u'An error occured when trying to connect to the web server: <urlopen error [Errno -2] Name or service not known>')
    >>> test_http_url()(u'')
    Traceback (most recent call last):
    ValueError:
    >>> pipe(
    ...     make_input_to_url(),
    ...     test_http_url(),
    ...     )(u'')
    (None, None)
    >>> test_http_url()(None)
    (None, None)
    """
    def test_http_url_converter(value, state = None):
        if value is None:
            return value, None
        if state is None:
            state = states.default_state
        request = urllib2.Request(value)
        request.add_header('User-Agent', 'Mozilla/5.0')
        try:
            response = urllib2.urlopen(request).read()
        except urllib2.HTTPError, response:
            if 200 <= response.code < 400:
                return value, state._(
                    u'An error occured when trying to connect to the web server: {0:d} {1}').format(
                    response.code, response.msg)
            if response.code not in (valid_status_codes or []):
                return value, state._(
                    u'The web server responded with a bad status code: {0:d} {1}').format(response.code, response.msg)
        except urllib2.URLError, e:
            return value, state._(
                u'An error occured when trying to connect to the web server: {0}').format(e)
        return value, None
    return test_http_url_converter
