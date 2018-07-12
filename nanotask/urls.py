from django.conf.urls import url

from . import views

app_name="nanotask"
urlpatterns = [
    url(r'^base/(?P<project_name>\w+)/$', views.load_base, name="load_base"),
    url(r'^nanotask/$', views.load_nanotask, name="load_nanotask"),
    url(r'^nanotask/(?P<project_name>\w+)/(?P<mturk_worker_id>\w+)/preview/$', views.load_preview_nanotask, name="load_preview_nanotask"),
    url(r'^answer/save/$', views.save_answer, name="save_answer"),
    url(r'^assignment/save/$', views.save_assignment, name="save_assignment"),
]
