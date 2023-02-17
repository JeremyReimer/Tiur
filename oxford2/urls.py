from django.contrib import admin
from django.urls import include, path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
#   path('admin/', admin.site.urls),
    path('<page_url>/latest/', views.pageview, name='pageview'),
#   re_path(r'<page_url>/latest/.*', views.pageview, name='pageview'),
]
