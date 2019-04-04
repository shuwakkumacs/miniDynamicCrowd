import json
import concurrent.futures
import boto3
import datetime

from nanotask.models import *
from django.db import transaction
from django.utils import timezone

def run(context):
    context.parser.add_argument("-i", "--id", help="delete by nanotask ID", default=None)
    context.parser.add_argument("-c", "--create-id", help="delete by create_id", default=None)
    context.parser.add_argument("-t", "--template", help="delete by template name", default=None)
    args = context.parser.parse_args()
    id = args.id
    create_id = args.create_id
    template_name = args.template

    if not (id or create_id or template_name):
        ans = input("deleting all. are you sure? [y/N]: ")
        if ans=="y":
             anotasks = Nanotask.objects.using(context.project_name).delete()
    else:
        args = {}
        for name in ['id','create_id','template_name']:
            if eval(name):
                args[name] = eval(name)
        # DELETES ALL FOREIGN OBJECTS!!!
        nanotasks = Nanotask.objects.using(context.project_name).filter(**args).delete()
