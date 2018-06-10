import json
import requests
import concurrent.futures
import boto3

from nanotask.models import *
from django.db import transaction

def run(context):
    context.parser.add_argument("--production", help="Production mode (non-sandbox)", action="store_true")
    args = context.parser.parse_args()
    is_sandbox = args.production
    
    with open("/root/DynamicCrowd/settings/project/{}.json".format(context.project_name)) as f:
        project_settings = json.load(f)
    
    client = context.get_mturk_client(is_sandbox)
    params = project_settings["AMT"]["HITParams"]
    params["Question"] = '<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">'\
                 + '<ExternalURL>{}/nanotask/base/{}/</ExternalURL>'.format(context.settings["BaseUrl"], context.project_name)\
                 + '<FrameHeight>{}</FrameHeight>'.format(project_settings["AMT"]["FrameHeight"])\
                 + '</ExternalQuestion>'
    num_unsolved_answers = Answer.objects.filter(mturk_worker_id=None).count()
    num_hits = -(-num_unsolved_answers//project_settings["DynamicCrowd"]["NanotasksPerHIT"]) # ceiling division
    print("{} HITs posted!".format(num_hits))
    client.create_hit(**params)
