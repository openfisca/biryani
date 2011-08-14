************
API Overview
************


Data Converters
===============

.. testsetup::

   from biryani.baseconv import *


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


Class & Instance Converters
---------------------------

.. autofunction:: biryani.baseconv.dict_to_instance
   :noindex:


Collection (aka dict, list, set, tuple, etc) Converters
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


Date & Time Converters
----------------------

.. testsetup::

   from biryani.datetimeconv import *

.. automodule:: biryani.datetimeconv
   :members:
   :undoc-members:
   :noindex:


Internet Data Converters
------------------------

.. autofunction:: biryani.baseconv.str_to_email
   :noindex:

.. autofunction:: biryani.baseconv.str_to_json
   :noindex:

.. autofunction:: biryani.baseconv.str_to_url
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


Special Converters
==================

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


String Functions
================

.. testsetup::

   from biryani.strings import *

.. automodule:: biryani.strings
   :members:
   :undoc-members:
   :noindex:

