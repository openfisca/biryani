************************************
How to to use *Biryani* in a project
************************************

.. note:: This chapter shows a few ways to import *Biryani* in your projects. They have proven there effectiveness, but
   there are other ways to import *Biryani*.


How to use *Biryani* in a simple project
========================================

*Biryani* allows you to import only the modules you really need and to merge them in a single pseudo-module::

    import biryani
    import biryani.baseconv
    import biryani.datetimeconv
    conv = biryani.custom_conv(biryani.baseconv, biryani.datetimeconv)

    # Use the converters. For example:
    d = conv.check(conv.iso8601_input_to_date)(u'1789-07-14')
    ...

See :func:`biryani.custom_conv` for more informations.


How to use *Biryani* in a multi-modules project
===============================================

In your project, create a module named ``conv.py``.

In this file, specify the converters you want::

    from biryani.babelconv import *
    from biryani.baseconv import *
    from biryani.bsonconv import *
    from biryani.datetimeconv import *
    from biryani.objectconv import *
    from biryani.webobconv import *
    ...
    from biryani import states

Append your own converters in this file.

In your others modules add::

    from . import conv

    # Use the converters. For example:
    s = '5'
    i = conv.check(conv.pipe(conv.input_to_int, conv.not_none))(s)
    assert i == 5
    ...

