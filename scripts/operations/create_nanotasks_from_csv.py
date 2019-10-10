import os
import csv
import sys

def run(context):
    context.parser.add_argument("template_name", help="Template name")
    context.parser.add_argument("csv_filename", help="CSV file name")
    context.parser.add_argument("-t", "--test", help="Create as test nanotasks", action="store_true")
    context.parser.add_argument("--ticketnum", help="Force the number of tickets per nanotask", default=None)
    args = context.parser.parse_args()
    template_name = args.template_name
    csv_filename = args.csv_filename
    is_test = args.test
    ticketnum = args.ticketnum

    with open("./scripts/csv/{}/{}".format(context.project_name,csv_filename)) as f:
        reader = csv.reader(f, delimiter=",", quotechar="'")
        columns = next(reader)
        def generate():
            idx = 0
            for row in reader:
                media_data = {}
                ground_truth = None
                for i,col in enumerate(columns):
                    if is_test and i==0:
                        ground_truth = row[i]
                    else:
                        media_data[col] = row[i]
                yield idx, ground_truth, media_data
                idx += 1
        context.save_nanotasks(template_name, csv_filename.split(".")[0], is_test, int(ticketnum), generate())
