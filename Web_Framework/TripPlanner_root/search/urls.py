from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    path('', views.get_home, name='home'),
    path('our-story/', views.get_our_story, name='our_story'),
    path('contact-us/', views.get_contact_us, name='contact_us'),
    path('search/', views.get_userinfo, name='search'),
    path(r'flight-info/user-id-<pk>/', views.get_flightinfo, name='flight'),
    path(r'accom-info/user-id-<user_id>-flight-id-<flight_id>/', views.get_accominfo, name="accom"),
    path(r'itinerary/user-id-<user_id>-accom-id-<accom_id>/', views.get_path_planning, name="itinerary"),
]

urlpatterns += staticfiles_urlpatterns()
