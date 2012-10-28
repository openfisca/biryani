*********************************
Tutorial 1: Validating a web form
*********************************


Objective
=========

This tutorial is a step by step guide that explains how to use *Biryani* to validate and convert the following web form:

* Username
* Password (2 times)
* Email
* Tags (several fields with the same name, each one may contain several tags separated by a comma)

It assumes that the forms is sent to the root of a web site using a HTTP POST method.


Prerequisite
============

This tutorial uses `WebOb <http://webob.org/>`_ to generate and parse requests, but could be easily transposed to other
web libraries.

>>> import webob

To generate a request:

>>> req1 = webob.Request.blank('/', POST = 'username=   John Doe&password=secret&password=bad')

To parse it:

>>> req1.POST.get('username')
u'   John Doe'
>>> req1.POST.getall('password')
[u'secret', u'bad']


First steps with *Biryani*
==========================

*Biryani* is a Python package split into several modules, to allow you to ony import the converters you need for your
application. The most frequently used converters are in package :mod:`biryani1.baseconv`.

>>> from biryani1 import baseconv as conv

First we need to cleanup username:

>>> def validate_form(params):
...     error = None
...     username = params.get('username')
...     if username is not None:
...         username = username.strip()
...         if not username:
...             username = None
...     return username, error
...
>>> validate_form(req1.POST)
(u'John Doe', None)

*Biryani* has a converter :func:`biryani1.baseconv.cleanup_line` that just does what the above function do.
So we can rewrite the `validate_form` function using it:

>>> def validate_form(params):
...     return conv.cleanup_line(params.get('username'))
...
>>> validate_form(req1.POST)
(u'John Doe', None)


Chaining converters
===================

Now, we need to ensure that submitted form always contains an username:

>>> def validate_form(params):
...     username, error = conv.cleanup_line(params.get('username'))
...     if error is None and username is None:
...         error = u'Missing value'
...     return username, error
...
>>> validate_form(req1.POST)
(u'John Doe', None)
>>> req2 = webob.Request.blank('/', POST = 'password=secret&password=bad')
>>> validate_form(req2.POST)
(None, u'Missing value')
>>> req3 = webob.Request.blank('/', POST = 'username=   &password=secret&password=bad')
>>> validate_form(req3.POST)
(None, u'Missing value')

*Biryani* has a filter :func:`biryani1.baseconv.not_none` that checks for ``None`` values:

>>> def validate_form(params):
...     username, error = conv.cleanup_line(params.get('username'))
...     if error is None:
...         username, error = conv.not_none(username)
...     return username, error

The :func:`biryani1.baseconv.pipe` allows to chain several converters. This simplifies the function:

>>> def validate_form(params):
...     return conv.pipe(conv.cleanup_line, conv.not_none)(params.get('username'))
...
>>> validate_form(req1.POST)
(u'John Doe', None)
>>> validate_form(req2.POST)
(None, u'Missing value')
>>> validate_form(req3.POST)
(None, u'Missing value')


Converting structures
=====================

Now that username is converted, we need to do the same thing for email. Let's transform function `validate_form` to
accept a dictionary containing submitted username & email, and to return a couple with another dictionary containing
converted username & email, and a dictionary containing the errors (or ``None`` when there is no error):

>>> def validate_form(params):
...     data = {}
...     errors = {}
...     username, error = conv.pipe(conv.cleanup_line, conv.not_none)(params.get('username'))
...     if username is not None:
...         data['username'] = username
...     if error is not None:
...         errors['username'] = error
...     email, error = conv.input_to_email(params.get('email'))
...     if email is not None:
...         data['email'] = email
...     if error is not None:
...         errors['email'] = error
...     return data, errors or None
...
>>> req4 = webob.Request.blank('/', POST = 'username=John Doe&email=john@doe.name')
>>> validate_form(req4.POST)
({'username': u'John Doe', 'email': u'john@doe.name'}, None)
>>> req5 = webob.Request.blank('/', POST = 'username=   John Doe&email=john.doe.name')
>>> validate_form(req5.POST)
({'username': u'John Doe', 'email': u'john.doe.name'}, {'email': u'An email must contain exactly one "@"'})
>>> req6 = webob.Request.blank('/', POST = 'email=john.doe.name')
>>> validate_form(req6.POST)
({'email': u'john.doe.name'}, {'username': u'Missing value', 'email': u'An email must contain exactly one "@"'})

