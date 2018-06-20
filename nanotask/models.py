from django.db import models

# Create your models here.

class Project(models.Model):
    name = models.TextField(null=False)
    nanotasks_per_hit = models.IntegerField(default=1, null=True)
    time_created = models.DateTimeField(auto_now_add=True, blank=True)

class Nanotask(models.Model):
    project_name = models.TextField(null=False)
    template_name = models.TextField(null=False)
    media_data = models.TextField(null=True, default={})
    time_created = models.DateTimeField(auto_now_add=True, blank=True)

class Answer(models.Model):
    nanotask = models.ForeignKey(Nanotask, on_delete=models.CASCADE)
    mturk_worker_id = models.CharField(max_length=255, null=True, default=None)
    value = models.TextField(null=True, default=None)
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_assigned = models.DateTimeField(null=True)
    time_submitted = models.DateTimeField(null=True)
    secs_elapsed = models.FloatField(null=False, default=0.0)

#class Template(models.Model):
#    project = models.ForeignKey(Project, on_delete=models.CASCADE)
#    name = models.TextField(null=False)
