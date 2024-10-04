from django.http import HttpResponse
from django.shortcuts import render, redirect
from Mywebsite.models import Quota
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


# Create your views here.
def index(request):
    all_subject = Quota.objects.all()   
    return render(request,"main.html",{"all_subject":all_subject})

def history(request):
    # if request.method == "GET":
    #         Subject = request.GET["subject.Subject"]
    #         Year = request.GET["Year"]
    #         Semester = request.GET["Semester"]
    #         Slot = request.GET["Slot"]
    #         Status = request.GET["Status"]

    #         Quota = Quota.objects.create(
    #             Subject = Subject,
    #             Year = Year,
    #             Semester = Semester,
    #             Slot = Slot,
    #             Status = Status
    #         )
    #     Quota.save()
    return render(request,"history.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username = username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        
        if password == confirm_password:
            try:
                user = User.objects.create_user(username=username, password=password)
                messages.success(request, "Registration successful. You can now log in.")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Passwords do not match.")
    
    return render(request, "register.html")