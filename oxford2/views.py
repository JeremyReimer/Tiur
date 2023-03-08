import os
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.shortcuts import redirect
from .models import Project

def index(request):
    response = redirect('/misc/latest')
    return response

def pageview(request, page_url):
    project_list = Project.objects.order_by('name')
    template = loader.get_template('oxford2/index.html')
    page_url_full = os.path.join(settings.BASE_DIR, 'oxford2', 'artifacts', page_url, 'index.html')
    try: 
      with open(page_url_full, "r", encoding="utf-8") as f:
          page_content = f.read() 
    except:
      page_content = 'No page found at ' + str(page_url_full)
    context = {
       'project_list': project_list,
       'current_project': page_url,
       'page_content': page_content,
    }
    return HttpResponse(template.render(context, request))




