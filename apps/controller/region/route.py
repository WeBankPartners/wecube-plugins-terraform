# _ coding:utf-8 _*_

from django.conf.urls import include, url
import region_controller
import az_controller

urlpatterns = [
    url(r'^region$', region_controller.RegionController()),
    url(r'^region/(?P<rid>[\w-]+)$', region_controller.RegionIdController()),
    url(r'^backend/region/apply$', region_controller.RegionAddController()),
    url(r'^backend/region/destroy$', region_controller.RegionDeleteController()),
    url(r'^backend/region/source$', region_controller.RegionSourceController()),

    url(r'^zone$', az_controller.ZoneController()),
    url(r'^zone/(?P<rid>[\w-]+)$', az_controller.ZoneIdController()),
    url(r'^backend/zone/apply$', az_controller.ZoneAddController()),
    url(r'^backend/zone/destroy$', az_controller.ZoneDeleteController()),
    url(r'^backend/zone/source$', az_controller.ZoneSourceController()),
]
