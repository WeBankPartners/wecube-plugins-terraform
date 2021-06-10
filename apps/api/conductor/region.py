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

    def provider_region_info(self, provider, region):
        '''

        :param provider:
        :param region:  region id
        :return:
        '''

        asset_id, data = RegionApi().provider_region_asset(provider, region)
        # if provider != data["provider"]:
        #     raise ValueError("provider: %s 没有region：%s 注册信息，请先注册" % (provider, region))

        return asset_id, data

    def zone_info(self, provider, zone):
        '''

        :param provider:
        :param zone:  zone id
        :return:
        '''

        asset_id, data = ZoneApi().zone_asset_data(zone)
        if provider != data["provider"]:
            raise ValueError("provider: %s zone：%s 注册信息，请先注册" % (provider, zone))

        return asset_id

    def provider_zone_info(self, provider, region, zone):
        '''

        :param provider:
        :param zone:  zone id
        :return:
        '''

        asset_id, data = ZoneApi().provider_zone_object(provider=provider, region=region, zone_id=zone)
        return asset_id, data

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

    def zone_asset(self, provider, zone_id):
        '''

        :param provider:
        :param zone: zone asset id
        :return:
        '''

        return ZoneApi().zone_asset(zone_id=zone_id)

    def zone_reverse_mapping(self, provider, region):
        '''

        :param provider:
        :param region: region id
        :return:
        '''

        return ZoneApi().zone_region_ids(region=region, provider=provider)
