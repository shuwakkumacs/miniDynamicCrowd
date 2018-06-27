import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db import transaction, connection
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
    #reserved_nanotask = Nanotask.objects.raw("SELECT * FROM nanotask INNER JOIN answers ON nanotask.id=answers.nanotask_id WHERE nanotask.id NOT IN (SELECT nanotask_id FROM answers WHERE mturk_worker_id!='{}') AND nanotask.project_name='{}';".format(mturk_worker_id,project_name))
    # TODO:: what to do with reservation --- like when reloading the page or coming back to the task later?
    #reserved_nanotask = Nanotask.objects.filter(answer__mturk_worker_id=mturk_worker_id).first()
    #if reserved_nanotask:
    #    nanotask = reserved_nanotask
    #else:
        # TODO:: get one under a certain criteria
    nanotask = Nanotask.objects.filter(answer__mturk_worker_id=mturk_worker_id, answer__value=None, project_name=project_name).order_by('id').first();
    if not nanotask:
        sql = "update nanotask_answer set mturk_worker_id='{0}' where mturk_worker_id is null and nanotask_id not in ( select nanotask_id from ( select distinct nanotask_id from nanotask_answer as a inner join nanotask_nanotask as n on a.nanotask_id=n.id where (a.mturk_worker_id='{0}' and n.project_name='{1}') or n.project_name<>'{1}') as tmp) order by nanotask_id asc, mturk_worker_id desc limit 1;".format(mturk_worker_id,project_name)
        with connection.cursor() as cursor:
            cursor.execute(sql)
        #nanotask = Nanotask.objects.raw("select * from nanotask_nanotask as n inner join nanotask_answer as a on n.id=a.nanotask_id where project_name='{0}' and n.id not in (select distinct nanotask_id from nanotask_answer where mturk_worker_id='{1}' and project_name='{0}')".format(project_name,mturk_worker_id))
        nanotask = Nanotask.objects.filter(answer__mturk_worker_id=mturk_worker_id, answer__value=None, project_name=project_name).order_by('id').first();
    #with transaction.atomic():
    #    nanotask = Nanotask.objects.filter(project_name=project_name, answer__mturk_worker_id=None).exclude(answer__mturk_worker_id=mturk_worker_id).first()
    #    if nanotask:
    #        answer = Answer.objects.filter(nanotask_id=nanotask.id, mturk_worker_id=None).first()
    #        answer.mturk_worker_id = mturk_worker_id
    #        answer.time_assigned = timezone.now()
    #        answer.save()

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
def save_answer(request):
    request_json = json.loads(request.body)
    id = request_json["id"]
    sec = request_json["sec"]
    ans = request_json["answer"]
    mturk_worker_id = request_json["mturk_worker_id"]

    with transaction.atomic():
        answer = Answer.objects.filter(nanotask_id=id, mturk_worker_id=mturk_worker_id).first()
        answer.value = json.dumps(ans)
        answer.time_submitted = timezone.now()
        answer.secs_elapsed = sec
        answer.save()

    return JsonResponse({})

@csrf_exempt
def save_assignment(request):
    request_json = json.loads(request.body)
    ids = request_json["ids"]
    mturk_assignment_id = request_json["mturk_assignment_id"]
    mturk_hit_id = request_json["mturk_hit_id"]
    mturk_worker_id = request_json["mturk_worker_id"]
    amt_assignment = AMTAssignment(mturk_assignment_id = mturk_assignment_id,
                                   mturk_hit_id = mturk_hit_id,
                                   mturk_worker_id = mturk_worker_id)
    amt_assignment.save()
    sql = "UPDATE nanotask_answer SET amt_assignment_id='{}' WHERE nanotask_id IN ({}) AND mturk_worker_id='{}';".format(amt_assignment.id, ",".join(map(str,ids)),mturk_worker_id)
    with connection.cursor() as cursor:
        cursor.execute(sql)
    return JsonResponse({})
