# _ coding:utf-8 _*_

from django.conf.urls import include, url
from provider_controller import ProviderController
from provider_controller import ProviderIdController
from resource_controller import ResourceController
from resource_controller import ResourceIdController
from config_controller import ConfigController
from config_controller import ConfigIdController
from provider_secret_controller import ProviderSecretController
from provider_secret_controller import ProviderSecretIdController


urlpatterns = [
    url(r'^provider$', ProviderController()),
    url(r'^provider/(?P<rid>[\w-]+)$', ProviderIdController()),

    url(r'^resource$', ResourceController()),
    url(r'^resource/(?P<rid>[\w-]+)$', ResourceIdController()),

    url(r'^keyconfig$', ConfigController()),
    url(r'^keyconfig/(?P<rid>[\w-]+)$', ConfigIdController()),

    url(r'^secret$', ProviderSecretController()),
    url(r'^secret/(?P<rid>[\w-]+)$', ProviderSecretIdController()),
]
