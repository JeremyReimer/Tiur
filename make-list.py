# This script builds a list of projects and categories, and then generates
# the file navtree.html which is the left-hand nav panel
# It also generates the search file search-data.json
import os
import sys
import re
from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print("BASE DIRECTORY: " + str(BASE_DIR))
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tiur.settings")
django.setup()
from oxford2.models import Category
from oxford2.models import Project
from oxford2.models import NavTreeItem
global category_list
category_list = []
project_file = "" # will save a list of projects to projects.csv
for project in Project.objects.all():
    project_data = project.name + ", "
    project_data += project.display_name + ", "
    project_data += str(project.build_type) + ", "
    project_data += str(project.parser) + ", "
    project_data += str(project.category) + ", "
    project_data += project.artifact_url + ", "
    project_data += str(project.weight) + ", "
    project_data += str(project.visible) + ", "
    project_data += str(project.active)
    print(project_data)
    project_file += project_data + "\n"
# save project file
save_file = os.path.join(BASE_DIR, "tiur", "oxford2", "projects.csv")
print("Saving file to: " + str(save_file))
save_file_handle = open(save_file, "w")
save_file_handle.write(project_file)
save_file_handle.close()

# Now generate the navtree

# Load the project list file so we can exclude hidden projects
project_list_handle = open(os.path.join(BASE_DIR, "tiur", "oxford2", "projects.csv"), "r")
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

def add_category_view(base_directory):
    global navtree_html
    global category_list
    # This adds an optional category-based view of projects
    navtree_html += '<li><span class="caret" id="allservices">Categories</span>\n'
    navtree_html += '<ul class="nested">'
    for category in Category.objects.all().order_by("display_name"):
        #category_list.append(category)
        cat_project_list = Project.objects.filter(category=category).order_by("weight")
        print("Category: " + str(category))
        navtree_html += '<li><span class="caret" id="allservices">' + str(category) + '</span>\n'
        navtree_html += '<ul class="nested">'
        for project in cat_project_list:
            print("-- Project: " + str(project.display_name))
            page_file_name = os.path.join(BASE_DIR, "tiur", "oxford2", "artifacts", str(project.name), "latest", "index.html")
            print("Need to load file: " + str(page_file_name))
            page_file_handle = open(page_file_name, "r")
            page_file_handle_content = page_file_handle.read()
            #print(page_file_handle_content)
            page_file_first_link = find_snippets(page_file_handle_content,'<a class="reference internal" href="', '">')[0]
            print('First link:' + str(page_file_first_link))   
            page_file_full_link = str(project.name) + '/latest/' + page_file_first_link
            print("Link to file: " + str(page_file_full_link))
            page_file_handle.close()
            if page_file_first_link.find('index.html') != -1: # If it's an index file, go one level deeper
                next_file_name = os.path.join(BASE_DIR, "tiur", "oxford2", "artifacts", page_file_full_link) 
                print('Grabbing next level of navigation...' + str(next_file_name))
                next_file_handle = open(next_file_name, "r")
                next_file_handle_content = next_file_handle.read()
                next_file_first_link = find_snippets(next_file_handle_content,'<a class="reference internal" href="', '">')[0]
                next_file_first_link = page_file_first_link.replace('index.html','') + next_file_first_link 
            else:
                next_file_first_link = page_file_first_link
            next_file_full_link = '/' + str(project.name) + '/latest/' + next_file_first_link
            print('Final project page link is: ' + str(next_file_full_link))
            next_file_handle.close()
            navtree_html += '<li><a href="' + next_file_full_link + '">' + str(project.display_name) + '</a></li>\n'
        # Now need to add any Navigation Tree Items in this category
        nav_items = NavTreeItem.objects.filter(category=category).order_by("weight")
        for nav_item in nav_items:
            navtree_html += '<li><a href="/' + str(nav_item.project) + '/latest/' + str(nav_item.item_url) + '">' + str(nav_item.display_name) + '</a></li>' 
        navtree_html += '</ul></li>'
    navtree_html += '</ul></li>'
    return

def generate_navtree(base_directory):
    global navtree_html
    global search_file
    global page_count
    start_dir = os.path.join(BASE_DIR, "tiur", "oxford2", "artifacts", base_directory)
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
                stub_path = os.path.join(BASE_DIR, "tiur", "oxford2", "artifacts")
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
                    #navtree_html += '<li><a href="' + page_url + '">' + page_title + '</a></li>\n'
                else: # it is an index.html
                    # if the filename is genindex.html, skip it, we don't want to process those index files
                    if thing.find('genindex.html') == -1:
                        print("It's a subfolder!")
                        folder_title = find_snippets(page_content, '<h1>', '<a')[0]
                        # If this folder is a top folder (eg a Project top level) we need to change the title
                        # to be not the actual document title, but the Project title from the database
                        tree_depth = base_directory.count('/')
                        print(">>>>>>>>>>>>>>> DIRECTORY DEPTH: " + str(tree_depth))
                        if tree_depth == 7:
                            print("======== NEW PROJECT FOLDER ===========")
                            folder_dir = str(base_directory.split('/')[-2])
                            project_object_name = Project.objects.get(name=folder_dir).display_name
                            folder_title = project_object_name
                        print("Folder title: " + folder_title)
                        navtree_html += '<li><span class="caret" id="' + page_url + '">' + folder_title + '</a></span>\n'
                        navtree_html += '<ul class="nested">\n'
                        # add all links inside this index.html to the navtree at once
                        inside_index_links = find_snippets(page_content, '<a class="reference internal" href="', '</a></li>')
                        # quick fix for URL (since we're doing it a new way)
                        page_url = page_url.replace('index.html', '')
                        for index_link in inside_index_links:
                            divider = index_link.find('">')
                            index_sub_link = index_link[:divider]
                            index_description = index_link[divider + 2:]
                            print('$$$$$$$$$ Adding page: ' + index_description + ' link: ' + index_sub_link)
                            if index_sub_link.find('index.html') == -1:
                                navtree_html += '<li><a href="' + page_url + index_sub_link + '">' + index_description + '</a></li>\n'
                    #print('Adding to navtree: ' + navtree_adding)
            else:
                print('Skipping file...')
    print('Finished directory, moving on...')
    navtree_html += '</ul></li>\n'
    return

# start of main script
navtree_html += '<ul id="myUL">\n'
navtree_html += '<li><span class="caret" id="allservices">All services</span>\n'
navtree_html += '<ul class="nested">'
generate_navtree('')
add_category_view('') # add the category view to the tree
navtree_html += '</li>\n'
navtree_html += '</ul>\n'
# Quick fix for excess close tags, will fix properly later
navtree_html = navtree_html.replace('</ul></li>\n</ul></li>\n</ul></li>\n', '</ul></li>\n</ul></li>\n')
print('All done!')
print('Saving to navtree.html...')
nav_file_handle = open(os.path.join(BASE_DIR, "tiur", "oxford2", "artifacts", "navtree.html"), 'w')
nav_file_handle.write(navtree_html)
nav_file_handle.close()
#print(navtree_html)
search_file += "}\n"
# fix final trailing comma
search_file = search_file.replace('    },\n}\n','    }\n}\n')
#print(search_file)
search_file_handle = open(os.path.join(BASE_DIR, "tiur", "oxford2", "static", "oxford2", "search-data.json"), "w")
search_file_handle.write(search_file)
search_file_handle.close()

# debugging
#print(navtree_html)
