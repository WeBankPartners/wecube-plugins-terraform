#_ coding:utf-8 _*_

from django.conf.urls import include, url


urlpatterns = [
    # url(r'^test/', include('apps.controller.test.route', namespace='test')),
    url(r'^configer/', include('apps.controller.configer.route', namespace='configer')),
    url(r'^network/', include('apps.controller.network.route', namespace='network')),
]