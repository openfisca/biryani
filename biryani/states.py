# -*- coding: utf-8 -*-


# Biryani -- A conversion and validation toolbox
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015 Emmanuel Raviart
# http://packages.python.org/Biryani/
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


"""Contexts used by converters"""


class State(object):
    _ = staticmethod(lambda message: message)

    def __repr__(self):
        """Hack to improve ``default_state`` aspect in Sphinx autodoc

        A state doesn't not need to implement this method.
        """
        if self is default_state:
            return '{0}.default_state'.format(__name__)
        else:
            return super(State, self).__repr__()


#: Minimal context, usable with converters
default_state = State()
