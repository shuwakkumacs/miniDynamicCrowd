import boto3
from IPython import embed

#endpoint_url = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
endpoint_url = "https://mturk-requester.us-east-1.amazonaws.com"

client = boto3.client('mturk',
            aws_access_key_id = "AKIAIBSZJU54MMGSC5OQ",
            aws_secret_access_key = "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",
            region_name = "us-east-1",
            endpoint_url = endpoint_url
)

#client.notify_workers(Subject='Invitation to compensation HIT',MessageText='Dear workers,\n\nOur HITs that you kindly worked on recently, named "Can you see the root of cow\'s tail?", the HIT(s) had not been properly submitted due to program bugs and therefore you were not paid properly.\nRegarding this, we would like to invite you to our compensation HIT -- please visit the HIT page below and just submit it, so that we can pay you the reward (this HIT can only submitted once):\nhttp://www.mturk.com/mturk/preview?groupId=3H5KS3F36Q9DMMOITMDYIIRCV3SYZO\n\nAgain, we apologize for the confusion and thank you very much for your kind cooperation.\n\nSincerely,\nTeppei',WorkerIds=["A127A2KRPBCOOK" ,"A13AA4ZKU2F2D0" ,"A13ODGEOEI0FCS" ,"A13RSZ2S04QV8J" ,"A16U5PX0QOHAFC" ,"A19LVWX8ZLO6CS" ,"A1ESKJFDQUMBL4" ,"A1ND9FU7OO5NQA" ,"A1NGUA9CRQEZCY" ,"A1QYORNO0GY308" ,"A1W06GIYOJMSAK" ,"A1WF1X8PQQJ2OQ" ,"A1ZZINLCZZYOH4" ,"A2A6JQABXWH9ID" ,"A2CCNSS33U3099" ,"A2GDE2EZTHMC4V" ,"A2IP5E5ITPEVPU" ,"A2N40EI5N9PX08" ,"A2S82Z2HC3HURZ" ,"A2SJKQXUUNQ87H" ,"A2SY89U2BZADGD" ,"A2VHNGVWAY4O3U" ,"A2Y9NTHSK2ZPBM" ,"A2YRYS17DU3A8R" ,"A2Z771QD4Z0D00" ,"A357C0NLWK75L0" ,"A37IIW0U49DKGP" ,"A3B0M28EYT4K6" ,"A3EO2DPEN9JYC8" ,"A3J0X7ZQAXLFPI" ,"A3MTARDZ80DNV8" ,"A3PHTY8E5TZS3H" ,"A3PIQY6PK42RIS" ,"A3S27CHX6ACLUO" ,"A3SIYZQYIHULPB" ,"A4H1NYJVE7C53" ,"AEF601SQFOSBL" ,"AKK2BPA71TA3M" ,"AKX2W7899TSSJ" ,"ANE2RBRS18K60" ,"AO2MNZUGWB5W9" ,"APMGE1034C1LB" ,"ASZ56AVQ9MQUK" ,"AVATI6877P5BN"])
print(client.notify_workers(Subject='Invitation to compensation HIT',MessageText='Dear workers,\n\nOur HITs that you kindly worked on recently, named "Can you see the root of cow\'s tail?", the HIT(s) had not been properly submitted due to program bugs and therefore you were not paid properly.\nRegarding this, we would like to invite you to our compensation HIT -- please visit the HIT page below and just submit it, so that we can pay you the reward (this HIT can only submitted once):\nhttp://www.mturk.com/mturk/preview?groupId=3H5KS3F36Q9DMMOITMDYIIRCV3SYZO\n\nAgain, we apologize for the confusion and thank you very much for your kind cooperation.\n\nSincerely,\nTeppei',WorkerIds=["A2GDE2EZTHMC4V"]))
