import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tiur.settings")
django.setup()
from oxford2.models import Category
from oxford2.models import Project
for category in Category.objects.all():
    print(category)
for project in Project.objects.all():
    print(project.display_name)
