from django.conf.urls import url

from . import views

app_name="nanotask"
urlpatterns = [
    url(r'^base/(?P<project_name>\w+)/$', views.load_base, name="load_base"),
    url(r'^project/$', views.create_project, name="create_project"),
    #url(r'^project/(?P<project_name>\w+)/$', views.get_project, name="get_project"),
    url(r'^nanotask/(?P<project_name>\w+)/(?P<mturk_worker_id>\w+)/$', views.load_nanotask, name="load_nanotask"),
    url(r'^nanotask/(?P<project_name>\w+)/(?P<mturk_worker_id>\w+)/preview/$', views.load_preview_nanotask, name="load_preview_nanotask"),
    url(r'^answers/save/(?P<mturk_worker_id>\w+)/$', views.save_answers, name="save_answers"),
]
