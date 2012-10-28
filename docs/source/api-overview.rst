************
API Overview
************

.. testsetup::

   from biryani1 import *
   from biryani1.baseconv import *
   from biryani1.strings import *


Data Converters
===============


Boolean Converters
------------------

.. autofunction:: biryani1.baseconv.anything_to_bool
   :noindex:

.. autofunction:: biryani1.baseconv.bool_to_str
   :noindex:

.. autofunction:: biryani1.baseconv.guess_bool
   :noindex:

.. autofunction:: biryani1.baseconv.input_to_bool
   :noindex:

.. autofunction:: biryani1.baseconv.str_to_bool
   :noindex:


Collection (dict, list, set, tuple, etc) Converters
-------------------------------------------------------

.. autofunction:: biryani1.baseconv.extract_when_singleton
   :noindex:

.. autofunction:: biryani1.baseconv.get
   :noindex:

.. autofunction:: biryani1.baseconv.item_or_sequence
   :noindex:

.. autofunction:: biryani1.baseconv.new_struct
   :noindex:

.. autofunction:: biryani1.baseconv.rename_item
   :noindex:

.. autofunction:: biryani1.baseconv.struct
   :noindex:

.. autofunction:: biryani1.baseconv.submapping
   :noindex:

.. autofunction:: biryani1.baseconv.uniform_mapping
   :noindex:

.. autofunction:: biryani1.baseconv.uniform_sequence
   :noindex:


Internet Data Converters
------------------------

.. autofunction:: biryani1.baseconv.input_to_email
   :noindex:

.. autofunction:: biryani1.baseconv.input_to_url_name
   :noindex:

.. autofunction:: biryani1.baseconv.input_to_url_path_and_query
   :noindex:

.. autofunction:: biryani1.baseconv.make_input_to_url
   :noindex:

.. autofunction:: biryani1.baseconv.make_str_to_url
   :noindex:

.. autofunction:: biryani1.baseconv.str_to_email
   :noindex:

.. autofunction:: biryani1.baseconv.str_to_url_path_and_query
   :noindex:


Number Converters
-----------------

.. autofunction:: biryani1.baseconv.anything_to_float
   :noindex:

.. autofunction:: biryani1.baseconv.anything_to_int
   :noindex:

.. autofunction:: biryani1.baseconv.input_to_float
   :noindex:

.. autofunction:: biryani1.baseconv.input_to_int
   :noindex:


String Converters
-----------------

.. autofunction:: biryani1.baseconv.anything_to_str
   :noindex:

.. autofunction:: biryani1.baseconv.cleanup_line
   :noindex:

.. autofunction:: biryani1.baseconv.cleanup_text
   :noindex:

.. autofunction:: biryani1.baseconv.decode_str
   :noindex:

.. autofunction:: biryani1.baseconv.empty_to_none
   :noindex:

.. autofunction:: biryani1.baseconv.encode_str
   :noindex:

.. autofunction:: biryani1.baseconv.input_to_slug
   :noindex:

.. autofunction:: biryani1.baseconv.make_input_to_normal_form
   :noindex:

.. autofunction:: biryani1.baseconv.make_input_to_slug
   :noindex:


Tests
-----

.. autofunction:: biryani1.baseconv.not_none
   :noindex:

.. autofunction:: biryani1.baseconv.test
   :noindex:

.. autofunction:: biryani1.baseconv.test_between
   :noindex:

.. autofunction:: biryani1.baseconv.test_conv
   :noindex:

.. autofunction:: biryani1.baseconv.test_equals
   :noindex:

.. autofunction:: biryani1.baseconv.test_not_none
   :noindex:

.. autofunction:: biryani1.baseconv.test_greater_or_equal
   :noindex:

.. autofunction:: biryani1.baseconv.test_in
   :noindex:

.. autofunction:: biryani1.baseconv.test_is
   :noindex:

.. autofunction:: biryani1.baseconv.test_isinstance
   :noindex:

.. autofunction:: biryani1.baseconv.test_less_or_equal
   :noindex:

.. autofunction:: biryani1.baseconv.test_none
   :noindex:

.. autofunction:: biryani1.baseconv.test_not_in
   :noindex:


Flow-Control Converters
=======================

.. autofunction:: biryani1.baseconv.condition
   :noindex:

.. autofunction:: biryani1.baseconv.first_match
   :noindex:

.. autofunction:: biryani1.baseconv.pipe
   :noindex:

.. autofunction:: biryani1.baseconv.switch
   :noindex:


Special Converters
==================

.. autofunction:: biryani1.baseconv.catch_error
   :noindex:

.. autofunction:: biryani1.baseconv.default
   :noindex:

.. autofunction:: biryani1.baseconv.fail
   :noindex:

.. autofunction:: biryani1.baseconv.function
   :noindex:

.. autofunction:: biryani1.baseconv.noop
   :noindex:

.. autofunction:: biryani1.baseconv.set_value
   :noindex:

.. autofunction:: biryani1.baseconv.translate
   :noindex:


Converters-related Utilities
============================

.. autofunction:: biryani1.baseconv.check
   :noindex:

.. autofunction:: biryani1.custom_conv
   :noindex:

.. autofunction:: biryani1.baseconv.ok
   :noindex:


String Functions
================

.. automodule:: biryani1.strings
   :members:
   :undoc-members:
   :noindex:


Extension Modules
=================

.. testsetup::

   from biryani1.babelconv import *
   from biryani1.base64conv import *
   from biryani1.bsonconv import *
   from biryani1.creditcardconv import *
   from biryani1.datetimeconv import *
   from biryani1.jsonconv import *
   from biryani1.jwkconv import *
   from biryani1.jwtconv import *
   from biryani1.netconv import *
   from biryani1.objectconv import *
   from biryani1.webobconv import *


Babel Converters
----------------

.. automodule:: biryani1.babelconv
   :members:
   :undoc-members:
   :noindex:


Base64 Converters
-----------------

.. automodule:: biryani1.base64conv
   :members:
   :undoc-members:
   :noindex:


BSON Converters
---------------

.. automodule:: biryani1.bsonconv
   :members:
   :undoc-members:
   :noindex:


Credit Card Converters
----------------------

.. automodule:: biryani1.creditcardconv
   :members:
   :undoc-members:
   :noindex:


Date & Time Converters
----------------------

.. automodule:: biryani1.datetimeconv
   :members:
   :undoc-members:
   :noindex:


JSON Converters
---------------

.. automodule:: biryani1.jsonconv
   :members:
   :undoc-members:
   :noindex:


JSON Web Keys (JWK) Converters
------------------------------

.. automodule:: biryani1.jwkconv
   :members:
   :undoc-members:
   :noindex:


JSON Web Tokens (JWK) Converters
--------------------------------

.. automodule:: biryani1.jwtconv
   :members:
   :undoc-members:
   :noindex:


Network Converters
------------------

.. automodule:: biryani1.netconv
   :members:
   :undoc-members:
   :noindex:


Object Converters
-----------------

.. automodule:: biryani1.objectconv
   :members:
   :undoc-members:
   :noindex:


WebOb Converters
----------------

.. automodule:: biryani1.webobconv
   :members:
   :undoc-members:
   :noindex:

