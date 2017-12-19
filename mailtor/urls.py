from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create_template', views.create_template, name='create_template'),
    url(r'^create_entity', views.create_entity, name='create_entity'),
    url(r'^$', views.index, name="mailtor")
]