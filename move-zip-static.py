# This is a simple script to copy over static (.js, .css, .png, .jpg) files
# from unzipped Static Zip File projects.
#
# Will be moved into admin.py after testing.

import os
project_name = "client-code-api" # will be taken from function later
working_dir = os.path.join(os.getcwd(), 'oxford2', 'artifacts', project_name, 'latest', 'zip')
destination_dir = os.path.join(os.getcwd(), 'oxford2', 'static', 'oxford2', 'artifacts')
print(working_dir)
files_list = os.listdir(working_dir)
for file in files_list:
    if file.find('.js') != -1  or file.find('.css') != -1 or file.find('.png') != -1 or file.find('.jpg') != -1:
        destination_file = destination_dir + '/' + project_name + "_" + file
        print(destination_file)

