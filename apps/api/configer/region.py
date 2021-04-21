# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.background.resource.configr.region import RegionObject
from apps.background.resource.configr.region import ZoneObject


class RegionApi(object):
    def region_asset(self, region_id):
        '''

        :param region_id:
        :return:
        '''

        data = RegionObject().region_object(region_id)
        return data["asset_id"], data

    def region_objectid(self, asset_id, provider=None):
        '''

        :param asset_id:
        :param provider:
        :return:
        '''

        data = RegionObject().region_asset_object(asset_id, provider)
        if data:
            return data["id"]
        return asset_id


class ZoneApi(object):
    def zone_asset(self, zone_id):
        '''

        :param region_id:
        :return:
        '''

        data = ZoneObject().zone_object(zone_id)
        return data["asset_id"]

    def zone_objectid(self, asset_id, provider=None):
        '''

        :param asset_id:
        :param provider:
        :return:
        '''

        data = ZoneObject().zone_asset_object(asset_id, provider)
        if data:
            return data["id"]

        return asset_id

    def zone_region_ids(self, region, provider=None):
        '''

        :param region:
        :param provider:
        :return:
        '''

        where_data = {"region": region}
        if provider:
            where_data["provider"] = region

        count, data = ZoneObject().list(filters=where_data)
        mapping = {}

        for x_data in data:
            asset_id = x_data["asset_id"]
            mapping[asset_id] = x_data["id"]

        return mapping