Using the converter :func:`biryani1.baseconv.struct`, the fonction can be simplified to:

>>> def validate_form(params):
...     return conv.struct(dict(
...         username = conv.pipe(conv.cleanup_line, conv.not_none),
...         email = conv.input_to_email,
...         ))(params)
...
>>> validate_form(req4.POST)
({'username': u'John Doe', 'email': u'john@doe.name'}, None)
>>> validate_form(req5.POST)
({'username': u'John Doe', 'email': u'john.doe.name'}, {'email': u'An email must contain exactly one "@"'})
>>> validate_form(req6.POST)
({'username': None, 'email': u'john.doe.name'}, {'username': u'Missing value', 'email': u'An email must contain exactly one "@"'})

This form validator is slightly different from the previous one, because it doesn't accept unexpected parameters:

>>> req7 = webob.Request.blank('/', POST = 'username=John Doe&email=john@doe.name&password=secret')
>>> validate_form(req7.POST)
({'username': u'John Doe', u'password': u'secret', 'email': u'john@doe.name'}, {u'password': u'Unexpected item'})

If we want to drop unexpected parameters, we need to use the ``default`` option of the :func:`biryani1.baseconv.struct`
converter:

>>> def validate_form(params):
...     return conv.struct(
...         dict(
...             username = conv.pipe(conv.cleanup_line, conv.not_none),
...             email = conv.input_to_email,
...             ),
...         default = 'drop',
...         )(params)
...
>>> req7 = webob.Request.blank('/', POST = 'username=John Doe&email=john@doe.name&password=secret')
>>> validate_form(req7.POST)
({'username': u'John Doe', 'email': u'john@doe.name'}, None)

If instead, we want to apply a default conversion, to the unexpected parameters, we can specify a converter in the
``default`` option. For example, to keep all unexpected parameters unchanged:

>>> def validate_form(params):
...     return conv.struct(
...         dict(
...             username = conv.pipe(conv.cleanup_line, conv.not_none),
...             email = conv.input_to_email,
...             ),
...         default = conv.noop,
...         )(params)
...
>>> req7 = webob.Request.blank('/', POST = 'username=John Doe&email=john@doe.name&password=secret')
>>> validate_form(req7.POST)
({'username': u'John Doe', u'password': u'secret', 'email': u'john@doe.name'}, None)


Using custom converters and filters
===================================

For the password, we need to ensure that it is present twice in submitted form and that both values are the same.
Let's add it to our function:

>>> def validate_form(params):
...     data, errors = conv.struct(
...         dict(
...             username = conv.pipe(conv.cleanup_line, conv.not_none),
...             email = conv.input_to_email,
...             ),
...         default = 'drop',
...         )(params)
...     passwords = params.getall('password')
...     if len(passwords) == 2 and passwords[0] == passwords[1]:
...         data['password'] = passwords[0]
...     else:
...         if errors is None:
...             errors = {}
...         errors['password'] = u'Password mismatch'
...         data['password'] = passwords # Return the erroneous values of password to show the error.
...     return data, errors
...
>>> req8 = webob.Request.blank('/', POST = 'username=   John Doe&password=secret&password=secret')
>>> validate_form(req8.POST)
({'username': u'John Doe', 'password': u'secret', 'email': None}, None)
>>> req1 = webob.Request.blank('/', POST = 'username=   John Doe&password=secret&password=bad')
>>> validate_form(req1.POST)
({'username': u'John Doe', 'password': [u'secret', u'bad'], 'email': None}, {'password': u'Password mismatch'})
>>> req9 = webob.Request.blank('/', POST = 'username=   John Doe&password=secret')
>>> validate_form(req9.POST)
({'username': u'John Doe', 'password': [u'secret'], 'email': None}, {'password': u'Password mismatch'})

In *Biryani*, there is no filter that checks that there is two passwords and that they are equal.
But we can easily write one using :func:`biryani1.baseconv.test`:

>>> test_passwords = conv.test(lambda passwords: len(passwords) == 2 and passwords[0] == passwords[1])
...
>>> test_passwords([u'secret', u'secret'])
([u'secret', u'secret'], None)
>>> test_passwords([u'secret', u'bad'])
([u'secret', u'bad'], u'Test failed')
>>> test_passwords([u'secret'])
([u'secret'], u'Test failed')

