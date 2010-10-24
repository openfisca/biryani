#! /usr/bin/env python
# -*- coding: utf-8 -*-


# Suq -- Python Toolbox
# By: Emmanuel Raviart <eraviart@easter-eggs.com>
#
# Copyright (C) 2009, 2010 Easter-eggs
# http://wiki.infos-pratiques.org/wiki/Suq
#
# This file is part of Suq.
#
# Suq is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Suq is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Toolbox to convert and validate values (for web forms, etc)"""


try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


classifiers = """\
Development Status :: 3 - Alpha
Environment :: Web Environment
Intended Audience :: Information Technology
License :: OSI Approved :: GNU Affero General Public License v3
Operating System :: OS Independent
Programming Language :: Python
"""

doc_lines = __doc__.split('\n')


setup(
    name = 'Suq-Conversion',
    version = '0.1',

    author = 'Emmanuel Raviart',
    author_email = 'eraviart@easter-eggs.com',
    classifiers = [classifier for classifier in classifiers.split('\n') if classifier],
    description = doc_lines[0],
    keywords = 'conversion form python validation web',
    license = 'http://www.fsf.org/licensing/licenses/agpl-3.0.html',
    long_description = '\n'.join(doc_lines[2:]),
    url = 'http://wiki.infos-pratiques.org/wiki/Suq',

    install_requires = [],
    namespace_packages = ['suq'],
    packages = find_packages(exclude = ['ez_setup']),
    zip_safe = False,
    )
