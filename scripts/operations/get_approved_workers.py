import json
import concurrent.futures
import boto3
import datetime

from nanotask.models import *
from django.db import transaction
from django.utils import timezone
import concurrent.futures

def run(context):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    context.parser.add_argument("--production", help="Production mode (non-sandbox)", action="store_false")
    args = context.parser.parse_args()
    is_sandbox = args.production

    client = context.get_mturk_client(is_sandbox)
    hits = HIT.objects.using(context.project_name).filter(project_name=context.project_name,is_sandbox=is_sandbox,time_expired=None).all()

    for hit in hits:
        executor.submit(list_assignments_for_hit,client,hit,context.project_name)
        #list_assignments_for_hit(client,hit,context.project_name)

def list_assignments_for_hit(client,hit,project_name):
    try:
        ret = client.list_assignments_for_hit(HITId=hit.mturk_hit_id)
        print(ret)
    except:
        print("skipping {}".format(hit.mturk_hit_id))
