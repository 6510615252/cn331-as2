# Generated by Django 5.1.1 on 2024-10-05 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Mywebsite', '0003_enrollment'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='approve',
            field=models.CharField(default='pending', max_length=20),
        ),
    ]
