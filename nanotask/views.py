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
from django.forms.models import model_to_dict

import boto3
import concurrent.futures

project_settings_all = {}

def load_project_settings(project_name):
    global project_settings_all
    if project_name not in project_settings_all:
        project_settings_all[project_name] = json.load(open("/root/DynamicCrowd/settings/projects/{}.json".format(project_name)))
    return project_settings_all[project_name]

@xframe_options_exempt
def load_base(request, project_name):
    project_settings = load_project_settings(project_name)
    context = {
        "base_title": project_settings["DynamicCrowd"]["Title"],
        "base_instruction": loader.get_template("./{}/instruction.html".format(project_name)).render({}, request),
        "nanotasks_per_hit": project_settings["DynamicCrowd"]["NanotasksPerHIT"],
        "min_height": project_settings["AMT"]["FrameHeight"]
    }
    ret = render(request, "base.html", context=context)
    return ret


@csrf_exempt
def load_static_template(request, project_name, template_name):
    template_path = "./{}/{}.html".format(project_name,template_name)
    return render(request, template_path)

@csrf_exempt
def load_nanotask(request, project_name):

    def get_reserved_nanotask(template_names=None, cond=None):
        template_names = [t for t in template_names if t is not None]
        if cond=="include":
            return Nanotask.objects.using(project_name).filter(ticket__mturk_worker_id=mturk_worker_id,
                                                               ticket__session_tab_id=session_tab_id,
                                                               ticket__time_submitted=None,
                                                               template_name__in=template_names).order_by('id').first();
        elif cond=="exclude":
            return Nanotask.objects.using(project_name).filter(ticket__mturk_worker_id=mturk_worker_id,
                                                               ticket__session_tab_id=session_tab_id,
                                                               ticket__time_submitted=None).exclude(template_name__in=template_names).order_by('id').first();
        else:
            return Nanotask.objects.using(project_name).filter(ticket__mturk_worker_id=mturk_worker_id,
                                                               ticket__session_tab_id=session_tab_id,
                                                               ticket__time_submitted=None).order_by('id').first();

    def reserve_nanotask(cursor, template_query):
        sql = "update {1}.nanotask_ticket set mturk_worker_id='{0}', session_tab_id='{2}', user_agent='{3}', time_assigned='{5}' where mturk_worker_id is null and nanotask_id not in ( select nanotask_id from ( select distinct nanotask_id from {1}.nanotask_ticket as a inner join {1}.nanotask_nanotask as n on a.nanotask_id=n.id where {4}(a.mturk_worker_id='{0}')) as tmp) order by nanotask_id asc, mturk_worker_id desc limit 1;".format(mturk_worker_id, project_name, session_tab_id, user_agent, template_query, timezone.now())
        cursor.execute(sql)

    def release_nanotask(cursor,nanotask):
        sql = "update {0}.nanotask_ticket set mturk_worker_id=null, session_tab_id='', user_agent='', time_assigned=NULL where nanotask_id='{1}' and mturk_worker_id='{2}' and session_tab_id='{3}';".format(project_name, nanotask.id, mturk_worker_id, session_tab_id)
        cursor.execute(sql)



    request_json = json.loads(request.body)
    mturk_worker_id = request_json["mturk_worker_id"]
    session_tab_id = request_json["session_tab_id"]
    user_agent = request_json["user_agent"]
    status = request_json["status"]
    response = {}


    project_settings = load_project_settings(project_name)

    if status=="__preview__":

        template_path = "./{}/preview.html".format(project_name)
        template = loader.get_template(template_path)
        response = {
            "info": {"id": None, "project_name": None, "template_name": "__preview__" },
            "html": template.render({}, request)
        } 
        return JsonResponse(response)

    else:

        if "WhiteWorkersList" in project_settings["DynamicCrowd"]:
            if mturk_worker_id not in project_settings["DynamicCrowd"]["WhiteWorkersList"]:
                html = '<center>You are not eligible to work on this HIT.</center><script>alert("We are sorry, but you are not in our list of workers who can work on this HIT. Please return this HIT.");</script>';
                response = {
                    "info": {"id": None, "project_name": project_name, "template_name": "__excluded__" },
                    "html": html
                } 
                return JsonResponse(response)

        assignments = AMTAssignment.objects.using(project_name).filter(mturk_worker_id=mturk_worker_id).all()
        try:
            max_assignments_per_worker = project_settings["DynamicCrowd"]["MaxAssignmentsPerWorker"]
        except:
            max_assignments_per_worker = 9999999

        if len(assignments)>=max_assignments_per_worker :
            html = '<center>You have completed the maximum number of HITs you can submit.</center><script>alert("We are sorry, but you have completed the maximum number of HITs you can submit.");</script>';
            response = {
                "info": {"id": None, "project_name": project_name, "template_name": "__maxassignments__" },
                "html": html
            } 
            return JsonResponse(response)


        try:
            first_template = project_settings["DynamicCrowd"]["FirstTemplate"]
        except:
            first_template = None
        try:
            last_template = project_settings["DynamicCrowd"]["LastTemplate"]
        except:
            last_template = None
    
        # matters only when page reloaded
        if status=="first":
            nanotask = get_reserved_nanotask([first_template],"include")
        elif status=="last":
            nanotask = get_reserved_nanotask([last_template],"include")
        else:
            nanotask = get_reserved_nanotask([first_template, last_template],"exclude")
        response["status"] = status

        # matters only when no nanotask is reserved
        if not nanotask:
            with connection.cursor() as cursor:
                if first_template or last_template:
                    template_query_main = "n.template_name in ({}) or ".format(",".join(["'{}'".format(t) for t in [first_template, last_template] if t]))
                else:
                    template_query_main = ""
                template_query_first = "n.template_name<>'{}' or ".format(first_template)
                template_query_last = "n.template_name<>'{}' or ".format(last_template)

                def reserve_nanotask_first(response):
                    reserve_nanotask(cursor, template_query_main)
                    nanotask_main = get_reserved_nanotask([first_template,last_template],"exclude")
                    if first_template:
                        if nanotask_main:
                            reserve_nanotask(cursor, template_query_first)
                            nanotask_first = get_reserved_nanotask([first_template],"include")
                            if nanotask_first:
                                nanotask = nanotask_first
                                response["status"] = "first"
                            else:
                                release_nanotask(cursor,nanotask_main)
                                nanotask = None
                        else:
                            nanotask = None
                    else:
                        nanotask = nanotask_main
                        response["status"] = ""
                    return nanotask, response

                def reserve_nanotask_main(response):
                    reserve_nanotask(cursor, template_query_main)
                    nanotask = get_reserved_nanotask([first_template, last_template],"exclude")
                    response["status"] = ""
                    return nanotask, response

                def reserve_nanotask_last(response):
                    if last_template:
                        reserve_nanotask(cursor, template_query_last)
                        nanotask_last = get_reserved_nanotask([last_template],"include")
                        if nanotask_last:
                            nanotask = nanotask_last
                            response["status"] = "last"
                        else:
                            response["status"] = "finish"
                    else:
                        nanotask = None
                        response["status"] = "finish"
                        response["info"] = "dummy"
                    return nanotask, response

                if status=="first": 
                    nanotask, response = reserve_nanotask_first(response)
                    
                elif status=="":
                    nanotask, response = reserve_nanotask_main(response)
                    if not nanotask:
                        nanotask, response = reserve_nanotask_last(response)

                elif status=="last":
                    nanotask, response = reserve_nanotask_last(response)

        if "status" in response and response["status"]=="finish":
            ret = JsonResponse(response)

        # returning main nanotask
        elif nanotask:
            media_data = json.loads(nanotask.media_data)
            template_path = "./{}/{}.html".format(project_name, nanotask.template_name)
            template = loader.get_template(template_path)
            response.update({
                "info": {"id": nanotask.id, "project_name": project_name, "template_name": nanotask.template_name },
                "html": template.render(media_data, request)
            })
            ret = JsonResponse(response)

        # terminating because of some error
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
    project_name = request_json["project_name"]
    status = request_json["status"]

    with transaction.atomic():
        ticket = Ticket.objects.using(project_name).filter(nanotask_id=id, mturk_worker_id=mturk_worker_id).first()
        ticket.time_submitted = timezone.now()
        ticket.working_time = sec
        ticket.save(using=project_name)
    for key,val in ans.items():
        if type(val)==list:
            for v in val:
                Answer(ticket=ticket, name=key, value=v).save(using=project_name)
        else:
            Answer(ticket=ticket, name=key, value=val).save(using=project_name)

    return JsonResponse({})

