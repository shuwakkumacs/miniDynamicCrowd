import os
import django
import csv
import sys
import json
sys.path.append(".")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DynamicCrowd.settings')  # 自分のsettings.py
django.setup()
from nanotask.models import *
from django.db import transaction


filename = sys.argv[1]
f = open("./scripts/nanotask_csv/{}".format(filename))
reader = csv.reader(f, delimiter=",", quotechar="'")

f = open("./scripts/settings/dynamiccrowd.json")
dc_settings = json.load(f)

project_name,template_name = next(reader)
columns = next(reader)
with transaction.atomic():
	for row in reader:
		media_data = {}
		for i,col in enumerate(columns):
			media_data[col] = row[i]
		nanotask = Nanotask(project_name=project_name, template_name=template_name, media_data=json.dumps(media_data))
		nanotask.save()
		for i in range(dc_settings["answers_per_nanotask"]):
			answer = Answer(nanotask=nanotask)
			answer.save()
