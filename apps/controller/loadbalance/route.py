# _ coding:utf-8 _*_

from django.conf.urls import include, url
import lb_controller
import lb_attach_controller
import listener_controller
import server_group_controller
import lb_rule_controller

urlpatterns = [
    url(r'^lb$', lb_controller.LBController()),
    url(r'^lb/(?P<rid>[\w-]+)$', lb_controller.LBIdController()),
    url(r'^backend/lb/apply$', lb_controller.LBAddController()),
    url(r'^backend/lb/destroy$', lb_controller.LBDeleteController()),
    url(r'^backend/lb/source$', lb_controller.LBSourceController()),

    url(r'^lb_listener$', listener_controller.LBListenerController()),
    url(r'^lb_listener/(?P<rid>[\w-]+)$', listener_controller.LBListenerIdController()),
    url(r'^backend/lb_listener/apply$', listener_controller.LBListenerAddController()),
    url(r'^backend/lb_listener/destroy$', listener_controller.LBListenerDeleteController()),
    url(r'^backend/lb_listener/source$', listener_controller.LBListenerSourceController()),

    url(r'^lb_attach$', lb_attach_controller.LBAttachController()),
    url(r'^lb_attach/(?P<rid>[\w-]+)$', lb_attach_controller.LBAttachIdController()),
    url(r'^lb_attach/(?P<rid>[\w-]+)/(?P<instance>[\w-]+)$', lb_attach_controller.LBDetachController()),
    url(r'^backend/lb_attach/apply$', lb_attach_controller.LBAttachAddController()),
    url(r'^backend/lb_attach/destroy$', lb_attach_controller.LBAttachDeleteController()),
    url(r'^backend/lb_attach/source$', lb_attach_controller.LBAttachSourceController()),

    url(r'^lb_rule$', lb_rule_controller.LBRuleController()),
    url(r'^lb_rule/(?P<rid>[\w-]+)$', lb_rule_controller.LBRuleIdController()),
    url(r'^backend/lb_rule/apply$', lb_rule_controller.LBRuleAddController()),
    url(r'^backend/lb_rule/destroy$', lb_rule_controller.LBRuleDeleteController()),
    url(r'^backend/lb_rule/source$', lb_rule_controller.LBRuleSourceController()),

    url(r'^lb_server_group$', server_group_controller.LBGroupController()),
    url(r'^lb_server_group/(?P<rid>[\w-]+)$', server_group_controller.LBGroupIdController()),
    url(r'^backend/lb_server_group/apply$', server_group_controller.LBGroupAddController()),
    url(r'^backend/lb_server_group/destroy$', server_group_controller.LBGroupDeleteController()),
    url(r'^backend/lb_server_group/source$', server_group_controller.LBGroupSourceController()),
]
