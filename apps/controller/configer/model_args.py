# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

resouce_property_models = {
    "vpc": ["name", "cider"],
    "subnet": []
}


def property_necessary(resource_name, resource_property):
    if resource_name not in resource_property:
        return

    columns_property = resouce_property_models.get(resource_name)
    for column in columns_property:
        if column not in resource_property:
            raise ValueError("缺少必要的property: %s" % column)
