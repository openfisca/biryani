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

>>> python_data_to_len = conv.function(lambda value: len(value or ''), handle_missing_value = True)
...
>>> python_data_to_len(None)
(0, None)

In the same way, if your function needs to use the state (for example for internationalization reasons), you need to set
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

