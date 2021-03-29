# _ coding:utf-8 _*_

from django.conf.urls import include, url
import lb_controller
import lb_attach_controller
import listener_controller

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

    url(r'^lb_attach$', lb_attach_controller.LBAttachController()),
    url(r'^lb_attach/(?P<rid>[\w-]+)$', lb_attach_controller.LBAttachIdController()),
    url(r'^lb_attach/(?P<rid>[\w-]+)/(?P<instance>[\w-]+)$', lb_attach_controller.LBDetachController()),
    url(r'^backend/lb_attach/apply$', lb_attach_controller.LBAttachAddController()),
    url(r'^backend/lb_attach/destroy$', lb_attach_controller.LBAttachDeleteController()),

]
