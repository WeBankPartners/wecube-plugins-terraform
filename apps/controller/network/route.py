# _ coding:utf-8 _*_

from django.conf.urls import include, url

import nat_controller
import eip_controller
import eip_association_controller
import ccn_controller
import ccn_attach_controller
import ccn_bandwidth_controller

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

from security_group_controller import SecGroupController
from security_group_controller import SecGroupIdController
from security_group_controller import SecGroupAddController
from security_group_controller import SecGroupDeleteController

from security_group_rule_controller import SecGroupRuleController
from security_group_rule_controller import SecGroupRuleIdController
from security_group_rule_controller import SecGroupRuleAddController
from security_group_rule_controller import SecGroupRuleDeleteController

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

    url(r'^security_group$', SecGroupController()),
    url(r'^security_group/(?P<rid>[\w-]+)$', SecGroupIdController()),
    url(r'^backend/security_group/create$', SecGroupAddController()),
    url(r'^backend/security_group/delete$', SecGroupDeleteController()),

    url(r'^security_group_rule$', SecGroupRuleController()),
    url(r'^security_group_rule/(?P<rid>[\w-]+)$', SecGroupRuleIdController()),
    url(r'^backend/security_group_rule/create$', SecGroupRuleAddController()),
    url(r'^backend/security_group_rule/delete$', SecGroupRuleDeleteController()),

    url(r'^nat$', nat_controller.NatGatewayController()),
    url(r'^nat/(?P<rid>[\w-]+)$', nat_controller.NatGatewayIdController()),
    url(r'^backend/nat/create$', nat_controller.NatGatewayAddController()),
    url(r'^backend/nat/delete$', nat_controller.NatGatewayDeleteController()),

    url(r'^eip$', eip_controller.EipController()),
    url(r'^eip/(?P<rid>[\w-]+)$', eip_controller.EipIdController()),
    url(r'^backend/eip/create$', eip_controller.EipAddController()),
    url(r'^backend/eip/delete$', eip_controller.EipDeleteController()),

    url(r'^eip_association$', eip_association_controller.EipAssociationController()),
    url(r'^eip_association/(?P<rid>[\w-]+)$', eip_association_controller.EipAssociationIdController()),
    url(r'^backend/eip_association/create$', eip_association_controller.EipAssociationAddController()),
    url(r'^backend/eip_association/delete$', eip_association_controller.EipAssociationDeleteController()),

    url(r'^ccn$', ccn_controller.CCNController()),
    url(r'^ccn/(?P<rid>[\w-]+)$', ccn_controller.CCNIdController()),
    url(r'^backend/ccn/create$', ccn_controller.CCNAddController()),
    url(r'^backend/ccn/delete$', ccn_controller.CCNDeleteController()),

    url(r'^ccn_attach$', ccn_attach_controller.CCNAttachController()),
    url(r'^ccn_attach/(?P<rid>[\w-]+)$', ccn_attach_controller.CCNAttachIdController()),
    url(r'^backend/ccn_attach/create$', ccn_attach_controller.CCNAttachAddController()),
    url(r'^backend/ccn_attach/delete$', ccn_attach_controller.CCNAttachDeleteController()),

    url(r'^ccn_bandwidth$', ccn_bandwidth_controller.CCNBandwidthController()),
    url(r'^ccn_bandwidth/(?P<rid>[\w-]+)$', ccn_bandwidth_controller.CCNBandwidthIdController()),
    url(r'^backend/ccn_bandwidth/create$', ccn_bandwidth_controller.CCNBandwidthAddController()),
    url(r'^backend/ccn_bandwidth/delete$', ccn_bandwidth_controller.CCNBandwidthDeleteController()),
]
