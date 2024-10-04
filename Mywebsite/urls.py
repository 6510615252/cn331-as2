from django.urls import path
from Mywebsite import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.login_view, name = "login"),
    path('login/', views.login_view, name = "login"),
    path('request/', views.request),
    path('main/', views.index, name = "main"),
    path('register/', views.register),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]