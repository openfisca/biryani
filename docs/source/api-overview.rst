************
API Overview
************

.. testsetup::

   from biryani import *
   from biryani.baseconv import *
   from biryani.strings import *


Data Converters
===============


Boolean Converters
------------------

.. autofunction:: biryani.baseconv.bool_to_str
   :noindex:

.. autofunction:: biryani.baseconv.guess_bool
   :noindex:

.. autofunction:: biryani.baseconv.python_data_to_bool
   :noindex:

.. autofunction:: biryani.baseconv.str_to_bool
   :noindex:


Collection (dict, list, set, tuple, etc) Converters
-------------------------------------------------------

.. autofunction:: biryani.baseconv.extract_when_singleton
   :noindex:

.. autofunction:: biryani.baseconv.get
   :noindex:

.. autofunction:: biryani.baseconv.item_or_sequence
   :noindex:

.. autofunction:: biryani.baseconv.new_struct
   :noindex:

.. autofunction:: biryani.baseconv.rename_item
   :noindex:

.. autofunction:: biryani.baseconv.struct
   :noindex:

.. autofunction:: biryani.baseconv.uniform_sequence
   :noindex:


Internet Data Converters
------------------------

.. autofunction:: biryani.baseconv.make_str_to_url
   :noindex:

.. autofunction:: biryani.baseconv.str_to_email
   :noindex:

.. autofunction:: biryani.baseconv.str_to_url_name
   :noindex:

.. autofunction:: biryani.baseconv.str_to_url_path_and_query
   :noindex:


Number Converters
-----------------

.. autofunction:: biryani.baseconv.str_to_float
   :noindex:

.. autofunction:: biryani.baseconv.str_to_int
   :noindex:

.. autofunction:: biryani.baseconv.python_data_to_float
   :noindex:

.. autofunction:: biryani.baseconv.python_data_to_int
   :noindex:


String Converters
-----------------

.. autofunction:: biryani.baseconv.make_str_to_normal_form
   :noindex:

.. autofunction:: biryani.baseconv.make_str_to_slug
   :noindex:

.. autofunction:: biryani.baseconv.cleanup_empty
   :noindex:

.. autofunction:: biryani.baseconv.cleanup_line
   :noindex:

.. autofunction:: biryani.baseconv.cleanup_text
   :noindex:

.. autofunction:: biryani.baseconv.decode_str
   :noindex:

.. autofunction:: biryani.baseconv.encode_str
   :noindex:

.. autofunction:: biryani.baseconv.str_to_slug
   :noindex:

.. autofunction:: biryani.baseconv.python_data_to_str
   :noindex:


Tests
-----

.. autofunction:: biryani.baseconv.exists
   :noindex:

.. autofunction:: biryani.baseconv.test
   :noindex:

.. autofunction:: biryani.baseconv.test_between
   :noindex:

.. autofunction:: biryani.baseconv.test_equals
   :noindex:

.. autofunction:: biryani.baseconv.test_exists
   :noindex:

.. autofunction:: biryani.baseconv.test_greater_or_equal
   :noindex:

.. autofunction:: biryani.baseconv.test_in
   :noindex:

.. autofunction:: biryani.baseconv.test_is
   :noindex:

.. autofunction:: biryani.baseconv.test_isinstance
   :noindex:

.. autofunction:: biryani.baseconv.test_less_or_equal
   :noindex:


Flow-Control Converters
=======================

.. autofunction:: biryani.baseconv.condition
   :noindex:

.. autofunction:: biryani.baseconv.first_match
   :noindex:

.. autofunction:: biryani.baseconv.pipe
   :noindex:

.. autofunction:: biryani.baseconv.switch
   :noindex:


Special Converters
==================

.. autofunction:: biryani.baseconv.catch_error
   :noindex:

.. autofunction:: biryani.baseconv.default
   :noindex:

.. autofunction:: biryani.baseconv.fail
   :noindex:

.. autofunction:: biryani.baseconv.function
   :noindex:

.. autofunction:: biryani.baseconv.noop
   :noindex:

.. autofunction:: biryani.baseconv.set_value
   :noindex:

.. autofunction:: biryani.baseconv.translate
   :noindex:


Converters-related Utilities
============================

.. autofunction:: biryani.baseconv.check
   :noindex:

.. autofunction:: biryani.custom_conv
   :noindex:


String Functions
================

.. automodule:: biryani.strings
   :members:
   :undoc-members:
   :noindex:


Extension Modules
=================

.. testsetup::

   from biryani.babelconv import *
   from biryani.base64conv import *
   from biryani.bsonconv import *
   from biryani.creditcardconv import *
   from biryani.datetimeconv import *
   from biryani.jsonconv import *
   from biryani.netconv import *
   from biryani.objectconv import *
   from biryani.webobconv import *


Babel Converters
----------------

.. automodule:: biryani.babelconv
   :members:
   :undoc-members:
   :noindex:


Base64 Converters
-----------------

.. automodule:: biryani.base64conv
   :members:
   :undoc-members:
   :noindex:


BSON Converters
---------------

.. automodule:: biryani.bsonconv
   :members:
   :undoc-members:
   :noindex:


Credit Card Converters
----------------------

.. automodule:: biryani.creditcardconv
   :members:
   :undoc-members:
   :noindex:


Date & Time Converters
----------------------

.. automodule:: biryani.datetimeconv
   :members:
   :undoc-members:
   :noindex:


JSON Converters
---------------

.. automodule:: biryani.jsonconv
   :members:
   :undoc-members:
   :noindex:


Network Converters
------------------

.. automodule:: biryani.netconv
   :members:
   :undoc-members:
   :noindex:


Object Converters
-----------------

.. automodule:: biryani.objectconv
   :members:
   :undoc-members:
   :noindex:


WebOb Converters
----------------

.. automodule:: biryani.webobconv
   :members:
   :undoc-members:
   :noindex:

