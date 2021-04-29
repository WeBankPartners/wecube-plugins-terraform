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
import peer_connection_controller

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
    url(r'^backend/vpc/apply$', vpc_controller.VPCAddController()),
    url(r'^backend/vpc/destroy$', vpc_controller.VPCDeleteController()),
    url(r'^backend/vpc/source$', vpc_controller.VPCSourceController()),

    url(r'^subnet$', subnet_controller.SubnetController()),
    url(r'^subnet/(?P<rid>[\w-]+)$', subnet_controller.SubnetIdController()),
    url(r'^backend/subnet/apply$', subnet_controller.SubnetAddController()),
    url(r'^backend/subnet/destroy$', subnet_controller.SubnetDeleteController()),
    url(r'^backend/subnet/source$', subnet_controller.SubnetSourceController()),

    url(r'^route_table$', routetable_controller.RouteTableController()),
    url(r'^route_table/(?P<rid>[\w-]+)$', routetable_controller.RouteTableIdController()),
    url(r'^backend/route_table/apply$', routetable_controller.RouteTableAddController()),
    url(r'^backend/route_table/destroy$', routetable_controller.RouteTableDeleteController()),
    url(r'^backend/route_table/source$', routetable_controller.RouteTableSourceController()),

    url(r'^route_entry$', RouteEntryController()),
    url(r'^route_entry/(?P<rid>[\w-]+)$', RouteEntryIdController()),
    url(r'^backend/route_entry/apply$', RouteEntryAddController()),
    url(r'^backend/route_entry/destroy$', RouteEntryDeleteController()),
    url(r'^backend/route_entry/source$', route_entry_controller.RTRuleSourceController()),

    url(r'^security_group$', SecGroupController()),
    url(r'^security_group/(?P<rid>[\w-]+)$', SecGroupIdController()),
    url(r'^backend/security_group/apply$', SecGroupAddController()),
    url(r'^backend/security_group/destroy$', SecGroupDeleteController()),
    url(r'^backend/security_group/source$', security_group_controller.SGSourceController()),

    url(r'^security_group_rule$', SecGroupRuleController()),
    url(r'^security_group_rule/(?P<rid>[\w-]+)$', SecGroupRuleIdController()),
    url(r'^backend/security_group_rule/apply$', SecGroupRuleAddController()),
    url(r'^backend/security_group_rule/destroy$', SecGroupRuleDeleteController()),

    url(r'^nat$', nat_controller.NatGatewayController()),
    url(r'^nat/(?P<rid>[\w-]+)$', nat_controller.NatGatewayIdController()),
    url(r'^backend/nat/apply$', nat_controller.NatGatewayAddController()),
    url(r'^backend/nat/destroy$', nat_controller.NatGatewayDeleteController()),
    url(r'^backend/nat/source$', nat_controller.NatSourceController()),

    url(r'^eip$', eip_controller.EipController()),
    url(r'^eip/(?P<rid>[\w-]+)$', eip_controller.EipIdController()),
    url(r'^backend/eip/apply$', eip_controller.EipAddController()),
    url(r'^backend/eip/destroy$', eip_controller.EipDeleteController()),
    url(r'^backend/eip/source$', eip_controller.EipSourceController()),

    url(r'^eip_association$', eip_association_controller.EipAssociationController()),
    url(r'^eip_association/(?P<rid>[\w-]+)$', eip_association_controller.EipAssociationIdController()),
    url(r'^backend/eip_association/apply$', eip_association_controller.EipAssociationAddController()),
    url(r'^backend/eip_association/destroy$', eip_association_controller.EipAssociationDeleteController()),

    url(r'^ccn$', ccn_controller.CCNController()),
    url(r'^ccn/(?P<rid>[\w-]+)$', ccn_controller.CCNIdController()),
    url(r'^backend/ccn/apply$', ccn_controller.CCNAddController()),
    url(r'^backend/ccn/destroy$', ccn_controller.CCNDeleteController()),
    url(r'^backend/ccn/source$', ccn_controller.CCNSourceController()),

    url(r'^ccn_attach$', ccn_attach_controller.CCNAttachController()),
    url(r'^ccn_attach/(?P<rid>[\w-]+)$', ccn_attach_controller.CCNAttachIdController()),
    url(r'^backend/ccn_attach/apply$', ccn_attach_controller.CCNAttachAddController()),
    url(r'^backend/ccn_attach/destroy$', ccn_attach_controller.CCNAttachDeleteController()),

    url(r'^ccn_bandwidth$', ccn_bandwidth_controller.CCNBandwidthController()),
    url(r'^ccn_bandwidth/(?P<rid>[\w-]+)$', ccn_bandwidth_controller.CCNBandwidthIdController()),
    url(r'^backend/ccn_bandwidth/apply$', ccn_bandwidth_controller.CCNBandwidthAddController()),
    url(r'^backend/ccn_bandwidth/destroy$', ccn_bandwidth_controller.CCNBandwidthDeleteController()),

    url(r'^peer_connection$', peer_connection_controller.PeerConnController()),
    url(r'^peer_connection/(?P<rid>[\w-]+)$', peer_connection_controller.PeerConnIdController()),
    url(r'^backend/peer_connection/apply$', peer_connection_controller.PeerConnAddController()),
    url(r'^backend/peer_connection/destroy$', peer_connection_controller.PeerConnDeleteController()),
    url(r'^backend/peer_connection/source$', peer_connection_controller.PeerConnSourceController()),
]
