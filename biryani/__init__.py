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


"""Biryani package

This root module is kept nearly empty to allow client applications to import only the converters they need, module by
module.
"""


__all__ = ['custom_conv']


class CustomConv(object):
    """Class for module-like objects that contains the content of selected conversion modules"""
    pass


def custom_conv(*modules):
    """Import given conversion modules and return a module-like object containing their aggregated content.

    How to use::

        import biryani
        import biryani.baseconv
        import biryani.datetimeconv
        import any.custom.module
        conv = biryani.custom_conv(biryani.baseconv, biryani.datetimeconv, any.custom.module)

    >>> import biryani.baseconv
    >>> import biryani.datetimeconv
    >>> conv = custom_conv(biryani.baseconv, biryani.datetimeconv)
    >>> conv.input_to_int(u'42') # input_to_int is defined in baseconv module.
    (42, None)
    >>> conv.iso8601_input_to_date(u'1789-07-14') # iso8601_input_to_date is defined in datetimeconv module.
    (datetime.date(1789, 7, 14), None)
    """

    conv = CustomConv()
    for module in modules:
        module_public_keys = getattr(module, '__all__', None)
        if module_public_keys is None:
            conv.__dict__.update(module.__dict__)
        else:
            for key in module_public_keys:
                setattr(conv, key, getattr(module, key))
    return conv
