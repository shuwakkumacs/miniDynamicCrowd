from django.db import models

# Create your models here.

class AMTAssignment(models.Model):
    mturk_assignment_id = models.CharField(max_length=255)
    mturk_hit_id = models.CharField(max_length=255, blank=True, null=True)  # allow blank for testing
    mturk_worker_id = models.CharField(max_length=255, blank=True, null=True)  # allow blank for testing
    bonus_amount = models.FloatField(default=0.0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_bonus_sent = models.DateTimeField(blank=True, null=True)

class HIT(models.Model):
    mturk_hit_id = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255)
    is_sandbox = models.IntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_expired = models.DateTimeField(blank=True, null=True)

class Nanotask(models.Model):
    project_name = models.TextField(max_length=255)
    template_name = models.TextField(max_length=255)
    media_data = models.TextField(blank=True, default="{}")
    create_id = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)

class Ticket(models.Model):
    nanotask = models.ForeignKey(Nanotask, on_delete=models.CASCADE)
    amt_assignment = models.ForeignKey(AMTAssignment, on_delete=models.CASCADE, blank=True, null=True)
    mturk_worker_id = models.CharField(max_length=255, blank=True, null=True)
    session_tab_id = models.CharField(max_length=32)
    time_created = models.DateTimeField(auto_now_add=True)
    time_assigned = models.DateTimeField(blank=True, null=True)
    time_submitted = models.DateTimeField(blank=True, null=True)
    working_time = models.FloatField(default=0.0)
    user_agent = models.CharField(max_length=255)

class Answer(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    name = models.TextField()
    value = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
