# _ coding:utf-8 _*_

from django.conf.urls import include, url
import instance_controller
import instance_type_controller

urlpatterns = [
    url(r'^instance$', instance_controller.InstanceController()),
    url(r'^instance/(?P<rid>[\w-]+)$', instance_controller.InstanceIdController()),
    url(r'^instance_action/(?P<rid>[\w-]+)$', instance_controller.InstanceActionController()),
    url(r'^backend/instance/create$', instance_controller.InstanceAddController()),
    url(r'^backend/instance/delete$', instance_controller.InstanceDeleteController()),
    url(r'^backend/instance/update$', instance_controller.InstanceUpdateController()),
    url(r'^backend/instance/action$', instance_controller.InstanceStartController()),

    url(r'^instance_type$', instance_type_controller.InstanceTypeController()),
    url(r'^instance_type/(?P<rid>[\w-]+)$', instance_type_controller.InstanceTypeIdController()),
]
