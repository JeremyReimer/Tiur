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
    print('Executing command: ' + command)
    return command

def make_scrape_zip_cmd(user, api_token, artifact_directory, artifact_url, artifact_file):
    # same as above, but don't add the filename at the end, as it's part of the URL
    command = 'wget -O ' + artifact_directory + '/' + artifact_file + ' -P ' + artifact_directory + ' --auth-no-challenge --user=' + user + ' --password=' + api_token + ' ' + artifact_url
    print('Executing command: ' + command)
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
    if last_separator == len(input_directory):
        final_dir = ''
        final_filename = input_directory
    else: 
        final_dir = input_directory[:last_separator]
        final_filename = input_directory[last_separator:]
    return final_dir, final_filename

def check_existing_dirs(check_directory):
   # check if this directory exists, otherwise create it
    if os.path.isdir(check_directory):
        print("Directory exists!")
    else:
        print("Creating directory...")
        os.makedirs(check_directory) # makedirs in case multiple subfolders at once
    return

def scrape_static_zip(JENKINS_USER, JENKINS_TOKEN, project_name, incoming_directory, incoming_url, artifact_file):
    artifact_file = project_name + ".zip" # For .zip files, rename the file for later extraction
    # debugging
    print("Downloading " + artifact_file)
    print("Project name: " + project_name)
    print(" into " + incoming_directory)
    print(" from " + incoming_url)
    check_existing_dirs(incoming_directory)
    command = make_scrape_zip_cmd(JENKINS_USER, JENKINS_TOKEN, incoming_directory, incoming_url, artifact_file)
    run_cmd(command) # Download the zip file
    return_message = "Downloaded .zip file..."
    # extract .zip file into a new directory
    unzip_dir = incoming_directory + "/zip"
    check_existing_dirs(unzip_dir)
    unzip_cmd = "unzip " + incoming_directory + "/" + project_name + ".zip -d " + unzip_dir
    run_cmd(unzip_cmd) # unzip the file
    return return_message

def scrape_docs(JENKINS_USER, JENKINS_TOKEN, project_name, incoming_directory, incoming_url, artifact_file):
    command = make_scrape_cmd(JENKINS_USER, JENKINS_TOKEN, incoming_directory, incoming_url, artifact_file)
    # debugging
    print("Downloading " + artifact_file)
    print(" into " + incoming_directory)
    print(" from " + incoming_url)
    check_existing_dirs(incoming_directory)
    run_cmd(command)
    # strip headers
    file_handle = open(incoming_directory + '/' + artifact_file, 'r')
    file_raw_text = file_handle.read()
    file_stripped_text = strip_extraneous(file_raw_text)
    file_handle.close()
    # get image list
    image_list = find_snippets(file_stripped_text, '<img alt="', '" ')
    # Replace image URLs (add project name to front of image link to avoid duplicates)
    file_stripped_text = file_stripped_text.replace('_images/', '/static/oxford2/artifacts/' + project_name + '_')
    # Save the stripped file back to where it was
    file_handle = open(incoming_directory + '/' + artifact_file, 'w')
    file_handle.write(file_stripped_text)
    file_handle.close()
    # Create images subdirectory if it doesn't exist
    if os.path.isdir(incoming_directory + '/_images'):
        print("Image directory exists!")
    else:
        print("Creating image directory...")
        os.mkdir(incoming_directory + '/_images')
    # Download all images on this page
    for image_link in image_list:
        print("Downloading image: " + image_link)
        image_dl_cmd = make_scrape_cmd(JENKINS_USER, JENKINS_TOKEN, incoming_directory, incoming_url, image_link)
        run_cmd(image_dl_cmd)
        # copy image into Oxford's static image directory
        raw_image_filename = image_link.replace('_images/','')
        cp_cmd = "cp " + incoming_directory + image_link + " " +  os.path.join(BASE_DIR, "oxford2", "static", "oxford2", "artifacts") + '/' + project_name + "_" + raw_image_filename
        print("Copying image to static directory... ")
        run_cmd(cp_cmd)
    # get internal link list
    link_list = find_snippets(file_stripped_text, '<a class="reference internal" href="', '">')
    # return confirmation (debugging for now)
    return_message = "Scraped: " + artifact_file + " from " + incoming_url
    return_message += " Image list: " + str(image_list)
    return_message += " Link list: " + str(link_list)
    # Remove any bad links. Bad links are images that link to themselves, or links to pages
    # that have already been downloaded, or a parent directory (..) We don't want to have them in our list.
    clean_list = [] # Make a blank list to copy into
    for test_link in link_list:
        print("Checking link: " + test_link)
        if (test_link.find('.png') == -1 and test_link.find('.jpg') == -1 and test_link.find('#') == -1 and test_link.find('..') == -1):
            clean_list.append(test_link)
        else:
            print("Found bad link: " + test_link)
    if len(clean_list) > 0:
        print("Running through list of links...")
        # If there are items in the cleaned link list, download them
        for link in clean_list:
            print(link)
            # Need to extract any subdirectory information from each link
            file_and_directory = get_sub_directory(link)
            artifact_relative_directory = file_and_directory[1]
            # now combine this path with the incoming directory plus the relative link
            artifact_directory = incoming_directory + '/' + file_and_directory[0] 
            artifact_file = file_and_directory[1]
            collect_url = incoming_url + file_and_directory[0]
            # Call the function recursively (WARNING: may run endlessly if there's a link to earlier page)
            scrape_docs(JENKINS_USER, JENKINS_TOKEN, project_name, artifact_directory, collect_url, artifact_file)
    else:
        print("All done!")
    return_message += "\n<p>Click <a href='/admin'> here</a> to return to the Admin page.</p>"
    return return_message

