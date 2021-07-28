from django.conf.urls import include, url
from .views import *
urlpatterns = [
    url(r'^items/$', ItemList),
]