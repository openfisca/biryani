*******************
*Biryani* Changelog
*******************


Next Release (Biryani 1.0)
===========================

* :func:`biryani.custom_conv` now accepts modules instead of modules names.

* Mapping conversions now preserve order when used with OrderedDict.

* Add parameter ``handle_none_value`` to func:`biryani.baseconv.new_mapping`, func:`biryani.baseconv.new_sequence` &
   func:`biryani.baseconv.new_struct`.

* Rename parameter ``set_none_value`` to ``handle_none_value`` in func:`biryani.baseconv.set_value`.


Remove implicit actions from converters
---------------------------------------

* Empty collections are no more replaced with ``None`` and parameter ``keep_empty`` is removed from:

  * :func:`biryani.baseconv.new_mapping`

  * :func:`biryani.baseconv.new_sequence`

  * :func:`biryani.baseconv.new_struct`

  * :func:`biryani.baseconv.struct`

  * :func:`biryani.baseconv.structured_mapping`

  * :func:`biryani.baseconv.structured_sequence`

  * :func:`biryani.baseconv.uniform_mapping`

  * :func:`biryani.baseconv.uniform_sequence`

* Replace parameter ``keep_none_items`` with inverse parameter ``drop_none_items`` in:

  * :func:`biryani.baseconv.item_or_sequence`

  * :func:`biryani.baseconv.structured_sequence`

* Replace parameter ``keep_none_keys`` with inverse parameter ``drop_none_keys`` in
  :func:`biryani.baseconv.uniform_mapping`.

* Replace parameter ``keep_none_values`` with inverse parameter ``drop_none_values`` in:

  * :func:`biryani.baseconv.struct`

  * :func:`biryani.baseconv.structured_mapping`

  * :func:`biryani.baseconv.uniform_mapping`

* Parameter ``add_prefix`` of :func:`biryani.baseconv.make_input_to_url` and :func:`biryani.baseconv.make_input_to_url`
  is now ``None`` by default, instead of ``"http://"``.


Biryani 0.10.0
==============

* Rename package to ``biryani``.


Biryani 0.9
===========

TODO


Biryani 0.8
===========

* Rework boolean converters. New :func:`biryani.baseconv.guess_bool` converter. Remove ``form_data_to_bool`` converter.

* Rename converter ``require`` to :func:`biryani.baseconv.not_none`.

    This new name is more consistent with other ``test_...`` converters.
    It is also more clear when used in a condition test. For example::

        conv.condition(
           conv.not_none,
           conv.set_value('Value exists'),
           conv.set_value('Value is missing'),
           )

* New :func:`biryani.baseconv.struct` converter that replaces both :func:`biryani.baseconv.structured_mapping` & :func:`biryani.baseconv.structured_sequence` converter.

* Replace ``mapping`` and "sequence`` converters with :func:`biryani.baseconv.new_struct` (and :func:`biryani.baseconv.new_mapping` and :func:`biryani.baseconv.new_sequence`).

* Add :func:`biryani.baseconv.get` converter.

* New :func:`biryani.baseconv.input_to_url_path_and_query` converter.

* Rename parameters ``keep_null_items`` & ``keep_null_keys`` used by mappings or sequences converters to ``keep_none_items`` & ``keep_none_keys``.

* Add optional state to :func:`biryani.baseconv.function` and :func:`biryani.baseconv.test` converters.

* Rename ``handle_none`` parameter of  :func:`biryani.baseconv.function` and :func:`biryani.baseconv.test` converters to ``handle_none_value``.

* Rename function ``to_value`` to :func:`biryani.baseconv.check` and extend it to accept either a converter or a conversion result as argument.

* New function :func:`biryani.custom_conv` to import only needed conversion modules.

* Function :func:`biryani.strings.slugify` now always returns unicode.

* Rename ``dict_to_instance`` converter to :func:`biryani.objectconv.dict_to_object` and move it to module :mod:`biryani.objectconv`.

* Remove converters in :mod:`biryani.objectconv` that were duplicates of :mod:`biryani.datetimeconv`.

* New module :mod:`biryani.creditcardconv`.

* Remove module ``pymongoconv``.

    This module was related to *Monpyjama* instead of *pymongo* and its converters are no more used.

* Rename module ``sugar.sweetbaseconv`` to :mod:`biryani.nonstandard.deprecatedbaseconv`.

* New experimental converter :func:`biryani.nonstandard.experimentalbaseconv.mapping_replace_sequence`.

* Add internationalization support and French localization.

* Complete documentation and tests.


Biryani 0.7
===========

*No changelog till 0.7 release.*
