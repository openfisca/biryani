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

