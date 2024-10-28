from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Quota(models.Model):
    Subject = models.CharField(max_length = 20)
    Year = models.IntegerField()
    Semester = models.IntegerField()
    Slot = models.IntegerField()
    Status = models.CharField(max_length = 20)

    def __str__(self):
        return self.Subject + " " + str(self.Year) + " " + str(self.Semester) + " " + str(self.Slot) + " " + str(self.Status)



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    quota = models.ForeignKey(Quota, on_delete=models.CASCADE) 
    approve = models.CharField(max_length = 20, default= 'Pending')


    def __str__(self):
        return f"{self.user.username} enrolled in {self.quota.Subject}"