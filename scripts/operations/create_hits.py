import json
import concurrent.futures
import boto3

from nanotask.models import *
from django.db import transaction

def run(context):
    context.parser.add_argument("--production", help="Production mode (non-sandbox)", action="store_false")
    args = context.parser.parse_args()
    is_sandbox = args.production

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    
    with open("/root/DynamicCrowd/settings/projects/{}.json".format(context.project_name)) as f:
        project_settings = json.load(f)
    
    client = context.get_mturk_client(is_sandbox)
    params = project_settings["AMT"]["HITParams"]
    params["Question"] = '<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">'\
                 + '<ExternalURL>{}/nanotask/base/{}/</ExternalURL>'.format(context.settings["BaseUrl"], context.project_name)\
                 + '<FrameHeight>{}</FrameHeight>'.format(project_settings["AMT"]["FrameHeight"])\
                 + '</ExternalQuestion>'
    num_unsolved_answers = Answer.objects.using(context.project_name).filter(mturk_worker_id=None).count()
    num_hits = -(-num_unsolved_answers//project_settings["DynamicCrowd"]["NanotasksPerHIT"]) # ceiling division
    print("{} HITs posted!".format(num_hits))
    for i in range(num_hits):
        executor.submit(create_hit,client,context.project_name,is_sandbox,params)
        #create_hit(client,context.project_name,is_sandbox,params)

def create_hit(client,project_name,is_sandbox,params):
    ret = client.create_hit(**params)
    mturk_hit_id = ret["HIT"]["HITId"]
    hit = HIT(mturk_hit_id=mturk_hit_id,project_name=project_name,is_sandbox=is_sandbox)
    hit.save(using=project_name)
    print("created {}".format(mturk_hit_id))
