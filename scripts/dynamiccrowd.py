import os
import django
import csv
import sys
import json
import requests
import concurrent.futures
import boto3
sys.path.append(".")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DynamicCrowd.settings')
django.setup()
from nanotask.models import *
from django.db import transaction

f = open("/root/settings.json")
settings = json.load(f)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

operation = sys.argv[1]
project_name = sys.argv[2]

def get_mturk_client():
	if settings["AMT"]["Sandbox"]:
		endpoint_url = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
	else:
		endpoint_url = "https://mturk-requester.us-east-1.amazonaws.com"
	
	return boto3.client('mturk',
		aws_access_key_id = settings["AMT"]["Credentials"]["AWSAccessKeyId"],
		aws_secret_access_key = settings["AMT"]["Credentials"]["AWSSecretAccessKey"],
		region_name = "us-east-1",
		endpoint_url = endpoint_url
	)


if __name__=="__main__":
	if operation=="create_project":
		project = Project(name=project_name, nanotasks_per_hit=settings["DynamicCrowd"]["AnswersPerNanotask"])
		project.save()
	

	elif operation=="create_nanotasks":
		template_name = sys.argv[3]
		f = open("./scripts/nanotask_csv/{}/{}.csv".format(project_name,template_name))
		reader = csv.reader(f, delimiter=",", quotechar="'")
		
		columns = next(reader)
		with transaction.atomic():
			for row in reader:
				media_data = {}
				for i,col in enumerate(columns):
					media_data[col] = row[i]
				nanotask = Nanotask(project_name=project_name, template_name=template_name, media_data=json.dumps(media_data))
				nanotask.save()
				for i in range(settings["DynamicCrowd"]["AnswersPerNanotask"]):
					answer = Answer(nanotask=nanotask)
					answer.save()
	

	elif operation=="create_hits":
		client = get_mturk_client()
		params = settings["AMT"]["HITParams"]
		params["Question"] = '<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">'\
			+ '<ExternalURL>{}/nanotask/base/{}/</ExternalURL>'.format(settings["BaseUrl"], project_name)\
			+ '<FrameHeight>{}</FrameHeight>'.format(settings["AMT"]["FrameHeight"])\
			+ '</ExternalQuestion>'
		num_unsolved_answers = Answer.objects.filter(mturk_worker_id=None).count()
		num_hits = -(-num_unsolved_answers//settings["DynamicCrowd"]["NanotasksPerHIT"]) # ceiling division
		#num_hits = 1
		print(num_hits)
		#for i in range(num_hits):
		#	#client.create_hit(**params)
		#	executor.submit(client.create_hit,**params)
