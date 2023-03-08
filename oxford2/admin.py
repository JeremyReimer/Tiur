from django.contrib import admin
from django.core import serializers
from django.http import HttpResponse

import jenkins
import requests
import subprocess
import os
import dotenv
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Load secret environment variable keys
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    load_dotenv(dotenv_file)
JENKINS_USER = os.environ.get('JENKINS_USER', "default_value")
JENKINS_TOKEN = os.environ.get('JENKINS_TOKEN', "default_value")

# Functions related to collecting documents start below

def run_cmd(cmd, verbose = False, *args, **kwargs):


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
    command = 'wget -O ' + artifact_directory + '/' + artifact_file + ' -P ' + artifact_directory + ' --auth-no-challenge --user=' + user + ' --password=' + api_token + ' ' + artifact_url + artifact_file
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
    # debug code
    querystring = str(queryset)
    querystring = querystring.replace(">","]")
    querystring = querystring.replace("<","[")
    response = response + querystring
    # get name and URL for project downloading
    project_name = queryset.values_list('name')[0][0]
    collect_url = queryset.values_list('artifact_url')[0][0]
    # collect docs from URL and save to artifacts directory
    artifact_directory = os.path.join(BASE_DIR, "oxford2", "artifacts", project_name)
    artifact_file = "index.html" # temporary
    command = make_scrape_cmd(JENKINS_USER, JENKINS_TOKEN, artifact_directory, collect_url, artifact_file)
    run_cmd(command)
    # strip headers
    file_handle = open(artifact_directory + '/' + artifact_file, 'r')
    file_raw_text = file_handle.read()
    file_stripped_text = strip_extraneous(file_raw_text)
    file_handle.close()
    # Replace image URLs
    file_stripped_text = file_stripped_text.replace('_images/', '/static/oxford2/artifacts/')
    # Save the stripped file back to where it was
    file_handle = open(artifact_directory + '/' + artifact_file, 'w')
    file_handle.write(file_stripped_text)
    file_handle.close()
    return HttpResponse(response)

class ProjectAdmin(admin.ModelAdmin):
    project_list = []
    actions = [collect_docs]

admin.site.register(Project, ProjectAdmin)
