import os
import django
from django.db import connection
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DynamicCrowd.settings')

def run(context):
    path4 = "DynamicCrowd/.projects"
    if not os.path.exists(path4):
        create_file(path4)
    f = open(path4,"r")
    projects = [x[:-1] for x in f.readlines()]
    if context.project_name in projects:
        print("project '{}' already exists".format(context.project_name))
        return
    f.close()

    path1 = "nanotask/templates/{}".format(context.project_name)
    if create_directory(path1):
        create_file("{}/preview.html".format(path1), preview_body)
        create_file("{}/instruction.html".format(path1), instruction_body)
    
    path2 = "scripts/csv/{}".format(context.project_name)
    create_directory(path2)

    path3 = "settings/projects" #{}.json".format(context.project_name)
    if not os.path.exists(path3):
        create_directory(path3)
    create_file("{}/{}.json".format(path3,context.project_name), settings_body)

    f = open(path4,"a")
    f.write(context.project_name+"\n")
    f.close()

    django.setup()
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE {};".format(context.project_name))
    connection.close()
    os.system("python manage.py migrate --database {}".format(context.project_name))

def directory_exists(dirpath):
    if os.path.exists(dirpath):
        return True
    else:
        print("ERROR: project directory {} does not exist.".format(dirpath))
        return False

def create_directory(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
        return True
    else:
        print("CAUTION: skipped creating directory {} because it already exists.".format(dirpath))
        return False

def create_file(filepath,body=None):
    if not os.path.exists(filepath):
        f = open(filepath,"a")
        if body:
            f.write(body)
        f.close()
        return True
    else:
        print("CAUTION: skipped creating file {} because it already exists.".format(filepath))
        return False

preview_body = '''My project preview is written here in HTML.'''

instruction_body = '''My project instruction is written here in HTML.'''

settings_body = '''{
	"AMT": {
		"FrameHeight": 600,
		"HITParams": {
			"MaxAssignments": 1,
			"LifetimeInSeconds": 36000,
			"AutoApprovalDelayInSeconds": 600,
			"AssignmentDurationInSeconds": 300,
			"Reward": "0.05",
			"Title": "Test HIT",
			"Keywords": "this, is, a, test, HIT",
			"Description": "This is a test HIT"
		}
	},
	"DynamicCrowd": {
        "Title": "My First DynamicCrowd Project",
		"NanotasksPerHIT": 10,
		"AnswersPerNanotask": 3
	}
}
'''
