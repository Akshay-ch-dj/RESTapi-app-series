from django.urls import path, include
from rest_framework.routers import DefaultRouter

from series import views

app_name = 'series'


# DefaultRouter is feature in django rest_framework that automatically generate
# the urls for the viewset, only need to include router urls in 'urlpatterns'
router = DefaultRouter()
router.register('tags', views.TagViewSet)

urlpatterns = [
    # router generates a list of urls associated with the viewsets
    path('', include(router.urls)),
]
