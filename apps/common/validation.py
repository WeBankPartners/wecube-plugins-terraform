# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import re


def validate_column_line(column):
    if re.match(r'^[0-9a-zA-Z_.]{1,63}$', column):
        return True
    else:
        raise ValueError("不合法的值, 需满足: [0-9a-zA-Z_.]")

