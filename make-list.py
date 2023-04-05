import os
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
