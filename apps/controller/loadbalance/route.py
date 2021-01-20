# _ coding:utf-8 _*_

from django.conf.urls import include, url
import lb_controller
import lb_attach_controller
import listener_controller

urlpatterns = [
    url(r'^lb$', lb_controller.LBController()),
    url(r'^lb/(?P<rid>[\w-]+)$', lb_controller.LBIdController()),
    url(r'^backend/lb/create$', lb_controller.LBAddController()),
    url(r'^backend/lb/delete$', lb_controller.LBDeleteController()),

    url(r'^lb_attach$', lb_attach_controller.LBAttachController()),
    url(r'^lb_attach/(?P<rid>[\w-]+)$', lb_attach_controller.LBAttachIdController()),
    url(r'^lb_attach/(?P<rid>[\w-]+)/(?P<instance>[\w-]+)$', lb_attach_controller.LBDetachController()),
    url(r'^backend/lb/attach$', lb_attach_controller.LBAttachAddController()),
    url(r'^backend/lb/detach$', lb_attach_controller.LBAttachDeleteController()),
    url(r'^backend/lb/detach/instance$', lb_attach_controller.LBDetachBackendController()),


]
