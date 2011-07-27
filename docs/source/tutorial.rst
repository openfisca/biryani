********
Tutorial
********

    >>> from biryani import allconv as conv
    >>> input_value = u'42'
    >>> output_value, error = conv.unicode_to_float(input_value)
    >>> output_value, error
    (42.0, None)
    >>> conv.unicode_to_float('forty two')
    ('forty two', 'Value must be a float')

Converters usually don't test their input value::

    >>> conv.unicode_to_float(42)
    Traceback (most recent call last):
    AttributeError: 'int' object has no attribute 'strip'

So, to ensure that input value is an unicode string, we need to chain several converters::

    >>> conv.pipe(
    ...     conv.test_isinstance(unicode),
    ...     conv.unicode_to_float,
    ...     )(u'42')
    (42.0, None)
    >>> conv.pipe(
    ...     conv.test_isinstance(unicode),
    ...     conv.unicode_to_float,
    ...     )(42)
    (42, "Value is not an instance of <type 'unicode'>")
    >>> conv.pipe(
    ...     conv.test_isinstance(unicode),
    ...     conv.unicode_to_float,
    ...     )('42')
    ('42', "Value is not an instance of <type 'unicode'>")

Use ``conv.to_value`` to extract value from conversion result or raise an exception when an error occurs:

    >>> conv.to_value(conv.pipe(
    ...     conv.test_isinstance(unicode),
    ...     conv.unicode_to_float,
    ...     ))(u'42')
    42.0
    >>> conv.to_value(conv.pipe(
    ...     conv.test_isinstance(unicode),
    ...     conv.unicode_to_float,
    ...     ))(42)
    Traceback (most recent call last):
    ValueError: Value is not an instance of <type 'unicode'>

Add a custom function to convert string to unicode when needed, and store resulting converter into a variable::

    >>> any_string_to_float = conv.pipe(
    ...     conv.function(lambda value: value.decode('utf-8') if isinstance(value, str) else value),
    ...     conv.test_isinstance(unicode),
    ...     conv.unicode_to_float,
    ...     )
    >>> any_string_to_float('42')
    (42.0, None)
    >>> any_string_to_float(u'42')
    (42.0, None)

.. note:: The builtin converter :func:`biryani.baseconv.string_to_unicode`: does the same thing as the conversion
   function above.

   So the converter could be simplified to::

        >>> anything_to_float = conv.pipe(
        ...     conv.string_to_unicode(),
        ...     conv.test_isinstance(unicode),
        ...     conv.unicode_to_float,
        ...     )
        >>> any_string_to_float('42')
        (42.0, None)
        >>> any_string_to_float(u'42')
        (42.0, None)

We can harden the custom function to convert anything to unicode::

    >>> anything_to_float = conv.pipe(
    ...     conv.function(lambda value: value.decode('utf-8') if isinstance(value, str) else unicode(value)),
    ...     conv.test_isinstance(unicode),
    ...     conv.unicode_to_float,
    ...     )
    >>> anything_to_float(42)
    (42.0, None)

Add ``conv.cleanup_line`` to strip spaces from string and convert it to None when empty::

    >>> anything_to_float = conv.pipe(
    ...     conv.function(lambda value: value.decode('utf-8') if isinstance(value, str) else unicode(value)),
    ...     conv.test_isinstance(unicode),
    ...     conv.cleanup_line,
    ...     conv.unicode_to_float,
    ...     )
    >>> anything_to_float('  42   ')
    (42.0, None)
    >>> anything_to_float(u'     ')
    (None, None)

Add ``conv.require`` to generate an error when value is missing (ie is ``None``)::

    >>> anything_to_float = conv.pipe(
    ...     conv.function(lambda value: value.decode('utf-8') if isinstance(value, str) else unicode(value)),
    ...     conv.test_isinstance(unicode),
    ...     conv.cleanup_line,
    ...     conv.unicode_to_float,
    ...     conv.require,
    ...     )
    >>> anything_to_float(u'     ')
    (None, 'Missing value')

