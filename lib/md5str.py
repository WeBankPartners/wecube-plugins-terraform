# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import hashlib


def Md5str(string):
    _data = hashlib.md5()
    _data.update(string.encode("utf-8"))
    return _data.hexdigest()
