*****************************
For *Biryani* maintainer only
*****************************


How to release a new version of *Biryani*
==========================================

#. Extract strings to translate from source code and update catalog (aka ``.po`` files) from biryani/i18n/biryani.pot``::

    make update-i18n

#. Ensure that Project-Id-Version in ``biryani/i18n/biryani.pot`` and ``.po`` files are correct.

#. Send source file and translations to *Transifex*::

    tx push -s

#. Add missing translations using *Transifex*.

#. Get *Transifex* translations::

    tx pull

#. Compile catalog::

    ./setup.py compile_catalog

#. Execute doctests and check that the build succeeded without error nor warning::

    ./setup.py build_sphinx -b doctest

#. Build the HTML documentation and check that the build succeeded without error nor warning::

    ./setup.py build_sphinx -b html

#. Launch the documentation coverage tests::

    ./setup.py build_sphinx -b coverage

   Then check that ``docs/build/coverage/python.txt`` doesn't list non documented functions.

#. Update ``changelog.rst`` using ``git log``.

#. Edit ``setup.py`` to change version number (ie remove "dev" suffix)::

    version = 'NEW_RELEASE_NUMBER',

#. Also check that everything is OK: classifiers, keywords, requirements.

#. Edit ``docs/source/conf.py`` to change version number in two lines::

    # The short X.Y version.
    version = 'NEW_MINOR_NUMBER'
    # The full version, including alpha/beta/rc tags.
    release = 'NEW_RELEASE_NUMBER'

#. Re-build the HTML documentation and check that the build succeeded without error nor warning::

    ./setup.py build_sphinx -b html

#. Commit changes.

#. Tag the new release and upload it to Gitorious::

    git tag NEW_RELEASE_NUMBER
    git push gitorious NEW_RELEASE_NUMBER

#. Build and upload the package to Pypi::

    ./setup.py upload_sphinx
    ./setup.py sdist
    ./setup.py register

#. Announce the new release.

#. Edit ``setup.py`` to change version number (ie increase minor and add "dev" suffix)::

    version = 'NEW_FUTURE_RELEASE_NUMBERdev',

#. Edit ``docs/source/conf.py`` to change version number in two lines::

    # The short X.Y version.
    version = 'NEW_FUTURE_MINOR_NUMBER'
    # The full version, including alpha/beta/rc tags.
    release = 'NEW_FUTURE_RELEASE_NUMBERdev'
