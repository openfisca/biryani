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


"""All Conversion Functions, except language specific ones"""


from baseconv import *

try:
    import babel
except ImportError:
    pass
else:
    # Don't export babel module.
    del babel
    from babelconv import *

try:
    import bson
except ImportError:
    pass
else:
    # Don't export bson module.
    del bson
    from bsonconv import *

try:
    import mx.DateTime, pytz
except ImportError:
    pass
else:
    # Don't export modules.
    del mx
    del pytz
    from datetimeconv import *

try:
    import pymongo
except ImportError:
    pass
else:
    # Don't export pymongo module.
    del pymongo
    from pymongoconv import *

