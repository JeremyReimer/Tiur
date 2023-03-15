from django.contrib import admin
from django.urls import include, path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
#   path('admin/', admin.site.urls),
    path('<page_url>/latest/<str:page>', views.pageview, name='pageview',),
    path('<page_url>/latest/', views.pageview, name='pageview', kwargs={'page': 'index.html', }),
    path('<page_url>/latest/<str:directory>/', views.pageview, name='pageview', kwargs={'page': 'index.html'}),
    path('<page_url>/latest/<str:directory>/<str:page>', views.pageview, name='pageview',),
]
