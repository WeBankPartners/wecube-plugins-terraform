# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.api.configer.region import RegionApi
from apps.api.configer.region import ZoneApi


class RegionConductor(object):
    def region_info(self, provider, region):
        '''

        :param provider:
        :param region:  region id
        :return:
        '''

        asset_id, data = RegionApi().region_asset(region)
        if provider != data["provider"]:
            raise ValueError("provider: %s 没有region：%s 注册信息，请先注册" % (provider, region))

        return asset_id

    def zone_info(self, provider, zone):
        '''

        :param provider:
        :param zone:  zone id
        :return:
        '''

        asset_id, data = ZoneApi().zone_asset(zone)
        if provider != data["provider"]:
            raise ValueError("provider: %s zone：%s 注册信息，请先注册" % (provider, zone))

        return asset_id

    def region_reverse_info(self, provider, region):
        '''

        :param provider:
        :param region: region asset id
        :return:
        '''

        return RegionApi().region_objectid(asset_id=region, provider=provider)

    def zone_reverse_info(self, provider, zone):
        '''

        :param provider:
        :param zone: zone asset id
        :return:
        '''

        return ZoneApi().zone_objectid(asset_id=zone, provider=provider)

    def zone_reverse_mapping(self, provider, region):
        '''

        :param provider:
        :param region: region id
        :return:
        '''

        return ZoneApi().zone_region_ids(region=region, provider=provider)
