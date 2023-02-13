from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world! This is Oxford 2.0's index.")


