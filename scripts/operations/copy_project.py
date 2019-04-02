import os
import django
import shutil
from django.db import connection
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DynamicCrowd.settings')

def run(context):
    context.parser.add_argument("new_project_name", help="New project name")
    args = context.parser.parse_args()
    new_project_name = args.new_project_name
    projects_path = "DynamicCrowd/.projects"
    f = open(projects_path,"r")
    projects = [x[:-1] for x in f.readlines()]
    f.close()
    if context.project_name not in projects:
        print("project {} does not exist".format(context.project_name))
        return
    else:
        f = open(projects_path,"a")
        f.write(new_project_name+"\n")
        f.close()

    path1_src = "nanotask/templates/{}".format(context.project_name)
    path1_dst = "nanotask/templates/{}".format(new_project_name)
    shutil.copytree(path1_src, path1_dst)
    
    path2_src = "scripts/csv/{}".format(context.project_name)
    path2_dst = "scripts/csv/{}".format(new_project_name)
    shutil.copytree(path2_src, path2_dst)

    shutil.copy("settings/projects/{}.json".format(context.project_name), "settings/projects/{}.json".format(new_project_name))

    django.setup()
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE {};".format(new_project_name))
    connection.close()
    os.system("mysqldump -u root -proot {} | mysql -u root -proot {}".format(context.project_name, new_project_name))
