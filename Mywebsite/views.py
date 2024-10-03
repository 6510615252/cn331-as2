from django.http import HttpResponse
from django.shortcuts import render
from Mywebsite.models import Quota

# Create your views here.
def index(request):
    all_subject = Quota.objects.all()   
    return render(request,"main.html",{"all_subject":all_subject})

def history(request):
    if request.method == "GET":
            Subject = request.GET["subject.Subject"]
            Year = request.GET["subject.Year"]
            Semester = request.GET["subject.Semester"]
            Slot = request.GET["subject.Slot"]
            Status = request.GET["subject.Status"]

            Quota = Quota.objects.create(
                Subject = subject,
                Year = Year,
                Semester = Semester,
                Slot = Slot,
                Status = Status
            )
            Quota.save()
    return render(request,"history.html")

def request(request):
    return render(request,"request.html")