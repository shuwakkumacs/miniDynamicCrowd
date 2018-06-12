# miniDynamicCrowd <font size="3">(v0.2, last update in 2018-05-13)</font>

## Notation

* **nanotask** ... a small microtask that is dynamically loaded and drawn in HIT
* **\<container_name>** ... Docker container name you specify
* **\<project_name>** ... DynamicCrowd project name you specify (<font color="red">Caution:</font> this is not a Django project name)
* **\<template_name>** ... Nanotask template name you specify (<font color="red">Caution:</font> this is not a Django template name)
* **\<subdomain>** ... a name that becomes a part of a webroot, followed by ".r9n.net"
* **\<web_root>** ... a base url to a web server running in a docker container which can be accessed externally (i.e., "http://\<subdomain>.r9n.net")

## Tutorial

### 1. Pull docker image and start a container

On the host server (e.g., a01):

$ docker pull shuwakkuma/dynamiccrowd
$ docker run -it --name <container_name> -d shuwakkuma/dynamiccrowd

#### (1-2. Creating a new user and a database on MySQL DB)

**There's currently no good solution but directly creating a user and a database in MySQL console (to be solved soon)**.
MySQL server instance is located in one of docker containers, called "mysqld_dc", and you can access as a root user through phpMyAdmin. Just visit on your browser `https://myadmin.r9n.net`. Otherwise, you can log in on the a01 console by hitting:

$ mysql -h 172.17.0.1 -u root -P 13306 -p

After creating them, do the followings on the host server:


### 2. Link the docker container to webroot

#### 2-1. Register your subdomain to Cloudflare DNS

