from django.contrib import admin

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
admin.site.register(Project)
admin.site.register(NavTreeItem)
admin.site.register(Version)
admin.site.register(Config)
