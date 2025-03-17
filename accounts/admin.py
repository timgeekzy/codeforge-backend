from django.contrib import admin
from .models import StudentProfile, ExamScore, Notification, UserNotification, StudentReview


# Register your models here.
admin.site.register(StudentProfile)
admin.site.register(ExamScore)
admin.site.register(Notification)
admin.site.register(UserNotification)
admin.site.register(StudentReview)

