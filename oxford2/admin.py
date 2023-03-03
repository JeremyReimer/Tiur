from django.contrib import admin
from django.core import serializers
from django.http import HttpResponse

import jenkins
import requests
import subprocess

# Functions related to collecting documents start below

def runcmd(cmd, verbose = False, *args, **kwargs):


    process = subprocess.Popen(
        cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
        shell = True
    )
    std_out, std_err = process.communicate()
    if verbose:
        print(std_out.strip(), std_err)
    pass

def make_scrape_cmd(user, api_token, artifact_directory, artifact_url, artifact_file):
    command = 'wget -P ' + artifact_directory + ' --auth-no-challenge --user=' + user + ' --password=' + api_token + ' ' + artifact_url + artifact_file
    return command

def strip_extraneous(text_string):
    start_string = '<div role="main" class="document" itemscope="itemscope" itemtype="http://schema.org/Article">'
    end_string = '<footer>'
    start_num = text_string.find(start_string)
    end_num = text_string.find(end_string)
    text_stripped = text_string[start_num:end_num]
    return text_stripped

def find_images(text_string, sub_string, end_string):
    text_start = 0
    images_list = []
    strip_string = '<img alt="'
    while True:
        text_start = text_string.find(sub_string, text_start)
        if text_start == -1:
            break
        text_end = text_string.find(end_string, text_start + 1)
        text_snippet = text_string[text_start:text_end]
        text_snippet = text_snippet[len(strip_string):] # take out img tag
        images_list.append(text_snippet)
        text_start = text_end + len(end_string)
    return images_list



from .models import Category
from .models import BuildType
from .models import ParserType
from .models import Project
from .models import NavTreeItem
from .models import Version
from .models import Config

admin.site.register(Category)
admin.site.register(BuildType)
admin.site.register(ParserType)
#admin.site.register(Project)
admin.site.register(NavTreeItem)
admin.site.register(Version)
admin.site.register(Config)

@admin.action(description='Collect latest docs for selected projects')
def collect_docs(modeladmin, request, queryset):
    response = "This is debug text " + "some more text"
    querystring = str(queryset)
    querystring = querystring.replace(">","]")
    querystring = querystring.replace("<","[")
    response = response + querystring
    print(request)
    print(queryset)
    # collect the docs for the current project(s)
    return HttpResponse(response)

class ProjectAdmin(admin.ModelAdmin):
    project_list = []
    actions = [collect_docs]

admin.site.register(Project, ProjectAdmin)