@admin.action(description='Collect latest docs for selected project')
def collect_docs(modeladmin, request, queryset):
    response = "Collecting data for project..."
    # get name, project type, and URL for project downloading
    project_name = queryset.values_list('name')[0][0]
    project_type = queryset.values_list('parser')[0][0]
    collect_url = queryset.values_list('artifact_url')[0][0]
    # remove extraneous index.html from the URL if it exists
    collect_url = collect_url.replace('index.html','')
    # first, make sure the project base directory exists
    artifact_base_directory = os.path.join(BASE_DIR, "oxford2", "artifacts", project_name)
    if os.path.isdir(artifact_base_directory):
        print("Directory exists!")
    else:
        print("Creating directory...")
        os.makedirs(artifact_base_directory) # makedirs in case multiple sublevels exist at once
    # collect docs from URL and save to project directory under "latest"
    artifact_directory = os.path.join(BASE_DIR, "oxford2", "artifacts", project_name, "latest")
    artifact_file = "index.html" # temporary
    print('--------------------------------------------------')
    print('Project type: ' + str(project_type))
    # Begin scraping, but only if it's a "Sphinx" project type
    scrape_message = 'Did not collect docs. Check logs for details.'
    if (project_type == 1): # this is regular HTML Sphinx Doc
        scrape_message = scrape_docs(JENKINS_USER, JENKINS_TOKEN, project_name, artifact_directory, collect_url, artifact_file) 
    if (project_type == 2): # this is Static Zipped Doc
        scrape_message = "Retrieving Static Zipped Doc.."
        scrape_message += scrape_static_zip(JENKINS_USER, JENKINS_TOKEN, project_name, artifact_directory, collect_url, artifact_file)
    response = response + scrape_message
    # generate navtree and searchfile
    run_cmd('python3 ' + os.path.join(BASE_DIR, "make-list.py"), Verbose=1) # run separate command to generate these
    # finish everything, return
    return HttpResponse(response)

class ProjectAdmin(admin.ModelAdmin):
    project_list = []
    actions = [collect_docs]

admin.site.register(Project, ProjectAdmin)
