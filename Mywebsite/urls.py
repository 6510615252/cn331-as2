from django.urls import path
from Mywebsite import views
urlpatterns = [
    path('', views.index),
    path('history/', views.history),
    path('request/', views.request),
]