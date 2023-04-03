import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.shortcuts import redirect
from .models import Project
from .models import Config

@login_required
def index(request):
    config_info = Config.objects.all().first().start_page
    if config_info == '/':
       config_info = 'misc/latest' # debugging
    response = redirect(config_info) 
    return response

@login_required
def pageview(request, page_url, page, directory=''):
    project_list = Project.objects.order_by('name')
    footer_text = Config.objects.all().first().footer_message
    template = loader.get_template('oxford2/index.html')
    base_url = os.path.join(settings.BASE_DIR, 'oxford2', 'artifacts')
    page_url_full = os.path.join(settings.BASE_DIR, 'oxford2', 'artifacts', page_url, 'latest', directory, page)
    page_url_partial = page_url_full.replace(base_url, '') # use this for auto clicking on navtree
    page_url_split = page_url_partial.split("/")
    nav_url_full = os.path.join(settings.BASE_DIR, 'oxford2', 'artifacts', 'navtree.html')
    print(page_url_split) # debugging
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
    # Highlight current page in navbar
    print("Current page: " + page_url_partial) # debugging
    nav_content = nav_content.replace('"' + page_url_partial + '"','"' + page_url_partial + '" class=activepage') 
    # figure out which folders to click open to display current page in navbar
    click_list = ''
    for x in range(1, len(page_url_split)-2):
        temp_list = page_url_split[1:x+2]
        temp_string = '/' + '/'.join(temp_list)+'/index.html'
        click_list += 'var testloadbtn' + str(x) + ' = document.getElementById("' + temp_string + '");\n'
        click_list += 'testloadbtn' + str(x) + '.click()\n'
        print(temp_string)

    context = {
       'project_list': project_list,
       'current_project': page_url,
       'page_content': page_content,
       'nav_content': nav_content,
       'click_list': click_list,
       'footer_text': footer_text,
    }
    return HttpResponse(template.render(context, request))




