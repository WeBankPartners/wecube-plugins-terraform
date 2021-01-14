# coding: utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.background.resource.vm.instance_type import InstanceTypeObject


class InstanceTypeApi(object):
    def __init__(self):
        self.resource_object = InstanceTypeObject()
