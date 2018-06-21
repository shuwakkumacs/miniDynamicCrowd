import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db import transaction
from django.utils import timezone
from .models import *
import json


@csrf_exempt
def create_project(request):
    request_json = json.loads(request.body)
    project = Project(**request_json)
    project.save()
    return HttpResponse(None)


@xframe_options_exempt
def load_base(request, project_name):
    project_settings = json.load(open("/root/DynamicCrowd/settings/projects/{}.json".format(project_name)))
    context = {
        "base_title": project_settings["DynamicCrowd"]["Title"],
        "base_instruction": loader.get_template("./{}/instruction.html".format(project_name)).render({}, request),
        "nanotasks_per_hit": project_settings["DynamicCrowd"]["NanotasksPerHIT"],
        "min_height": project_settings["AMT"]["FrameHeight"]
    }
    ret = render(request, "base.html", context=context)
    return ret


@csrf_exempt
def load_preview_nanotask(request, project_name, mturk_worker_id):
    template_path = "./{}/preview.html".format(project_name)
    template = loader.get_template(template_path)
    response = {
        "info": {"id": None, "project_name": project_name, "template_name": "__preview__" },
        "html": template.render({}, request)
    } 
    return JsonResponse(response)


@csrf_exempt
def load_nanotask(request, project_name, mturk_worker_id):
    # FIXME:: obviously not optimal or scaling
    reserved_nanotask = Nanotask.objects.raw("SELECT * FROM nanotask INNER JOIN answers ON nanotask.id=answers.nanotask_id WHERE nanotask.id NOT IN (SELECT nanotask_id FROM answers WHERE mturk_worker_id!='{}') AND nanotask.project_name='{}';".format(mturk_worker_id,project_name))
    # TODO:: what to do with reservation --- like when reloading the page or coming back to the task later?
    #reserved_nanotask = Nanotask.objects.filter(answer__mturk_worker_id=mturk_worker_id).first()
    #if reserved_nanotask:
    #    nanotask = reserved_nanotask
    #else:
        # TODO:: get one under a certain criteria
    with transaction.atomic():
        nanotask = Nanotask.objects.filter(project_name=project_name, answer__mturk_worker_id=None).exclude(answer__mturk_worker_id=mturk_worker_id).first()
        if nanotask:
            answer = Answer.objects.filter(nanotask_id=nanotask.id, mturk_worker_id=None).first()
            answer.mturk_worker_id = mturk_worker_id
            answer.time_assigned = timezone.now()
            answer.save()

    if nanotask:
        media_data = json.loads(nanotask.media_data)
        template_path = "./{}/{}.html".format(project_name, nanotask.template_name)
        template = loader.get_template(template_path)
        response = {
            "info": {"id": nanotask.id, "project_name": nanotask.project_name, "template_name": nanotask.template_name },
            "html": template.render(media_data, request)
        } 
        ret = JsonResponse(response)
    else:
        ret = JsonResponse({"info": None, "html": None}) 
    return ret


@csrf_exempt
def create_nanotasks(request):
    # TODO:: replace the current script by this restful api
    pass

@csrf_exempt
def save_answers(request):
    request_json = json.loads(request.body)
    ids = request_json["ids"]
    secs = request_json["secs"]
    answers = request_json["answers"]

    with transaction.atomic():
        amt_assignment = AMTAssignment(mturk_assignment_id=request_json["mturk_assignment_id"],
                                       mturk_hit_id=request_json["mturk_hit_id"],
                                       mturk_worker_id=request_json["mturk_worker_id"])
        amt_assignment.save()
        for i,id in enumerate(ids):
            answer = Answer.objects.filter(nanotask_id=id,mturk_worker_id=request_json["mturk_worker_id"]).first()
            answer.value = json.dumps(answers[i])
            answer.time_submitted = timezone.now()
            answer.secs_elapsed = secs[i]
            answer.amt_assignment = amt_assignment
            answer.save()

    return JsonResponse({})