Use a custom ``test`` to ensure that float is a valid latitude::

    >>> anything_to_latitude = conv.pipe(
    ...     conv.function(lambda value: value.decode('utf-8') if isinstance(value, str) else unicode(value)),
    ...     conv.test_isinstance(unicode),
    ...     conv.cleanup_line,
    ...     conv.unicode_to_float,
    ...     conv.test(lambda value: -180 <= value <= 180),
    ...     conv.require,
    ...     )
    >>> anything_to_latitude('50')
    (50.0, None)
    >>> anything_to_latitude('')
    (None, 'Missing value')
    >>> anything_to_latitude(' -123.4 ')
    (-123.40000000000001, None)
    >>> anything_to_latitude(u'500')
    (500.0, 'Test failed')

Add an explicit error message when latitude is not between -180 and 180 degrees::

    >>> anything_to_latitude = conv.pipe(
    ...     conv.function(lambda value: value.decode('utf-8') if isinstance(value, str) else unicode(value)),
    ...     conv.test_isinstance(unicode),
    ...     conv.cleanup_line,
    ...     conv.unicode_to_float,
    ...     conv.test(lambda value: -180 <= value <= 180, error = 'Latitude must be between -180 and 180'),
    ...     conv.require,
    ...     )
    >>> anything_to_latitude(u'500')
    (500.0, 'Latitude must be between -180 and 180')

Generalize the converter to a function that accepts any bound::

    >>> def anything_to_bounded_float(min_bound, max_bound):
    ...     return conv.pipe(
    ...         conv.function(lambda value: value.decode('utf-8') if isinstance(value, str) else unicode(value)),
    ...         conv.test_isinstance(unicode),
    ...         conv.cleanup_line,
    ...         conv.unicode_to_float,
    ...         conv.test(lambda value: min_bound <= value <= max_bound,
    ...             error = 'Value must be between {0} and {1}'.format(min_bound, max_bound)),
    ...         conv.require,
    ...         )
    >>> anything_to_bounded_float(-180, 180)(90)
    (90.0, None)

.. note:: The builtin converter :func:`biryani.baseconv.test_between`: does the same thing as the test on bounds above.

   So the converter could be simplified to::

        >>> def anything_to_bounded_float(min_bound, max_bound):
        ...     return conv.pipe(
        ...         conv.function(lambda value: value.decode('utf-8') if isinstance(value, str) else unicode(value)),
        ...         conv.test_isinstance(unicode),
        ...         conv.cleanup_line,
        ...         conv.unicode_to_float,
        ...         conv.test_between(min_bound, max_bound),
        ...         conv.require,
        ...         )
        >>> anything_to_bounded_float(-180, 180)(90)
        (90.0, None)


Use the generalized function to convert a dictionary containing both a latitude and a longitude::

    >>> dict_to_lat_long = conv.structured_mapping(dict(
    ...     latitude = anything_to_bounded_float(-180, 180),
    ...     longitude = anything_to_bounded_float(-360, 360),
    ...     ))
    >>> dict_to_lat_long(dict(latitude = '-12.34', longitude = u"45"))
    ({'latitude': -12.34, 'longitude': 45.0}, None)
    >>> dict_to_lat_long(dict(latitude = '-12.34', longitude = u"45,6"))
    ({'latitude': -12.34}, {'longitude': 'Value must be a float'})
    >>> dict_to_lat_long(dict(latitude = None, longitude = ''))
    (None, {'latitude': 'Missing value', 'longitude': 'Missing value'})
    >>> dict_to_lat_long(None)
    (None, None)

Converters working on complex structures can be chained too::

    >>> dict_to_lat_long = conv.pipe(
    ...     conv.test_isinstance(dict),
    ...     conv.structured_mapping(dict(
    ...         latitude = anything_to_bounded_float(-180, 180),
    ...         longitude = anything_to_bounded_float(-360, 360),
    ...         )),
    ...     conv.require,
    ...     )
    >>> dict_to_lat_long(dict(latitude = '-12.34', longitude = u"45"))
    ({'latitude': -12.34, 'longitude': 45.0}, None)
    >>> dict_to_lat_long(dict(latitude = '-12.34', longitude = u"45,6"))
    ({'latitude': -12.34}, {'longitude': 'Value must be a float'})
    >>> dict_to_lat_long(['-12.34', u"45"])
    (['-12.34', u'45'], "Value is not an instance of <type 'dict'>")
    >>> dict_to_lat_long(None)
    (None, 'Missing value')

