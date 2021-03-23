# _ coding:utf-8 _*_

from django.conf.urls import include, url

import vpc_controller
import nat_controller
import eip_controller
import eip_association_controller
import ccn_controller
import ccn_attach_controller
import ccn_bandwidth_controller
import subnet_controller
import routetable_controller
import route_entry_controller
import security_group_controller

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
    url(r'^vpc$', vpc_controller.VPCController()),
    url(r'^vpc/(?P<rid>[\w-]+)$', vpc_controller.VPCIdController()),
    url(r'^backend/vpc/create$', vpc_controller.VPCAddController()),
    url(r'^backend/vpc/delete$', vpc_controller.VPCDeleteController()),
    url(r'^backend/vpc/source$', vpc_controller.VPCSourceController()),

    url(r'^subnet$', subnet_controller.SubnetController()),
    url(r'^subnet/(?P<rid>[\w-]+)$', subnet_controller.SubnetIdController()),
    url(r'^backend/subnet/create$', subnet_controller.SubnetAddController()),
    url(r'^backend/subnet/delete$', subnet_controller.SubnetDeleteController()),
    url(r'^backend/subnet/source$', subnet_controller.SubnetSourceController()),

    url(r'^route_table$', routetable_controller.RouteTableController()),
    url(r'^route_table/(?P<rid>[\w-]+)$', routetable_controller.RouteTableIdController()),
    url(r'^backend/route_table/create$', routetable_controller.RouteTableAddController()),
    url(r'^backend/route_table/delete$', routetable_controller.RouteTableDeleteController()),
    url(r'^backend/route_table/source$', routetable_controller.RouteTableSourceController()),

    url(r'^route_entry$', RouteEntryController()),
    url(r'^route_entry/(?P<rid>[\w-]+)$', RouteEntryIdController()),
    url(r'^backend/route_entry/create$', RouteEntryAddController()),
    url(r'^backend/route_entry/delete$', RouteEntryDeleteController()),

    url(r'^security_group$', SecGroupController()),
    url(r'^security_group/(?P<rid>[\w-]+)$', SecGroupIdController()),
    url(r'^backend/security_group/create$', SecGroupAddController()),
    url(r'^backend/security_group/delete$', SecGroupDeleteController()),
    url(r'^backend/security_group/source$', security_group_controller.SGSourceController()),

    url(r'^security_group_rule$', SecGroupRuleController()),
    url(r'^security_group_rule/(?P<rid>[\w-]+)$', SecGroupRuleIdController()),
    url(r'^backend/security_group_rule/create$', SecGroupRuleAddController()),
    url(r'^backend/security_group_rule/delete$', SecGroupRuleDeleteController()),

    url(r'^nat$', nat_controller.NatGatewayController()),
    url(r'^nat/(?P<rid>[\w-]+)$', nat_controller.NatGatewayIdController()),
    url(r'^backend/nat/create$', nat_controller.NatGatewayAddController()),
    url(r'^backend/nat/delete$', nat_controller.NatGatewayDeleteController()),
    url(r'^backend/nat/source$', nat_controller.NatSourceController()),

    url(r'^eip$', eip_controller.EipController()),
    url(r'^eip/(?P<rid>[\w-]+)$', eip_controller.EipIdController()),
    url(r'^backend/eip/create$', eip_controller.EipAddController()),
    url(r'^backend/eip/delete$', eip_controller.EipDeleteController()),
    url(r'^backend/eip/source$', eip_controller.EipSourceController()),

    url(r'^eip_association$', eip_association_controller.EipAssociationController()),
    url(r'^eip_association/(?P<rid>[\w-]+)$', eip_association_controller.EipAssociationIdController()),
    url(r'^backend/eip_association/create$', eip_association_controller.EipAssociationAddController()),
    url(r'^backend/eip_association/delete$', eip_association_controller.EipAssociationDeleteController()),

    url(r'^ccn$', ccn_controller.CCNController()),
    url(r'^ccn/(?P<rid>[\w-]+)$', ccn_controller.CCNIdController()),
    url(r'^backend/ccn/create$', ccn_controller.CCNAddController()),
    url(r'^backend/ccn/delete$', ccn_controller.CCNDeleteController()),
    url(r'^backend/ccn/source$', ccn_controller.CCNSourceController()),

    url(r'^ccn_attach$', ccn_attach_controller.CCNAttachController()),
    url(r'^ccn_attach/(?P<rid>[\w-]+)$', ccn_attach_controller.CCNAttachIdController()),
    url(r'^backend/ccn_attach/create$', ccn_attach_controller.CCNAttachAddController()),
    url(r'^backend/ccn_attach/delete$', ccn_attach_controller.CCNAttachDeleteController()),

    url(r'^ccn_bandwidth$', ccn_bandwidth_controller.CCNBandwidthController()),
    url(r'^ccn_bandwidth/(?P<rid>[\w-]+)$', ccn_bandwidth_controller.CCNBandwidthIdController()),
    url(r'^backend/ccn_bandwidth/create$', ccn_bandwidth_controller.CCNBandwidthAddController()),
    url(r'^backend/ccn_bandwidth/delete$', ccn_bandwidth_controller.CCNBandwidthDeleteController()),
]
