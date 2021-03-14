from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_userinfo, name='index'),
    path(r'flight-info/<pk>/', views.get_flightinfo, name='flight'),
]