import copy

settings_common = {
    'ENGINE': 'django.db.backends.mysql',
    "HOST": "127.0.0.1",
    "USER": "root",
    "PASSWORD": "admin"
}

default = copy.deepcopy(settings_common)
default["NAME"] = "information_schema"

db_settings = {
    "default": default
}
    

try:
    f = open("DynamicCrowd/.projects","r")
    projects = list(f.readlines())
    for project in projects:
        project_name = project[:-1] if project[-1]=="\n" else project
        setting = copy.deepcopy(settings_common)
        setting["NAME"] = project_name
        db_settings[project_name] = setting
except FileNotFoundError as e:
    pass
