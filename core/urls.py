from django.urls import path, conf
from rest_framework.routers import DefaultRouter


router = DefaultRouter()


urlpatterns = [
    path("", conf.include(router.urls)),
]
