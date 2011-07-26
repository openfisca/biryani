# -*- coding: utf-8 -*-


# Biryani -- A conversion and validation toolbox
# By: Emmanuel Raviart <eraviart@easter-eggs.com>
#
# Copyright (C) 2009, 2010, 2011 Easter-eggs
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


"""All Conversion Functions"""


from baseconv import *

try:
    import babel
except ImportError:
    from babelconv import *
else:
    # Don't export babel module.
    del babel

try:
    import bson
except ImportError:
    from bsonconv import *
else:
    # Don't export bson module.
    del bson

try:
    import mx.DateTime, pytz
except ImportError:
    from datetimeconv import *
else:
    # Don't export modules.
    del mx
    del pytz

try:
    import pymongo
except ImportError:
    from pymongoconv import *
else:
    # Don't export pymongo module.
    del pymongo

try:
    from suq import strings
except ImportError:
    from suqstringsconv import *
else:
    # Don't export strings module.
    del strings

