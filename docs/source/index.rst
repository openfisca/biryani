.. Biryani documentation master file, created by sphinx-quickstart on Tue Jul  5 16:44:13 2011.
   You can adapt this file completely to your liking, but it should at least contain the root `toctree` directive.

   * To build HTML doc: ``./setup.py build_sphinx``.
   * To test doctests: ``./setup.py build_sphinx -b doctest``.
   * To see API documentation coverage: ``./setup.py build_sphinx -b coverage``.


Biryani - A Python conversion and validation toolbox
====================================================

*Biryani* is a Python library to convert and validate data (for web forms, CSV files, XML files, etc).

*Biryani* seeks to provide the same functionality as `FormEncode <http://formencode.org/>`_, while being more easy to use and extend.

To convert a value into another, you first create the ad-hoc converter by chaining conversion functions. Each conversion function takes a value as input and outputs a couple containing the converted value and an optional error message.


Usage Example
=============

A sample validator for a web form containing the following fields:

* Username
* Password (2 times)
* Email
* Tags (several fields with the same name, each one may contain several tags separated by a comma)

This example uses `WebOb <http://webob.org/>`_.

>>> import webob
>>> from biryani import allconv as conv
>>> validate_form = conv.mapping(dict(
...     username = conv.pipe(conv.multidict_get('username'), conv.cleanup_line, conv.require),
...     password = conv.pipe(
...         conv.multidict_getall('password'),
...         conv.test(lambda passwords: len(passwords) == 2 and passwords[0] == passwords[1],
...             error = u'Password mismatch'),
...         conv.function(lambda passwords: passwords[0]),
...         ),
...     email = conv.pipe(conv.multidict_get('email'), conv.str_to_email),
...     tags = conv.pipe(
...         conv.multidict_getall('tag'),
...         conv.function(lambda tags: u','.join(tags).split(u',')),
...         conv.uniform_sequence(conv.str_to_slug, constructor = set),
...         conv.function(sorted),
...         ),
...     ))

>>> req = webob.Request.blank('/?username=   John Doe&password=secret&password=secret&email=john@doe.name&tag=friend&tag=user,ADMIN')
>>> result, errors = validate_form(req.GET)
>>> result
{'username': u'John Doe', 'password': u'secret', 'email': u'john@doe.name', 'tags': [u'admin', u'friend', u'user']}

>>> req = webob.Request.blank('/?password=secret&password=other secret&email=john@doe.name&tag=friend&tag=user,ADMIN')
>>> result, errors = validate_form(req.GET)
>>> result
{'password': [u'secret', u'other secret'], 'email': u'john@doe.name', 'tags': [u'admin', u'friend', u'user']}
>>> errors
{'username': u'Missing value', 'password': u'Password mismatch'}

>>> req = webob.Request.blank('/?username=John Doe&password=secret&email=john.doe.name')
>>> result, errors = validate_form(req.GET)
>>> result
{'username': u'John Doe', 'password': [u'secret'], 'email': u'john.doe.name'}
>>> errors
{'password': u'Password mismatch', 'email': u'An email must contain exactly one "@"'}

See :doc:`tutorial1-web-form` for a complete explanation of this example.


Documentation
=============

.. toctree::
   :maxdepth: 2

   tutorial1-web-form
   tutorial2
   how-to-use
   api
   sugar

.. TODO

   Philosophy
   Comparison with FormEncode
   Howto use with WebOb
   How to use with lxml
   How to import a CSV file


Copyright and license
=====================

Biryani is a free software.

* Author: Emmanuel Raviart <eraviart@easter-eggs.com>
* Copyright (C) 2009, 2010, 2011 Easter-eggs

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Get Biryani
===========

Biryani is available as an easy-installable package on the `Python Package Index <http://pypi.python.org/pypi/Biryani>`_.

The code can be found in a Git repository, at http://gitorious.org/biryani.

