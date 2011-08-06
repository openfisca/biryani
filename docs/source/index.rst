.. Biryani documentation master file, created by sphinx-quickstart on Tue Jul  5 16:44:13 2011.
   You can adapt this file completely to your liking, but it should at least contain the root `toctree` directive.

   * To build HTML doc: ``./setup.py build_sphinx``.
   * To test doctests: ``./setup.py build_sphinx -b doctest``.
   * To see API documentation coverage: ``./setup.py build_sphinx -b coverage``.


Welcome to Biryani
==================

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

This sample uses `WebOb <http://webob.org/>`_.

>>> import webob
>>> from biryani import allconv as conv
>>> validate_form = conv.mapping(dict(
...     username = conv.pipe(conv.multidict_get('username'), conv.cleanup_line, conv.require),
...     password = conv.pipe(
...         conv.multidict_getall('password'),
...         conv.test(lambda passwords: len(passwords) == 2 and passwords[0] == passwords[1],
...             error = 'Password mismatch'),
...         conv.function(lambda passwords: passwords[0]),
...         ),
...     email = conv.pipe(conv.multidict_get('email'), conv.str_to_email),
...     tags = conv.pipe(
...         conv.multidict_getall('tag'),
...         conv.function(u','.join),
...         conv.function(lambda tags: tags.split(u',')),
...         conv.uniform_sequence(conv.str_to_slug, constructor = set),
...         ),
...     ))

>>> req = webob.Request.blank('/?username=   John Doe&password=secret&password=secret&email=john@doe.name&tag=person&tag=user,ADMIN')
>>> result, errors = validate_form(req.GET)
>>> result
{'username': u'John Doe', 'password': u'secret', 'email': u'john@doe.name', 'tags': set([u'admin', u'person', u'user'])}
>>> conv.to_value(validate_form)(req.GET)
{'username': u'John Doe', 'password': u'secret', 'email': u'john@doe.name', 'tags': set([u'admin', u'person', u'user'])}

>>> req = webob.Request.blank('/?password=secret&password=other secret&email=john@doe.name&tag=person&tag=user,ADMIN')
>>> result, errors = validate_form(req.GET)
>>> result
{'password': [u'secret', u'other secret'], 'email': u'john@doe.name', 'tags': set([u'admin', u'person', u'user'])}
>>> errors
{'username': 'Missing value', 'password': 'Password mismatch'}
>>> conv.to_value(validate_form)(req.GET)
Traceback (most recent call last):
ValueError: {'username': 'Missing value', 'password': 'Password mismatch'}

>>> req = webob.Request.blank('/?username=John Doe&password=secret&email=john.doe.name')
>>> validate_form(req.GET)
({'username': u'John Doe', 'password': [u'secret'], 'email': u'john.doe.name'}, {'password': 'Password mismatch', 'email': 'An email must contain exactly one "@"'})


Documentation
=============

.. toctree::
   :maxdepth: 2

   tutorial
   how-to-use
   api
   sugar

.. TODO

   Comparison with FormEncode
   Howto use with WebOb
   How to use with lxml
   How to import a CSV file


Get Biryani
===========

Biryani is available as an easy-installable package on the `Python Package Index <http://pypi.python.org/pypi/Biryani>`_.

The code can be found in a Git repository, at http://gitorious.org/biryani.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

