import os
import sys
import re
import subprocess
from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Load the project list file so we can exclude hidden projects
project_list_handle = open(os.path.join(BASE_DIR, "oxford2", "projects.csv"), "r")
project_list_content = project_list_handle.read()
project_list_handle.close()
project_list = project_list_content.split("\n")[:-1]
# load global variables for navtree, page count, and search index
global navtree_html
navtree_html = ''
global page_count
page_count = 0 # For building the search index file search-data.json
global search_file
search_file = '{\n' # The search file text

HREMOVE = re.compile('<.*?>')

def remove_html(input_html):
    cleaned_text = input_html
    cleaned_text = cleaned_text.replace('<p>',' | ')
    cleaned_text = cleaned_text.replace('<br>',' | ')
    cleaned_text = re.sub(HREMOVE, '', cleaned_text)
    cleaned_text = cleaned_text.replace('¶', '')
    cleaned_text = cleaned_text.replace('"', '')
    cleaned_text = cleaned_text.replace('\\', '')
    cleaned_text = cleaned_text.replace('/', '')
    cleaned_text = cleaned_text.replace('\n', ' | ')
    return cleaned_text

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

def push_index(incoming_list): # sort the list so index.html is first
    outgoing_list = []
    is_there_an_index = 0
    for thing in incoming_list:
        if thing != 'index.html':
            outgoing_list.append(thing)
        else:
            is_there_an_index = 1
    if is_there_an_index == 1:
        outgoing_list.insert(0,'index.html')
    return outgoing_list

def generate_navtree(base_directory):
    global navtree_html
    global search_file
    global page_count
    start_dir = os.path.join(BASE_DIR, "oxford2", "artifacts", base_directory)
    print("Generating nav tree...")
    print(start_dir)
    dir_list = sorted(os.listdir(start_dir))
    dir_list = push_index(dir_list) # push index.html to the front
    print(dir_list)
    for thing in dir_list:
        if os.path.isdir(os.path.join(start_dir,thing)):
            print("Directory: " + str(thing))
            new_dir = os.path.join(start_dir,thing)
            print('Now looking into: ' + new_dir)
            # check to see if this directory is for a hidden project
            hidden_project = 0 # default is visible
            for project in project_list:
                project_data = project.split(', ')
                if str(thing) == project_data[0]: # first, find the right project
                    if project_data[7] == "False": # is it marked not visible?
                        print("*** HIDDEN PROJECT DIRECTORY! ****")
                        hidden_project = 1
            if new_dir.find('..') == -1 and hidden_project == 0: # don't go back recursively, avoid hidden
                generate_navtree(new_dir) # recursively walk through the directories
        else:
            print("File: " + str(thing))
            # Make sure to skip the navtree file itself, and all image files
            if thing != 'navtree.html' and thing.find('.png') == -1 and thing.find('.jpg') == -1 and thing.find('#') == -1: 
                page_handle = open(start_dir + "/" + thing, 'r')
                page_content = page_handle.read()
                page_handle.close()
                page_url = os.path.join(start_dir, thing)
                print('Full path: ' + page_url)
                stub_path = os.path.join(BASE_DIR, "oxford2", "artifacts")
                page_url = page_url.replace(stub_path, '')
                # Check if it's an index file or a sub-file
                if thing.find('index.html') == -1:
                    print("It's a page!")
                    page_title = find_snippets(page_content, '<h1>', '<a')[0]
                    print("Page title: " + page_title)
                    # Clean page content and make one line for building search index
                    search_content = remove_html(page_content)
                    search_file += '"' + str(page_count) + '": {\n'
                    search_file += '    "doc": "' + page_title + '",\n'
                    search_file += '    "title": "' + page_title + '",\n'
                    search_file += '    "content": "' + search_content + '",\n'
                    search_file += '    "url": "' + page_url + '",\n'
                    search_file += '    "relUrl": "' + page_url +'"\n'
                    search_file += '    },\n'
                    page_count += 1
                    navtree_html += '<li><a href="' + page_url + '">' + page_title + '</a></li>\n'
                else:
                    print("It's a subfolder!")
                    folder_title = find_snippets(page_content, '<h1>', '<a')[0]
                    print("Folder title: " + folder_title)
                    navtree_html += '<li><span class="caret" id="' + page_url + '">' + folder_title + '</a></span>\n'
                    navtree_html += '<ul class="nested">\n'
                #print('Adding to navtree: ' + navtree_adding)
            else:
                print('Skipping file...')
    print('Finished directory, moving on...')
    navtree_html += '</ul>\n'

navtree_html += '<ul id="myUL">\n'
navtree_html += '<li><span class="caret" id="allservices">All services</span>\n'
navtree_html += '<ul class="nested">'
generate_navtree('')
navtree_html += '</li>\n'
navtree_html += '</ul>\n'
print('All done!')
print('Saving to navtree.html...')
nav_file_handle = open(os.path.join(BASE_DIR, "oxford2", "artifacts", "navtree.html"), 'w')
nav_file_handle.write(navtree_html)
nav_file_handle.close()
#print(navtree_html)
search_file += "}\n"
# fix final trailing comma
search_file = search_file.replace('    },\n}\n','    }\n}\n')
#print(search_file)
search_file_handle = open(os.path.join(BASE_DIR, "oxford2", "static", "oxford2", "search-data.json"), "w")
search_file_handle.write(search_file)
search_file_handle.close()

# debugging
print(project_list)
