# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

resouce_property_models = {
    "provider": ["secret_id", "secret_key", "region"],
    "vpc": ["name", "cider"],
    "subnet": ["cider", "name", "vpc_id", "zone"],
    "route_table": ["name", "vpc_id"],
    "route_entry": []
}


def property_necessary(resource_name, resource_property):
    if resource_name not in resouce_property_models.keys():
        return

    columns_property = resouce_property_models.get(resource_name)
    for column in columns_property:
        if column not in resource_property.keys():
            raise ValueError("缺少必要的property: %s" % column)
