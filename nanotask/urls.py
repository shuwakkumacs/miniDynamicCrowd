from django.conf.urls import url

from . import views

app_name="nanotask"
urlpatterns = [
    url(r'^base/(?P<project_name>\w+)/$', views.load_base, name="load_base"),
    url(r'^nanotask/(?P<project_name>\w+)/$', views.load_nanotask, name="load_nanotask"),
    url(r'^nanotask/(?P<project_name>\w+)/(?P<template_name>\w+)/$', views.load_static_template, name="load_static_template"),
    url(r'^answer/save/$', views.save_answer, name="save_answer"),
    url(r'^assignment/save/$', views.update_completed_hit, name="update_completed_hit"),
    url(r'^data/assignments/(?P<project_name>\w+)/$', views.get_assignments, name="get_assignments"),
    url(r'^console/manage-hits/(?P<project_name>\w+)/$', views.view_manage_hits, name="view_manage_hits"),
    url(r'^mturkapi/(?P<operation_name>\w+)/$', views.mturk_operation, name="mturk_operation"),
]
