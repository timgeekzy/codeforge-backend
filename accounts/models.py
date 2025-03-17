from django.db import models 
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db.models import Avg
User = get_user_model()
# Create your models here.

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    recipients = models.ManyToManyField(User, through='UserNotification')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        users = User.objects.filter(is_active=True)

        UserNotification.objects.bulk_create(
            [
                UserNotification(user=user, notification=self)
                for user in users
            ]
        )


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'notification')



class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student_profile')
    fullname = models.CharField(max_length=255)
    nickname = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    phone_no = models.CharField(default='-', max_length=25)
    course = models.CharField()
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    rank = models.CharField(default='Rookie I', max_length=50)
    date_joined = models.DateField(default=now)
    is_graduated = models.BooleanField(default=False)
    
    def __str__(self):
        return self.fullname
    
    


class StudentReview(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    rating = models.FloatField(default=0.0)
    review = models.TextField(max_length=700)
    created_at = models.DateField(auto_now_add=now)

    def __str__(self):
        return f'Review by: {self.student.user.username}'
    
    @classmethod
    def average_rating(cls):
        return cls.objects.aggregate(Avg('rating'))['rating__avg'] or 0.0

class ExamScore(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, default='Exam 1')
    obj = models.PositiveIntegerField()
    debug = models.PositiveIntegerField()
    project = models.PositiveIntegerField()
    overall = models.PositiveIntegerField(default=0)
    grade = models.CharField(max_length=10, default='')
    date_uploaded = models.DateField(default=now)

class UploadMaterial(models.Model):
    course = models.CharField(max_length=255)
    material = models.FileField(upload_to='pdf_files/')
    title = models.CharField(max_length=255)
    uploaded_date = models.DateField(default=now)
    size = models.IntegerField(null=True, blank=True)



