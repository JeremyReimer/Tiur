from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Project

def index(request):
    return HttpResponse("Hello, world! This is Oxford 2.0's index.")

def pageview(request, page_url):
    project_list = Project.objects.order_by('-name')
    template = loader.get_template('oxford2/index.html')
    context = {
       'project_list': project_list,
       'current_project': page_url,
    }
    return HttpResponse(template.render(context, request))




