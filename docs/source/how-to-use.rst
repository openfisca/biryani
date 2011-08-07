**************************
How to to use in a project
**************************


Howto use Biryani in a simple project
=====================================

::

    from biryani import allconv as conv

    # Use the converters. For example:
    s = '5'
    i = conv.to_value(conv.str_to_int, conv.require)(s)
    assert i == 5
    ...


Howto use Biryani in a multi-modules project
============================================

In your project, create a module named ``conv.py``.

In this file, either import every converter, all in once::

    from biryani.allconv import *
    from biryani import states


Or specify the converters you want::

    from biryani.babelconv import *
    from biryani.baseconv import *
    from biryani.bsonconv import *
    from biryani.datetimeconv import *
    from biryani.pymongoconv import *
    from biryani.webobconv import *
    ...
    from biryani import states

Append your own converters in this file.

In your others modules add::

    from . import conv

    # Use the converters. For example:
    s = '5'
    i = conv.to_value(conv.str_to_int, conv.require)(s)
    assert i == 5
    ...

