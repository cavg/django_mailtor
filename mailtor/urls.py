from django.urls import path

from . import views

urlpatterns = [
    path('create_template', views.create_template, name='create_template'),
    path('create_entity', views.create_entity, name='create_entity'),
    path('tracking_open/<str:mail_id>', views.tracking_open, name='tracking_open'),
    path('home', views.index, name="mailtor")
]