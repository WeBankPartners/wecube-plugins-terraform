# coding=utf8
from __future__ import (absolute_import, division, print_function, unicode_literals)

from uuid import uuid4


def get_uuid(upper=False, HYPHEN=False):
    '''
    :param upper:
    :param HYPHEN:
    :return:   32位的uuid
    '''
    uuid = str(uuid4())
    if not HYPHEN:
        uuid = uuid.replace('-', '')
    if upper:
        return uuid.upper()
    return uuid
