from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    department = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    file_upload = models.FileField(upload_to='uploads/', blank=True, null=True)


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def _str_(self):
        return self.name

class Project(models.Model):
    project_name = models.CharField(max_length=255)
    description = models.TextField()
    project_head = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    departments = models.ManyToManyField(Department)
    p1=models.CharField(max_length=100,default="none")
    p2=models.CharField(max_length=100,default="none")
    p3=models.CharField(max_length=100,default="none")

    def _str_(self):
        return self.project_name
class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.OneToOneField(Department, on_delete=models.CASCADE)

class Post(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    post_id = models.AutoField
    project_id1 = models.IntegerField(default=0, null=True) 
    post_content = models.CharField(max_length=5000)
    timestamp= models.DateTimeField(default=now)

    
class Replie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    reply_id = models.AutoField
    reply_content = models.CharField(max_length=5000) 
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default='')
    timestamp= models.DateTimeField(default=now)


class Task(models.Model):
    PRIORITY_CHOICES = [
        (1, 'High'),
        (2, 'Medium'),
        (3, 'Low'),
    ]

    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    due_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    

    def __str__(self):
        return f'{self.description} (Priority: {self.get_priority_display()})'