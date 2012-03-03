********************************
How to create your own converter
********************************

There is 3 kinds of converters:

* the converters that never generate an error, called *functions*,
* the filters that only test input value, called *tests*,
* the generic form of converters.


Functions
=========

To create a converter that never produces an error, the easiest method is to create a function that accepts the input
value as argument and that returns the output value as its only result. Then you just have to wrap this function using
the :func:`biryan.baseconv.function` converter.

Example of a converter that returns the length of a value:

>>> from biryani import baseconv as conv
...
>>> python_data_to_len = conv.function(lambda value: len(value))
...
>>> python_data_to_len(u'abc')
(3, None)
>>> python_data_to_len([1, 2, 3])
(3, None)
>>> python_data_to_len([])
(0, None)

By default, the function converter doesn't call its wrapped function when input value is None and always returns ``None``,
so:

>>> python_data_to_len(None)
(None, None)

Most of the times this is the correct behaviour, because in *Biryani*, when the input value is missing (aka ``None``) a
converter is considered to have nothing to convert and should return nothing (aka ``None``).

But, if you want to change this behaviour, you can set the ``handle_missing_value`` flag:

>>> python_data_to_len = conv.function(lambda value: len(value), handle_missing_value = True)
...
>>> python_data_to_len(None)
Traceback (most recent call last):
TypeError: object of type 'NoneType' has no len()

In this case, you will have to rewrite your function to handle the ``None`` input value:

>>> python_data_to_len = conv.function(lambda value: len(value or []), handle_missing_value = True)
...
>>> python_data_to_len(None)
(0, None)

In the same way, if your function needs to use the state (mainly for internationalization reasons), you need to set
the ``handle_state`` flag.

For example, here is a function that counts if there is "zero", "one" or "many" items in input value and returns the
localized response.

>>> from biryani import states
...
>>> def zero_one_or_many(value, state = states.default_state):
...     size = len(value)
...     if size == 0:
...         return state._(u'zero')
...     elif size == 1:
...         return state._(u'one')
...     else:
...         return state._(u'many')
...
>>> convert_to_zero_one_or_many = conv.function(zero_one_or_many, handle_state = True)
...
>>> convert_to_zero_one_or_many(u'')
(u'zero', None)
>>> convert_to_zero_one_or_many(u'a')
(u'one', None)
>>> convert_to_zero_one_or_many(u'abc')
(u'many', None)
>>>
>>> class FrenchState(object):
...     def _(self, s):
...         return {
...             u'many': u'beaucoup',
...             u'one': u'un',
...             }.get(s, s)
>>> french_state = FrenchState()
...
>>> convert_to_zero_one_or_many(u'', state = french_state)
(u'zero', None)
>>> convert_to_zero_one_or_many(u'a', state = french_state)
(u'un', None)
>>> convert_to_zero_one_or_many(u'abc', state = french_state)
(u'beaucoup', None)


Tests
=====

To create a converter that tests its input value without modifying it and that produces an error when test fails, the 
easiest method is to create a function that accepts the input value as argument and that returns the result of the test
as a boolean. Then you just have to wrap this test function using the :func:`biryan.baseconv.test` converter.

Example of a converter that tests whether a password as a sufficient length:

>>> test_valid_password = conv.test(lambda password: len(password) >= 8)
...
>>> test_valid_password(u'abcdefgh')
(u'abcdefgh', None)
>>> test_valid_password(u'123')
(u'123', u'Test failed')

You can changed default error message, using the ``error`` argument:

>>> test_valid_password = conv.test(lambda password: len(password) >= 8, error = u'Password too short')
...
>>> test_valid_password(u'123')
(u'123', u'Password too short')

By default, the test converter doesn't call its wrapped function when input value is None and always returns ``None``,
so:

>>> test_valid_password(None)
(None, None)

Most of the times this is the correct behaviour, because in *Biryani*, when the input value is missing (aka ``None``) a
test is considered to have nothing to test and should return nothing (aka ``None``).

But, if you want to change this behaviour, you can set the ``handle_missing_value`` flag:

