from django.shortcuts import render
from django.http import HttpResponse
from .models import Project

def index(request):
    return HttpResponse("Hello, world! This is Oxford 2.0's index.")

def pageview(request, page_url):
    projects_list = Project.objects.order_by('-name')
    output = "This is the HTML for the %s project." % page_url
    output = output + "\n" + ', '.join([p.name for p in projects_list])
    return HttpResponse(output)



