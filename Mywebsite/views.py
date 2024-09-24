from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,"main.html")

def history(request):
    return render(request,"history.html")

def request(request):
    return render(request,"request.html")