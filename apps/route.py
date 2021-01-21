# _ coding:utf-8 _*_

from django.conf.urls import include, url

urlpatterns = [
    # url(r'^test/', include('apps.controller.test.route', namespace='test')),
    url(r'^configer/', include('apps.controller.configer.route', namespace='configer')),
    url(r'^network/', include('apps.controller.network.route', namespace='network')),
    url(r'^vm/', include('apps.controller.vm.route', namespace='vm')),
    url(r'^storage/', include('apps.controller.storage.route', namespace='storage')),
    url(r'^loadbalance/', include('apps.controller.loadbalance.route', namespace='lb')),
    url(r'^database/', include('apps.controller.database.route', namespace='database')),
]
