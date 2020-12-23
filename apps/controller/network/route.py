# _ coding:utf-8 _*_

from django.conf.urls import include, url
from vpc_controller import VPCController
from vpc_controller import VPCAddController
from vpc_controller import VPCIdController
from vpc_controller import VPCDeleteController

urlpatterns = [
    url(r'^vpc/create$', VPCAddController()),
    url(r'^vpc$', VPCController()),
    url(r'^vpc/describe$', VPCIdController()),
    url(r'^vpc/delete$', VPCDeleteController())
]
