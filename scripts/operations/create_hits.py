import json
import requests
import concurrent.futures
import boto3

from nanotask.models import *
from django.db import transaction

def run(context):
	client = context.get_mturk_client()
	params = context.settings["AMT"]["HITParams"]
	params["Question"] = '<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">'\
			     + '<ExternalURL>{}/nanotask/base/{}/</ExternalURL>'.format(context.settings["BaseUrl"], context.project_name)\
			     + '<FrameHeight>{}</FrameHeight>'.format(context.settings["AMT"]["FrameHeight"])\
			     + '</ExternalQuestion>'
	num_unsolved_answers = Answer.objects.filter(mturk_worker_id=None).count()
	num_hits = -(-num_unsolved_answers//context.settings["DynamicCrowd"]["NanotasksPerHIT"]) # ceiling division
	print(num_hits)
