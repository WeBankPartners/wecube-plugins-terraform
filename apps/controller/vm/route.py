# _ coding:utf-8 _*_

from django.conf.urls import include, url
import instance_controller
import instance_type_controller
import eni_controller
import eni_attach_controller

urlpatterns = [
    url(r'^instance$', instance_controller.InstanceController()),
    url(r'^instance/(?P<rid>[\w-]+)$', instance_controller.InstanceIdController()),
    url(r'^instance_action/(?P<rid>[\w-]+)$', instance_controller.InstanceActionController()),
    url(r'^backend/instance/create$', instance_controller.InstanceAddController()),
    url(r'^backend/instance/delete$', instance_controller.InstanceDeleteController()),
    url(r'^backend/instance/update$', instance_controller.InstanceUpdateController()),
    url(r'^backend/instance/action$', instance_controller.InstanceStartController()),
    url(r'^backend/instance/source$', instance_controller.InstanceSourceController()),

    url(r'^instance_type$', instance_type_controller.InstanceTypeController()),
    url(r'^instance_type/(?P<rid>[\w-]+)$', instance_type_controller.InstanceTypeIdController()),

    url(r'^network_interface$', eni_controller.EniController()),
    url(r'^network_interface/(?P<rid>[\w-]+)$', eni_controller.EniIdController()),
    url(r'^backend/network_interface/create$', eni_controller.EniAddController()),
    url(r'^backend/network_interface/delete$', eni_controller.EniDeleteController()),
    url(r'^backend/network_interface/source$', eni_controller.ENISourceController()),

    url(r'^network_interface_attach$', eni_attach_controller.EniAttachController()),
    url(r'^network_interface_attach/(?P<rid>[\w-]+)$', eni_attach_controller.EniAttachIdController()),
    url(r'^backend/network_interface/attach$', eni_attach_controller.EniAttachAddController()),
    url(r'^backend/network_interface/detach$', eni_attach_controller.EniDetachController()),

]
