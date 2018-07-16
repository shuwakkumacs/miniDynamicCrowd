import json
import concurrent.futures
import boto3
import datetime

from nanotask.models import *
from django.db import transaction
from django.utils import timezone

def run(context):
    context.parser.add_argument("--production", help="Production mode (non-sandbox)", action="store_false")
    args = context.parser.parse_args()
    is_sandbox = args.production

    client = context.get_mturk_client(is_sandbox)
    hits = HIT.objects.using(context.project_name).filter(project_name=context.project_name,is_sandbox=is_sandbox,time_expired=None).all()

    for hit in hits:
        executor.submit(expire_hit,client,hit,context.project_name)
        #expire_hit(client,hit,context.project_name)

def expire_hit(client,hit,project_name):
    try:
        ret = client.update_expiration_for_hit(HITId=hit.mturk_hit_id,ExpireAt=datetime.datetime(1,1,1))
        hit.time_expired = timezone.now()
        hit.save(using=project_name)
        print(hit.mturk_hit_id)
    except:
        print("skipping {}".format(hit.mturk_hit_id))