We can improve the error message of our test:

>>> test_passwords = conv.test(lambda passwords: len(passwords) == 2 and passwords[0] == passwords[1],
...     error = u'Password mismatch')
...
>>> test_passwords([u'secret', u'secret'])
([u'secret', u'secret'], None)
>>> test_passwords([u'secret', u'bad'])
([u'secret', u'bad'], u'Password mismatch')

But, when no password is given, we don't want to compare them. Currently, we obtain:

>>> test_passwords(None)
(None, None)

But:

>>> test_passwords([])
([], u'Password mismatch')

So we add the :func:`biryani1.baseconv.empty_to_none` converter to convert an empty list of password to ``None``:

>>> test_passwords = conv.pipe(
...     conv.empty_to_none,
...     conv.test(lambda passwords: len(passwords) == 2 and passwords[0] == passwords[1]),
...     )
...
>>> test_passwords([u'secret', u'secret'])
([u'secret', u'secret'], None)
>>> test_passwords([u'secret', u'bad'])
([u'secret', u'bad'], u'Test failed')
>>> test_passwords([u'secret'])
([u'secret'], u'Test failed')
>>> test_passwords(None)
(None, None)
>>> test_passwords([])
(None, None)

Now, when the two passwords are the same we must extract the first one. There is no standard converter in *Biryani* to
extract the first item of a list, but we can create it using :func:`biryani1.baseconv.function`:

>>> extract_first_item = conv.function(lambda items: items[0])
...
>>> extract_first_item([u'secret', u'secret'])
(u'secret', None)

Let's combine `test_passwords` and `extract_first_item` to rewrite our `validate_form` function:

>>> def validate_form(params):
...     inputs = dict(
...         username = params.get('username'),
...         password = params.getall('password'),
...         email = params.get('email'),
...         )
...     return conv.struct(dict(
...         username = conv.pipe(conv.cleanup_line, conv.not_none),
...         password = conv.pipe(
...             conv.empty_to_none,
...             conv.test(lambda passwords: len(passwords) == 2 and passwords[0] == passwords[1],
...                 error = u'Password mismatch'),
...             conv.function(lambda passwords: passwords[0]),
...             ),
...         email = conv.input_to_email,
...         ))(inputs)
...
>>> validate_form(req8.POST)
({'username': u'John Doe', 'password': u'secret', 'email': None}, None)
>>> validate_form(req1.POST)
({'username': u'John Doe', 'password': [u'secret', u'bad'], 'email': None}, {'password': u'Password mismatch'})
>>> validate_form(req9.POST)
({'username': u'John Doe', 'password': [u'secret'], 'email': None}, {'password': u'Password mismatch'})


Adding complexity
=================

Our form validator is nearly finished, the last fields that we will validate are the tags.

The `tag` field can be repeated and each one can contain several tags separated by a comma.

We can split the various `tag` fields using the following function:

>>> def cleanup_tags(tags):
...     return u','.join(tags).split(u',')
...
>>> cleanup_tags([u'friend', u'user,ADMIN', u'', u'customer, friend'])
[u'friend', u'user', u'ADMIN', u'', u'customer', u' friend']

Let's improve the function to also clean up tags and remove empty ones:

>>> def cleanup_tags(tags):
...     return [
...         clean_tag
...         for clean_tag in (
...             tag.strip().lower()
...             for tag in u','.join(tags).split(u',')
...             )
...         if clean_tag
...         ]
...
>>> cleanup_tags([u'friend', u'user,ADMIN', u'', u'customer, friend'])
[u'friend', u'user', u'admin', u'customer', u'friend']

Add removal of duplicate tags and sort the result:

>>> def cleanup_tags(tags):
...     return sorted(set([
...         clean_tag
...         for clean_tag in (
...             tag.strip().lower()
...             for tag in u','.join(tags).split(u',')
...             )
...         if clean_tag
...         ]))
...
>>> cleanup_tags([u'friend', u'user,ADMIN', u'', u'customer, friend'])
[u'admin', u'customer', u'friend', u'user']

Replace the empty tags array to ``None`` when it is empty:


