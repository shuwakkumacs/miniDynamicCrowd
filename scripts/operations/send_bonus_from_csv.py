import os
import csv
import sys

import concurrent.futures
import boto3

from django.utils import timezone

from nanotask.models import *

def run(context):
    context.parser.add_argument("csv_filename", help="CSV file name")
    context.parser.add_argument("--production", help="Production mode (non-sandbox)", action="store_false")
    args = context.parser.parse_args()
    is_sandbox = args.production
    csv_filename = args.csv_filename

    client = context.get_mturk_client(is_sandbox)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    with open("./scripts/csv/{}/{}".format(context.project_name,csv_filename)) as f:
        reader = csv.reader(f, delimiter=",", quotechar="'")
        for row in reader:
            #executor.submit(send_bonus,row)
            send_bonus(client,row)

def send_bonus(client,row):
    mturk_assignment_id = row[0]
    reward = float(row[1])
    amt_assignment = AMTAssignment.objects.filter(mturk_assignment_id=mturk_assignment_id).first()
    if amt_assignment:
        if amt_assignment.bonus_amount != 0.0:
            print("{}, ${:.2f} skipped (already paid)".format(mturk_assignment_id,reward))
        else:
            try:
                client.send_bonus(WorkerId=amt_assignment.mturk_worker_id,
                                  BonusAmount=str(reward),
                                  AssignmentId=mturk_assignment_id,
                                  Reason='We are sending you a bonus of ${:.2f}. We sincerely apologize for the confusion and thank you very much again for your kind cooperation!'.format(reward))
                amt_assignment.bonus_amount = reward
                amt_assignment.time_bonus_sent = timezone.now()
                amt_assignment.save()
                print("{}, ${:.2f} success".format(mturk_assignment_id,reward))
            except Exception as e:
                print("{}, ${:.2f} failed: {}".format(mturk_assignment_id,reward,e))
    else:
        print("{}, ${:.2f} failed: doesn't exist in AMTAssignment record".format(mturk_assignment_id,reward))
