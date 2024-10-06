from django.urls import path
from Mywebsite import views
from django.contrib.auth import views as auth_views
from .views import register_quota
from .views import cancel_quota
urlpatterns = [
    path('', views.login_view, name = "login"),
    path('login/', views.login_view, name = "login"),
    path('history/', views.history, name='history'),
    path('main/', views.index, name = "main"),
    path('register/', views.register),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register_quota/', register_quota, name='register_quota'),
    path('cancel_quota/', cancel_quota, name = 'cancel_quota'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    

]