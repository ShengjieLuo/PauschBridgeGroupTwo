from django.urls import path,re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('process', views.process, name='process'),
    re_path(r'onbridge/*', views.onbridge, name='onbridge'),
]
