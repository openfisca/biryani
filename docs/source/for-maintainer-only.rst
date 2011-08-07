*****************************
For *Biryani* maintainer only
*****************************


How to release a new version of *Biryani*
=========================================

#. Edit ``setup.py`` to change version number (ie remove "dev" suffix)::

    version = 'NEW_RELEASE_NUMBER',

#. Edit ``docs/source/conf.py`` to change version number in two lines::

    # The short X.Y version.
    version = 'NEW_MINOR_NUMBER'
    # The full version, including alpha/beta/rc tags.
    release = 'NEW_RELEASE_NUMBER'

#. TODO: Update the localizations and ensure that they are uptodate.

#. Execute doctests and check that the build succeeded without error nor warning::

    ./setup.py build_sphinx -b doctest

#. Build the HTML documentation and check that the build succeeded without error nor warning::

    ./setup.py build_sphinx -b html

#. Launch the documentation coverage tests::

    ./setup.py build_sphinx -b coverage

   Then check that ``docs/build/coverage/python.txt`` doesnt list non documented functions.

#. Tag the new release and upload it to Gitorious::

    git tag NEW_RELEASE_NUMBER
    git push gitorious NEW_RELEASE_NUMBER

#. Build and upload the package to Pypi::

    ./setup.py sdist
    ./setup.py register

#. Announce the new release.

#. Edit ``setup.py`` to change version number (ie increase minor and add "dev" suffix)::

    version = 'NEW_FUTURE_RELEASE_NUMBERdev',

#. Edit ``docs/source/conf.py`` to change version number in two lines::

    # The short X.Y version.
    version = 'NEW_FUTURE_MINOR_NUMBERdev'
    # The full version, including alpha/beta/rc tags.
    release = 'NEW_FUTURE_RELEASE_NUMBERdev'