>>> def cleanup_tags(tags):
...     return sorted(set([
...         clean_tag
...         for clean_tag in (
...             tag.strip().lower()
...             for tag in u','.join(tags).split(u',')
...             )
...         if clean_tag
...         ])) or None
...
>>> cleanup_tags([u'friend', u'user,ADMIN', u'', u'customer, friend'])
[u'admin', u'customer', u'friend', u'user']
>>> cleanup_tags([u'', u'    '])

Now use this function in `validate_form`:

>>> def validate_form(params):
...     inputs = dict(
...         username = params.get('username'),
...         password = params.getall('password'),
...         email = params.get('email'),
...         tags = params.getall('tag'),
...         )
...     def cleanup_tags(tags):
...         return sorted(set([
...             clean_tag
...             for clean_tag in (
...                 tag.strip().lower()
...                 for tag in u','.join(tags).split(u',')
...                 )
...             if clean_tag
...             ])) or None
...     return conv.struct(dict(
...         username = conv.pipe(conv.cleanup_line, conv.not_none),
...         password = conv.pipe(
...             conv.empty_to_none,
...             conv.test(lambda passwords: len(passwords) == 2 and passwords[0] == passwords[1],
...                 error = u'Password mismatch'),
...             conv.function(lambda passwords: passwords[0]),
...             ),
...         email = conv.input_to_email,
...         tags = conv.function(cleanup_tags),
...         ))(inputs)
...
>>> req10 = webob.Request.blank('/', POST = 'username=   John Doe&tag=friend&tag=user,ADMIN&tag=&tag=customer, friend')
>>> validate_form(req10.POST)
({'username': u'John Doe', 'password': None, 'email': None, 'tags': [u'admin', u'customer', u'friend', u'user']}, None)


The end
=======

Our form validator works well, but let's rewrite the tags converter in a more "biryanic" way:

* To split tags in a single list, we can use::

    conv.function(lambda tags: u','.join(tags).split(u','))

* To simplify each tag in the generated list, we can use our good friend :func:`biryani1.baseconv.cleanup_line` in
  combination with :func:`biryani1.baseconv.uniform_sequence` that will applies it to each item of the list::

    conv.uniform_sequence(conv.cleanup_str)

* :func:`biryani1.baseconv.cleanup_line` as even an option that generates a set instead of a list::

    conv.uniform_sequence(conv.cleanup_str, constructor = set)

* We can make a slight improvement by converting each tag to a slug, using :func:`biryani1.baseconv.input_to_slug` to
  remove diacritical marks, etc::

    conv.uniform_sequence(conv.input_to_slug, constructor = set)

Let's combine everything in a new version of `validate_form`:

>>> def validate_form(params):
...     inputs = dict(
...         username = params.get('username'),
...         password = params.getall('password'),
...         email = params.get('email'),
...         tags = params.getall('tag'),
...         )
...     return conv.struct(dict(
...         username = conv.pipe(conv.cleanup_line, conv.not_none),
...         password = conv.pipe(
...             conv.empty_to_none,
...             conv.test(lambda passwords: len(passwords) == 2 and passwords[0] == passwords[1],
...                 error = u'Password mismatch'),
...             conv.function(lambda passwords: passwords[0]),
...             ),
...         email = conv.input_to_email,
...         tags = conv.pipe(
...             conv.function(lambda tags: u','.join(tags).split(u',')),
...             conv.uniform_sequence(conv.input_to_slug, constructor = set, drop_none_items = True),
...             conv.function(sorted),
...             ),
...         ))(inputs)
...
>>> validate_form(req10.POST)
({'username': u'John Doe', 'password': None, 'email': None, 'tags': [u'admin', u'customer', u'friend', u'user']}, None)
>>> req11 = webob.Request.blank('/', POST = 'username=Jean Dupont&tag=Rêveur, Œil de Lynx&tag=COLLÈGUE')
>>> validate_form(req11.POST)
({'username': u'Jean Dupont', 'password': None, 'email': None, 'tags': [u'collegue', u'oeil-de-lynx', u'reveur']}, None)

Our form converter is now completed.

Hopefully, this tutorial has shown you, that *Biryani* is both useful, elegant and powerful, that it can be easily mixed
with *non-Biryani* code and that it can be incrementally extended to cover your needs.

