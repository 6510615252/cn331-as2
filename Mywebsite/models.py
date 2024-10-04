from django.db import models

# Create your models here.

class Quota(models.Model):
    Subject = models.CharField(max_length = 20)
    Year = models.IntegerField()
    Semester = models.IntegerField()
    Slot = models.IntegerField()
    Status = models.CharField(max_length = 20)

    def __str__(self):
        return self.Subject + " " + str(self.Year) + " " + str(self.Semester) + " " + str(self.Slot) + " " + str(self.Status)