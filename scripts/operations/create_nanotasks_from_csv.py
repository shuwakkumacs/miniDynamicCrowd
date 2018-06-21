import os
import csv
import sys

def run(context):
    context.parser.add_argument("template_name", help="Template name")
    context.parser.add_argument("csv_filename", help="CSV file name")
    args = context.parser.parse_args()
    template_name = args.template_name
    csv_filename = args.csv_filename

    with open("./scripts/csv/{}/{}".format(context.project_name,csv_filename)) as f:
        reader = csv.reader(f, delimiter=",", quotechar="'")
        columns = next(reader)
        def generate():
            for row in reader:
                media_data = {}
                for i,col in enumerate(columns):
                    media_data[col] = row[i]
                yield media_data
        context.save_nanotasks(template_name, generate())

