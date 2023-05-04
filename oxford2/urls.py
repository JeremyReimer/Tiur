from django.contrib import admin
from django.urls import include, path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('setdarkmode', views.set_dark_mode),
    path('rmdarkmode', views.rm_dark_mode),
#    path('admin/', admin.site.urls), # already defined in project views
    path('accounts/', include('django.contrib.auth.urls')),
    path('<page_url>/latest/<str:page>', views.pageview, name='pageview',),
    path('<page_url>/latest/', views.pageview, name='pageview', kwargs={'page': 'index.html', }),
    path('<page_url>/latest/<str:directory>/', views.pageview, name='pageview', kwargs={'page': 'index.html'}),
    path('<page_url>/latest/<str:directory>/<str:page>', views.pageview, name='pageview',),
    path('<page_url>/latest/<str:directory>/<str:subdirectory>/<str:page>', views.pageview, name='pageview',),
    path('<page_url>/latest/<str:directory>/<str:subdirectory>/<str:subsubdir>/<str:page>', views.pageview, name='pageview',),
]
