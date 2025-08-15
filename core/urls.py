from django.urls import path, conf
from rest_framework.routers import DefaultRouter
from django.conf import settings


router = DefaultRouter()

if not settings.DEBUG:
    router.include_root_view = False

urlpatterns = [
    path("", conf.include(router.urls)),
]
