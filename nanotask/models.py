from django.db import models

# Create your models here.

class AMTAssignment(models.Model):
    mturk_assignment_id = models.CharField(max_length=255, null=True, default=None)
    mturk_hit_id = models.CharField(max_length=255, null=True, default=None)
    mturk_worker_id = models.CharField(max_length=255, null=True, default=None)
    bonus_amount = models.FloatField(null=False, default=0.0)
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_bonus_sent = models.DateTimeField(null=True)

class HIT(models.Model):
    mturk_hit_id = models.CharField(max_length=255, null=True, default=None)
    project_name = models.CharField(max_length=255, null=True, default=None)
    is_sandbox = models.IntegerField(null=False)
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_expired = models.DateTimeField(null=True)

class Nanotask(models.Model):
    project_name = models.TextField(null=False)
    template_name = models.TextField(null=False)
    media_data = models.TextField(null=True, default={})
    time_created = models.DateTimeField(auto_now_add=True, blank=True)

class Answer(models.Model):
    nanotask = models.ForeignKey(Nanotask, on_delete=models.CASCADE)
    amt_assignment = models.ForeignKey(AMTAssignment, on_delete=models.CASCADE, null=True, default=None)
    mturk_worker_id = models.CharField(max_length=255, null=True, default=None)
    value = models.TextField(null=True, default=None)
    time_created = models.DateTimeField(auto_now_add=True, blank=True)
    time_assigned = models.DateTimeField(null=True)
    time_submitted = models.DateTimeField(null=True)
    secs_elapsed = models.FloatField(null=False, default=0.0)
