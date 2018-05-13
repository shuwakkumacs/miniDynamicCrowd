#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from django.forms.models import model_to_dict

from tqdm import tqdm

class Context:

    def __init__(self, setting):
        with open(setting) as f:
            self.settings = json.load(f)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        self.operation = sys.argv[1]
        self.project_name = sys.argv[2]
    
    def get_mturk_client(self):
        if self.settings["AMT"]["Sandbox"]:
            endpoint_url = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
        else:
            endpoint_url = "https://mturk-requester.us-east-1.amazonaws.com"
        
        return boto3.client('mturk',
                    aws_access_key_id = self.settings["AMT"]["Credentials"]["AWSAccessKeyId"],
                    aws_secret_access_key = self.settings["AMT"]["Credentials"]["AWSSecretAccessKey"],
                    region_name = "us-east-1",
                    endpoint_url = endpoint_url
        )
    
    def new_project(self):
        return Project(name=self.project_name, nanotasks_per_hit=self.settings["DynamicCrowd"]["AnswersPerNanotask"])
    
    def save_nanotasks(self, template_name, generator, total=0):
        with transaction.atomic():
            for row in tqdm(generator, total=total):
                nanotask = Nanotask(project_name=self.project_name, template_name=template_name, media_data=json.dumps(row))
                nanotask.save()
                for i in range(self.settings["DynamicCrowd"]["AnswersPerNanotask"]):
                    answer = Answer(nanotask=nanotask)
                    answer.save()

    def export_answers(self, callback):
        for row in Answer.objects.select_related('nanotask').filter(nanotask__project_name=self.project_name):
            callback(model_to_dict(row), model_to_dict(row.nanotask))

def main():
    context = Context("/root/settings.json")
    mod = __import__(context.operation, fromlist=["run"])
    run = getattr(mod,"run")
    run(context)

if __name__=="__main__":
    main()
