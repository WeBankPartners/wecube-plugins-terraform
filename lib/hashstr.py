# coding:utf-8

import hashlib


def hash256str(str):
    return hashlib.sha256(str).hexdigest()

