# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

from core import local_exceptions
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

    def provider_region_asset(self, provider, region_id):
        '''

        :param region_id:
        :return:
        '''

        client = RegionObject()
        data = client.query_one(where_data={"provider": provider, "id": region_id})
        if not data:
            data = client.query_one(where_data={"provider": provider, "name": region_id})
            if not data:
                data = client.query_one(where_data={"provider": provider, "asset_id": region_id})

        if not data:
            raise local_exceptions.ResourceValidateError("region", "region %s 未注册" % region_id)

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

    def zone_asset_data(self, zone_id):
        '''

        :param region_id:
        :return:
        '''

        data = ZoneObject().zone_object(zone_id)
        return data["asset_id"], data

    def provider_zone_object(self, provider, region, zone_id):
        '''

        :param provider:
        :param region:
        :param zone_id:
        :return:
        '''

        template = {"provider": provider}
        if region:
            template["region"] = region

        where_data = {"id": zone_id}
        where_data.update(template)
        data = ZoneObject().query_one(where_data=where_data)
        if not data:
            where_data = {"name": zone_id}
            where_data.update(template)
            data = ZoneObject().query_one(where_data=where_data)
            if not data:
                where_data = {"asset_id": zone_id}
                where_data.update(template)
                data = ZoneObject().query_one(where_data=where_data)

        if not data:
            raise local_exceptions.ResourceValidateError("zone", "zone %s 未注册" % zone_id)

        return data["asset_id"], data

    def zone_objectid(self, asset_id, provider=None):
        '''

        :param asset_id:
        :param provider:
        :return:
        '''

        data = ZoneObject().zone_asset(asset_id, provider)
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

    def region_zones(self, region, provider=None):
        '''

        :param region:
        :param provider:
        :return:
        '''

        where_data = {"region": region}
        # if provider:
        #     where_data["provider"] = region

        count, data = ZoneObject().list(filters=where_data)
        mapping = []

        for x_data in data:
            mapping.append(x_data["id"])
            mapping.append(x_data["asset_id"])

        return mapping
