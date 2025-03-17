from django.urls import path, include
from .views import (
    StudentRegistrationView, AdminLoginView,
    StudentListView, UploadExamScoreView,
    ExamScoreView, UpdateGraduationStatusView,
    StudentLoginView, UploadMaterialViewSet,
    RankUpdateView, 
    MarkNotificationAsReadAPIView, UserNotificationListView,
    BroadcastNotificationCreateAPIView, student_count_view,
    StudentReviewListCreateView, AcademyAverageRatingView
)
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'admin/upload-material', UploadMaterialViewSet)
urlpatterns = [
    path('register/', StudentRegistrationView.as_view(), name='register_student'),
    path('review/', StudentReviewListCreateView.as_view(), name='review-list'),
    path('rating/', AcademyAverageRatingView.as_view(), name='acad-rating'),
    path('', include(router.urls)),
    path('login/', StudentLoginView.as_view(), name='login_student'),
    path('notification/', UserNotificationListView.as_view(), name='user-notification'),
    path('notification/<int:id>/read/', MarkNotificationAsReadAPIView.as_view(), name='mark-read'),
    path('admin/notification/', BroadcastNotificationCreateAPIView.as_view(), name='send-notification'),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin/students/', StudentListView.as_view(), name='student_list'),
    path('admin/upload-result/', UploadExamScoreView.as_view(), name='upload_result'),
    path('admin/result/', ExamScoreView().as_view(), name='result'),
    path('admin/rank-update/<int:pk>/', RankUpdateView.as_view()),
    path('admin/update-graduation/<int:pk>/', UpdateGraduationStatusView().as_view(), name='update_graduation'),
    path('student-count/', views.student_count_view, name='student_count')
]