@csrf_exempt
def update_completed_hit(request):
    request_json = json.loads(request.body)
    ids = request_json["ids"]
    mturk_assignment_id = request_json["mturk_assignment_id"]
    mturk_hit_id = request_json["mturk_hit_id"]
    mturk_worker_id = request_json["mturk_worker_id"]
    project_name = request_json["project_name"]
    amt_assignment = AMTAssignment(mturk_assignment_id = mturk_assignment_id,
                                   mturk_hit_id = mturk_hit_id,
                                   mturk_worker_id = mturk_worker_id)
    amt_assignment.save(using=project_name)
    sql = "UPDATE {0}.nanotask_ticket SET amt_assignment_id='{1}' WHERE nanotask_id IN ({2}) AND mturk_worker_id='{3}';".format(project_name, amt_assignment.id, ",".join(map(str,ids)),  mturk_worker_id)
    with connection.cursor() as cursor:
        cursor.execute(sql)
    connection.close()
    return JsonResponse({})

@csrf_exempt
def get_assignments(request, project_name):
    assignments = AMTAssignment.objects.using(project_name).values()
    assignments_list = [a for a in assignments]
    return JsonResponse(assignments_list, safe=False)

@csrf_exempt
def mturk_operation(request, operation_name):
    def get_mturk_client(is_sandbox):
        with open("/root/DynamicCrowd/settings/global.json") as f:
            settings = json.load(f)

        if is_sandbox:
            endpoint_url = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
        else:
            endpoint_url = "https://mturk-requester.us-east-1.amazonaws.com"
        
        return boto3.client('mturk',
                    aws_access_key_id = settings["AMT"]["Credentials"]["AWSAccessKeyId"],
                    aws_secret_access_key = settings["AMT"]["Credentials"]["AWSSecretAccessKey"],
                    region_name = "us-east-1",
                    endpoint_url = endpoint_url
        )

    def exec_operation(client, operation_name, **kwargs):
        exec_str = "client.{}(**kwargs)".format(operation_name)
        try:
            exec(exec_str)
        except Exception as e:
            result = str(e)
        if "result" in locals():
            return {"status": "error", "data": kwargs, "message": result}
        else:
            return {"status": "success", "data": kwargs}

    #client = get_mturk_client(True) # sandbox
    client = get_mturk_client(False) # production
    request_json = json.loads(request.body)
    params_list = request_json["params_list"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for params in params_list:
            futures.append(executor.submit(exec_operation, client, operation_name, **params))

    results = [f.result() for f in futures]

    return JsonResponse(results, safe=False)

@csrf_exempt
def update_assignment_status(request, project_name, status):
    request_json = json.loads(request.body)
    assignment_ids = request_json["ids"]

    sql = "UPDATE {0}.nanotask_amtassignment SET status='{1}' WHERE mturk_assignment_id IN ({2});".format(project_name, status, ",".join(["'{}'".format(aid) for aid in assignment_ids]))
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
    return JsonResponse({})

@csrf_exempt
def update_assignment_comment(request, project_name):
    request_json = json.loads(request.body)
    id = request_json["id"]
    comment = request_json["comment"]
    assignment = AMTAssignment.objects.using(project_name).filter(id=id).first()
    assignment.comment = comment
    assignment.save()
    return JsonResponse({})

@csrf_exempt
def view_manage_hits(request, project_name):
    template_path = "./console/manage_hits.html".format()
    return HttpResponse(loader.get_template(template_path).render({}, request))