Go to [https://dash.cloudflare.com/login](https://dash.cloudflare.com/login) and log in.

Then navigate to r9n.net -> DNS, then register as follows:

<table>
<tr><th>Type</th><th>Name</th><th>Value</th><th>TTL</th><th>Status</th></tr>
<tr><td>A</td><td>&lt;subdomain></td><td>points to 133.9.84.27</td><td>Automatic</td><td>go through (orange cloud)</td></tr>
</table>

After setting above, go to `https://<subdomain_name>.r9n.net` (i.e., `<web_root>`) in a web browser and make sure that you get 502 Error of Cloudflare CDN.

#### 2-2. Link the webroot to Nginx route

On the host server:

$ sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' <container_name>
172.17.0.8            # <- remember this
$ cd /etc/nginx/sites-available
$ touch <subdomain>

Then edit the file as follows:

server {
listen 80;
listen 443 ssl;

server_name <subdomain>.r9n.net;

location / {
proxy_set_header Host $http_host;
proxy_pass http://172,.17.0.8/;     # your docker container IP address
}

}

After setting above, visit `<web_root>` in a web browser and make sure that you get Nginx default start page.

#### 2-3. Check if Django app is linked to the webroot

On the **docker container**:

$ cd ~/DynamicCrowd
$ python manage.py runserver 0:80

Then visit `<web_root>` in a web browser and make sure that you get Django error page.

### 3. Start a default DynamicCrowd project

On the docker container:

$ cd ~/DynamicCrowd
$ python scripts/dynamiccrowd.py operations.create_project myproject   # create a project named "myproject"
$ python scripts/dynamiccrowd.py operations.create_template myproject mytemplate   # create a template named "mytemplate"
$ python scripts/dynamiccrowd.py operations.create_nanotasks_from_csv myproject mytemplate   # register nanotasks to DB

Then visit `<webroot>/nanotask/myproject/` to view a preview page, and add a query like `<webroot>/nanotask/myproject/?assignmentId=test` to enter a worker demo mode.

As you answer to a nanotask in the demo mode, proceed to the next task and so on, the pulled nanotasks are flagged with a worker's ```workerId``` (in this case, "PREVIEW_WORKER") so that the task is not reserved by any other worker on-line at the same time.
When the number of nanotasks you worked on exceeds ```NanotasksPerHIT``` specified to the project, all the answers are saved in the DB.

### 4. Create HITs (not tested)

$ cd ~

Open ```settings.json``` and edit parameters in ```AMT``` as well as ```DynamicCrowd->AnswersPerNanotask```. 

<font color="red">Caution:</font> When you are trying to just test the template, make sure ```Sandbox``` is set to true.

Then proceed to generate HITs:

$ cd ~/DynamicCrowd
$ python scripts/dynamiccrowd.py create_hits <project_name> <template_name>

DB records named ```Answers``` are created according to 

## Files to configure

Files that need to be edited before nanotasks are published to workers are listed below:

### 1. HTML templates

Navigate to `~/DynamicCrowd/nanotask/templates/<project_name>/`, and make sure that you already created a DynamicCrowd project/template.

There are at least three HTML files you need to edit:

* `<template_name>.html` ... a file for nanotasks with dynamic values on which workers actually work on
* `preview.html` ... a file for a nanotask preview that workers see before they accept your DynamicCrowd project microtask
* `instruction.html` ... a file for common instructions shown to workers on your DynamicCrowd project

#### 1-1. ```<template_name>.html```

This template file can be written using Django Template Language --- the file can contain any "key", any string you specify, inserted anywhere in the code, and they are interpreted as any arbitrary string value you specify in a later step. You can also put some simple condition terms (e.g., if-else, etc.) For further information for notation, see [Django documentation for Django Template Language](https://docs.djangoproject.com/en/2.0/ref/templates/language/).

Here's a sample of a template:

<div id="description">{{ description }}</div>

<div class="media_data"><img src="{{ img_url }}" /></div>

<div id="btns-wrapper">
<button id="answer_1" class="nano-submit" name="choice" value="{{ btn_lbl1 }}">{{ btn_lbl1 }}</button>
<button id="answer_2" class="nano-submit" name="choice" value="{{ btn_lbl2 }}">{{ btn_lbl2 }}</button>
</div>

#### 1-2. ```preview.html``` 

`preview.html` is for a web page displayed to workers before accepting HIT. This is supposed to be something that describes:

* Types of HITs that workers might see during a HIT
* Criteria for answers to each nanotask
* Number of nanotasks workers should complete to submit a HIT and how much it is worth (=Reward amount)

#### 1-3. ```instruction.html```

`instruction.html` is for a general instruction to let workers know what to do on a group of your nanotasks --- this will be automatically shown in a preview page once workers open it, and also can be shown whenever workers hit a "See Instructions" button below the project title. This instruction is expected to include:

* Sentences for task description at a glance
* Samples and/or any other detailed information of your nanotask criteria so that workers can complete without misunderstanding the goal
* A link or a button to report bugs/questions/comments to you

### 2. Dynamic values for nanotasks



#### Edit a csv file

Navigate to `~/DynamicCrowd/scripts/nanotask_csv/<project_name>/`, and make sure that you already created a DynamicCrowd project/template.

Edit ```<template_name>.csv``` to specify all the values corresponding to keys indicated in the template file.

In the first line, list all the keys wrapped by double-quotes ("") and separated by commas.

Here's a sample line of ```<template_name>.csv``` corresponding to the above template:

"description", "img_url", "btn_lbl1", "btn_lbl2"

Then lines, each of which represents values for each nanotask, follows after the top line of ```<template_name>.csv```, also wrapped by double-quotes and separated by commas:

"Does the image contain a jumping dog?", "http://some.url.com/image_a001.jpg", "Yes", "No"
"Does the image contain a jumping dog?", "http://some.url.com/image_a002.jpg", "Yes", "No"
"Does the image contain a jumping dog?", "http://some.url.com/image_a003.jpg", "Yes", "No"
"Does the image contain a jumping cat?", "http://some.url.com/image_b001.jpg", "Yes", "No"

Once you finish editing the csv file, execute the following command to register them in the DB:

$ cd ~/DynamicCrowd
$ python scripts/dynamiccrowd.py create_nanotasks <project_name> <template_name>


### 3. Project setting parameters

Open ```~/settings.json``` and modify ```DynamicCrowd->NanotasksPerHIT``` value to specify the number of nanotasks per HIT.

<font color="red">Caution:</font> Currently no interface for editing ```NanotasksPerHIT``` is implemented.


## Operation commands

### Usage
$ cd ~/DynamicCrowd/
$ python scripts/dynamiccrowd.py operations.<operation_name> <project_name> [args]

<table>
<tr><th>operation_name</th><th>args</th><th>description</th></tr>
<tr><td>create_project</td><td>N/A</td><td>Create a DynamicCrowd project</td></tr>
<tr><td>create_template</td><td>&lt;template_name></td><td>
Create a DynamicCrowd template</td></tr>
<tr><td>create_nanotasks_from_csv</td><td>&lt;template_name></td><td>Register nanotasks to DB by using a CSV batch file</td></tr>
<tr><td>create_hits</td><td>N/A</td><td>Create HITs that covers all nanotasks registered in DB</td></tr>
</table>


# References

* [miniDynamicCrowd Bitbucket repository](https://bitbucket.org/shuwakkumacs/minidynamiccrowd)
* To refer, your account needs to be added as a collaborator since the repo is private
* [miniDynamicCrowd Docker Hub repository](https://hub.docker.com/r/shuwakkuma/dynamiccrowd/)

# Update Logs

#### 2018-05-13
Temporarily added an operations list

#### 2018-04-11
Initial document
