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

def pageview(request, page_url, page, directory=''):
    project_list = Project.objects.order_by('name')
    template = loader.get_template('oxford2/index.html')
    page_url_full = os.path.join(settings.BASE_DIR, 'oxford2', 'artifacts', page_url, directory, page)
    nav_url_full = os.path.join(settings.BASE_DIR, 'oxford2', 'artifacts', 'navtree.html')
    try: 
      with open(page_url_full, "r", encoding="utf-8") as f:
          page_content = f.read() 
    except:
      page_content = 'No page found at ' + str(page_url_full)
    # load navtree
    try:
      with open(nav_url_full, "r", encoding="utf-8") as n:
          nav_content = n.read()
    except:
          nav_content = 'Unable to load navigation tree.'
    # figure out which folders to click open to display current page in navbar
    click_list = 'var testloadbtn = document.getElementById("/auth3/latest/index.html");\n'
    click_list += 'testloadbtn.click()\n'
    click_list += 'var testloadbtn2 = document.getElementById("/auth3/latest/overview/index.html");\n'
    click_list += 'testloadbtn2.click()\n'

    context = {
       'project_list': project_list,
       'current_project': page_url,
       'page_content': page_content,
       'nav_content': nav_content,
       'click_list': click_list,
    }
    return HttpResponse(template.render(context, request))




