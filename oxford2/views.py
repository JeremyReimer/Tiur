from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world! This is Oxford 2.0's index.")

def pageview(request, page_url):
    return HttpResponse("This is the HTML for the %s project." % page_url)



