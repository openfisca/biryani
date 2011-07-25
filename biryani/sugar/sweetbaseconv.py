# -*- coding: utf-8 -*-


# Biryani -- A conversion and validation toolbox
# By: Emmanuel Raviart <eraviart@easter-eggs.com>
#
# Copyright (C) 2009, 2010, 2011 Easter-eggs
# http://packages.python.org/biryani/
#
# This file is part of Biryani.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Experimental or Non Standard Converters

Since these converters may change at any time, don't import this module, but copy and paste the functions you need in
your application.
"""


from .. import baseconv as conv


N_ = conv.N_


def attribute(name):
    """Return a converter that retrieves an existing attribute from an object.

    This converter is non-standard, because:

      * It is a simple one-liner.
      * It needs an option to specify what to do when attribute doesn't exist.
    """
    return conv.function(lambda value: getattr(value, name))