>>> test_valid_password = conv.test(lambda password: len(password) >= 8, handle_missing_value = True)
...
>>> test_valid_password(None)
Traceback (most recent call last):
TypeError: object of type 'NoneType' has no len()

In this case, you will have to rewrite your test to handle the ``None`` input value:

>>> test_valid_password = conv.test(lambda password: len(password or u'') >= 8, handle_missing_value = True)
...
>>> test_valid_password(None)
(None, u'Test failed')

In the same way, if your test needs to use the state (mainly for internationalization reasons), you need to set
the ``handle_state`` flag.

For example, here is a filter that tests whether the localized version of a string as an even length:

>>> def has_even_len(value, state = states.default_state):
...     return len(state._(value)) % 2 == 0
...
>>> test_has_even_len = conv.test(has_even_len, handle_state = True)
...
>>> test_has_even_len(u'many')
(u'many', None)
>>> test_has_even_len(u'one')
(u'one', u'Test failed')
>>> test_has_even_len(u'one', state = french_state)
(u'one', None)
>>> test_has_even_len(u'two', state = french_state)
(u'two', u'Test failed')


Generic converters
==================

Example of a custom converter that accepts a couple of passwords as input value, compares the two passwords and either
generates an error when they differ or are two short, or returns the valid password when they match.

A converter is a function that has two parameters, the input value and the state, and that returns a couple
(output value, eventual error message).

>>> def validate_password(passwords, state = states.default_state):
...     # Generally, a converter should ignore a ``None`` input value:
...     if passwords is None:
...         return passwords, None
...     # Test passwords.
...     if len(passwords) < 2:
...         # When an error occurs and output value can not be computed, return input value with the error message.
...         # Every error message is localized using ``state._()``.
...         return passwords, state._(u'Missing passwords')
...     password = passwords[0]
...     if password != passwords[1]:
...         return passwords, state._(u'Password mismatch')
...     if len(password) < 8:
...         return password, state._(u'Password too short')
...     return password, None

>>> validate_password([u'abcdefgh', u'abcdefgh'])
(u'abcdefgh', None)
>>> validate_password([u'abc', u'abc'])
(u'abc', u'Password too short')
>>> validate_password([u'abcdefgh'])
([u'abcdefgh'], u'Missing passwords')

To create a customizable converter you should write a function accepting customizing options as parameters and returning
a customized converters.

For example, to transform our password validator to add a minimal password length:

>>> def validate_password(min_len = 6):
...     def validate_password_converter(passwords, state = states.default_state):
...         # Generally, a converter should ignore a ``None`` input value:
...         if passwords is None:
...             return passwords, None
...         # Test passwords.
...         if len(passwords) < 2:
...             # When an error occurs and output value can not be computed, return input value with the error message.
...             # Every error message is localized using ``state._()``.
...             return passwords, state._(u'Missing passwords')
...         password = passwords[0]
...         if password != passwords[1]:
...             return passwords, state._(u'Password mismatch')
...         if len(password) < min_len:
...             return password, state._(u'Password too short')
...         return password, None
...     return validate_password_converter

>>> validate_password()([u'abcdefgh', u'abcdefgh'])
(u'abcdefgh', None)
>>> validate_password()([u'abc', u'abc'])
(u'abc', u'Password too short')
>>> validate_password(3)([u'abc', u'abc'])
(u'abc', None)

.. note:: This converter could also be written by combining existing converters:

    >>> def validate_password(min_len = 6):
    ...     return conv.pipe(
    ...         conv.test(lambda passwords: len(passwords) >= 2,
    ...             error = u'Missing passwords'),
    ...         conv.test(lambda passwords: passwords[0] == passwords[1],
    ...             error = u'Password mismatch'),
    ...         conv.function(lambda passwords: passwords[0]),
    ...         conv.test(lambda password: len(password) >= min_len,
    ...             error = u'Password too short'),
    ...         )

    >>> validate_password()([u'abcdefgh', u'abcdefgh'])
    (u'abcdefgh', None)
    >>> validate_password()([u'abc', u'abc'])
    (u'abc', u'Password too short')
    >>> validate_password(3)([u'abc', u'abc'])
    (u'abc', None)

