import os
import csv
import sys

def run(context):
    template_name = sys.argv[3]
    with open("./scripts/nanotask_csv/{}/{}.csv".format(context.project_name,template_name)) as f:
        reader = csv.reader(f, delimiter=",", quotechar="'")
        columns = next(reader)
        def generate():
            for row in reader:
                media_data = {}
                for i,col in enumerate(columns):
                    media_data[col] = row[i]
                yield media_data
        context.save_nanotasks(template_name, generate())

