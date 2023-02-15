from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<page_url>/', views.pageview, name='pageview'),
]
