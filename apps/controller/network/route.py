# _ coding:utf-8 _*_

from django.conf.urls import include, url
from vpc_controller import VPCController
from vpc_controller import VPCAddController
from vpc_controller import VPCIdController
from vpc_controller import VPCDeleteController

from subnet_controller import SubnetController
from subnet_controller import SubnetAddController
from subnet_controller import SubnetIdController
from subnet_controller import SubnetDeleteController

from routetable_controller import RouteTableController
from routetable_controller import RouteTableIdController
from routetable_controller import RouteTableAddController
from routetable_controller import RouteTableDeleteController

from route_entry_controller import RouteEntryController
from route_entry_controller import RouteEntryIdController
from route_entry_controller import RouteEntryAddController
from route_entry_controller import RouteEntryDeleteController

urlpatterns = [
    url(r'^vpc$', VPCController()),
    url(r'^vpc/(?P<rid>[\w-]+)$', VPCIdController()),
    url(r'^backend/vpc/create$', VPCAddController()),
    url(r'^backend/vpc/delete$', VPCDeleteController()),

    url(r'^subnet$', SubnetController()),
    url(r'^subnet/(?P<rid>[\w-]+)$', SubnetIdController()),
    url(r'^backend/subnet/create$', SubnetAddController()),
    url(r'^backend/subnet/delete$', SubnetDeleteController()),

    url(r'^route_table$', RouteTableController()),
    url(r'^route_table/(?P<rid>[\w-]+)$', RouteTableIdController()),
    url(r'^backend/route_table/create$', RouteTableAddController()),
    url(r'^backend/route_table/delete$', RouteTableDeleteController()),

    url(r'^route_entry$', RouteEntryController()),
    url(r'^route_entry/(?P<rid>[\w-]+)$', RouteEntryIdController()),
    url(r'^backend/route_entry/create$', RouteEntryAddController()),
    url(r'^backend/route_entry/delete$', RouteEntryDeleteController()),
]
