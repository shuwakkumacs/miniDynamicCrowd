import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db import transaction
from .models import *
import json

settings = json.load(open("/root/settings.json"))


@csrf_exempt
def create_project(request):
	request_json = json.loads(request.body)
	project = Project(**request_json)
	project.save()
	return HttpResponse(None)


@csrf_exempt
def get_project(request, project_name):
	project = Project.objects.filter(name=project_name).first()
	return JsonResponse({"id": project.id, "name": project.name, "nanotasks_per_hit": project.nanotasks_per_hit})


@xframe_options_exempt
def load_base(request, project_name):
	context = {
		"min_height": settings["AMT"]["FrameHeight"],
		"base_url": settings["BaseUrl"]
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
	reserved_nanotask = Nanotask.objects.raw("SELECT * FROM nanotask INNER JOIN answers ON nanotask.id=answers.nanotask_id WHERE nanotask.id NOT IN (SELECT nanotask_id FROM answers WHERE mturk_worker_id!='{}');".format(mturk_worker_id))
	# TODO:: what to do with reservation --- like when reloading the page or coming back to the task later?
	#reserved_nanotask = Nanotask.objects.filter(answer__mturk_worker_id=mturk_worker_id).first()
	#if reserved_nanotask:
	#	nanotask = reserved_nanotask
	#else:
		# TODO:: get one under a certain criteria
	with transaction.atomic():
		nanotask = Nanotask.objects.filter(project_name=project_name, answer__mturk_worker_id=None).exclude(answer__mturk_worker_id=mturk_worker_id).first()
		if nanotask:
			answer = Answer.objects.filter(nanotask_id=nanotask.id, mturk_worker_id=None).first()
			answer.mturk_worker_id = mturk_worker_id
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
def save_answers(request, mturk_worker_id):
	print(request.body)
	request_json = json.loads(request.body)
	ids = request_json["ids"]
	answers = request_json["answers"]

	with transaction.atomic():
		for i,id in enumerate(ids):
			answer = Answer.objects.filter(nanotask_id=id,mturk_worker_id=mturk_worker_id).first()
			answer.value = json.dumps(answers[i])
			answer.save()

	return JsonResponse({})
