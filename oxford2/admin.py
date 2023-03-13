from django.contrib import admin
from django.core import serializers
from django.http import HttpResponse
from .models import Category
from .models import BuildType
from .models import ParserType
from .models import Project
from .models import NavTreeItem
from .models import Version
from .models import Config
#import jenkins
#import requests
import subprocess
import os
import dotenv
from dotenv import load_dotenv
from pathlib import Path

admin.site.register(Category)
admin.site.register(BuildType)
admin.site.register(ParserType)
#admin.site.register(Project)
admin.site.register(NavTreeItem)
admin.site.register(Version)
admin.site.register(Config)


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

def find_snippets(text_string, sub_string, end_string):
    text_start = 0
    snippets_list = []
    while True:
        text_start = text_string.find(sub_string, text_start)
        if text_start == -1:
            break
        text_end = text_string.find(end_string, text_start + 1)
        text_snippet = text_string[text_start:text_end]
        text_snippet = text_snippet[len(sub_string):] # take out opening tag
        snippets_list.append(text_snippet)
        text_start = text_end + len(end_string)
    return snippets_list

def get_sub_directory(input_directory):
    dir_length = len(input_directory)
    last_separator = dir_length
    for idx,c in enumerate(reversed(input_directory)):
        if c == '/':
            last_separator = (dir_length - idx) # iterating through string in reverse order
            break
    final_dir = input_directory[:last_separator]
    return final_dir

def scrape_docs(JENKINS_USER, JENKINS_TOKEN, artifact_directory, collect_url, artifact_file):
    command = make_scrape_cmd(JENKINS_USER, JENKINS_TOKEN, artifact_directory, collect_url, artifact_file)
    # debugging
    print("Downloading " + artifact_file)
    print(" into " + artifact_directory)
    print(" from " + collect_url)
    # check if this directory exists, otherwise create it
    if os.path.isdir(artifact_directory):
        print("Directory exists!")
    else:
        os.mkdir(artifact_directory)
    run_cmd(command)
    # strip headers
    file_handle = open(artifact_directory + '/' + artifact_file, 'r')
    file_raw_text = file_handle.read()
    file_stripped_text = strip_extraneous(file_raw_text)
    file_handle.close()
    # get image list
    image_list = find_snippets(file_stripped_text, '<img alt="', '" ')
    # Replace image URLs
    file_stripped_text = file_stripped_text.replace('_images/', '/static/oxford2/artifacts/')
    # Save the stripped file back to where it was
    file_handle = open(artifact_directory + '/' + artifact_file, 'w')
    file_handle.write(file_stripped_text)
    file_handle.close()
    # get internal link list
    link_list = find_snippets(file_stripped_text, '<a class="reference internal" href="', '">')
    # return confirmation (debugging for now)
    return_message = "Scraped: " + artifact_file + " from " + collect_url
    return_message += " Image list: " + str(image_list)
    return_message += " Link list: " + str(link_list)
    # Remove any bad links. Bad links are images that link to themselves, or links to pages
    # that have already been downloaded. We don't want to have them in our list.
    clean_list = [] # Make a blank list to copy into
    for test_link in link_list:
        print("Checking link: " + test_link)
        if (test_link.find('.png') == -1 and test_link.find('.jpg') == -1 and test_link.find('#') == -1):
            clean_list.append(test_link)
        else:
            print("Found bad link: " + test_link)
    if len(clean_list) > 0:
        # If there are items in the cleaned link list, download them
        for link in clean_list:
            print(link)
            # Need to extract any subdirectory information from each link
            artifact_directory = get_sub_directory(link)
            # Call the function recursively (WARNING: may run endlessly if there's a link to earlier page)
            scrape_docs(JENKINS_USER, JENKINS_TOKEN, artifact_directory, collect_url, link)
    else:
        print("All done!")
    return return_message

@admin.action(description='Collect latest docs for selected projects')
def collect_docs(modeladmin, request, queryset):
    response = "Collecting data for projects..."
    # get name and URL for project downloading
    project_name = queryset.values_list('name')[0][0]
    collect_url = queryset.values_list('artifact_url')[0][0]
    # collect docs from URL and save to artifacts directory
    artifact_directory = os.path.join(BASE_DIR, "oxford2", "artifacts", project_name)
    artifact_file = "index.html" # temporary
    # run scraping function
    scrape_message = scrape_docs(JENKINS_USER, JENKINS_TOKEN, artifact_directory, collect_url, artifact_file) 
    response = response + scrape_message
    return HttpResponse(response)

class ProjectAdmin(admin.ModelAdmin):
    project_list = []
    actions = [collect_docs]

admin.site.register(Project, ProjectAdmin)
