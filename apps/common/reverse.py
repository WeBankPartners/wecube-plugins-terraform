# -*- coding: utf-8 -*-

import json


class Reverse(object):
    @classmethod
    def reverse_json(cls, data):
        res = {}
        for key, value in data.items():
            res[value] = key

        return res

