import os
from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print("BASE DIRECTORY: " + str(BASE_DIR))
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tiur.settings")
django.setup()
from oxford2.models import Category
from oxford2.models import Project
category_list = []
for category in Category.objects.all():
    category_list.append(category)
    project_list = Project.objects.filter(category=category).order_by("weight")
    print("Category: " + str(category) + " Projects: " + str(project_list))
    for project in project_list:
        print("Project name: " + str(project.display_name))
print(category_list)
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

