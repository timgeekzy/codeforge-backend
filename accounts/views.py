from rest_framework import generics, status
import rest_framework.filters
import rest_framework.pagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
import rest_framework
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from .serializers import (
    StudentRegistrationSerializer, UserSerializer,
    ExamScoreSerializer, StudentGraduationSerializer,
    UploadMaterialSerializer, RankSerializer,
    NotificationSerializer, UserNotificationSerializer,
    StudentReviewSerializer
)
import logging
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db import transaction
from django.contrib.auth.models import User
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from .models import ExamScore, StudentProfile, UploadMaterial, UserNotification, Notification, StudentReview
from django.utils.timezone import now

logger = logging.getLogger(__name__)

# Create your views here.
def student_count_view(request):
    total_students = StudentProfile.objects.count()
    data = {
        'total_students':total_students
    }
    return JsonResponse(data)

class StudentReviewListCreateView(generics.ListCreateAPIView):
    queryset = StudentReview.objects.all()
    serializer_class = StudentReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        student_profile = StudentProfile.objects.get(user=self.request.user)
        serializer.save(student=student_profile)

class AcademyAverageRatingView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        average_rating = StudentReview.average_rating()
        return Response({'average_rating': average_rating})

class StudentRegistrationView(generics.CreateAPIView):
    serializer_class = StudentRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        request_id = request.headers.get('X-Request-ID', 'unknown')
        logger.info(f'Recieve request data: {request.data} {request.FILES}')

        cache_key = f"register_request_{request_id}"
        if cache.get(cache_key):
            logger.warning(f"Dublicate request detected for ID: {request_id}")
            return Response({'detail': "Request already processed"}, status=status.HTTP_400_BAD_REQUEST)
        
        cache.set(cache_key, True, timeout=60)
        with transaction.atomic():
            email = request.data.get('email', '')
            User.objects.select_for_update().filter(username=email)
            
            if User.objects.filter(username=email).exists():
                logging.warning(f"User with email {email} already exist, Request ID: {request_id}")
                return Response({'email': ['A user with email already exist']})
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f'Created user with ID: {user.id}')
            return Response({"detail": "Registration successful"}, status=status.HTTP_201_CREATED)
        logger.error(f'Valodation errors: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if user and user.is_staff:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id})
        return Response({'error': 'User not an admin'}, status=status.HTTP_401_UNAUTHORIZED)

class StudentLoginView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id})
        return Response({'error': "User does'nt exist"}, status=status.HTTP_401_UNAUTHORIZED)

class BroadcastNotificationCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = NotificationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification =  Notification.objects.create(
            title=serializer.validated_data['title'],
            message=serializer.validated_data['message']
        )

        return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
    
class UserNotificationListView(generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user).select_related('notification')

class MarkNotificationAsReadAPIView(generics.UpdateAPIView):
    queryset = UserNotification.objects.all()
    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
       serializer.save(read=True, read_at=now)

class StudentListView(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = rest_framework.pagination.PageNumberPagination
    filter_backends = [rest_framework.filters.SearchFilter, rest_framework.filters.OrderingFilter]
    search_fields = ['studentprofile_fullname']
    ordering_fields = ['id', 'email']

    def get_queryset(self):
        return User.objects.filter(is_staff=False, student_profile__isnull=False)
    
    def list(self, request, *args, **kwargs):
        # token = request.auth
        # if not token or not token.user.is_staff:
        #     logger.info(f'Error: {request.data}')
        #     return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)
    

class UploadExamScoreView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        student_id = request.data.get('student')
        student = get_object_or_404(StudentProfile, user_id=student_id)
        serializer = ExamScoreSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(student=student)
            return Response({'success': 'Result successfully uploaded'}, status=status.HTTP_201_CREATED)
        return Response({'Error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
    
class ExamScoreView(generics.ListAPIView):
    queryset = ExamScore.objects.all()
    serializer_class = ExamScoreSerializer
    permission_classes = [IsAdminUser]


class UpdateGraduationStatusView(generics.UpdateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentGraduationSerializer
    lookup_field = 'pk'

    def put(self, request, pk):
        try:
            student = StudentProfile.objects.get(pk=pk)
        except StudentProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = StudentGraduationSerializer(student, data=request.data)
       
        if serializer.is_valid():
            serializer.save()
            student.refresh_from_db()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UploadMaterialViewSet(ModelViewSet):
    queryset = UploadMaterial.objects.all()
    serializer_class = UploadMaterialSerializer

    def perform_create(self, serializer):
        file = self.request.FILES['material']
        size = file.size 
        serializer.save(size=size)

    @action(methods=['get'], detail=True)
    def download(self, request, pk=None):
        pdf_file = get_object_or_404(UploadMaterial, pk=pk)
        response = FileResponse(pdf_file.material, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_file.title}"'
        return response


class RankUpdateView(APIView):
    queryset = StudentProfile.objects.all()
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        try:
            student = StudentProfile.objects.get(pk=pk)
        except StudentProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RankSerializer(student, data=request.data)

        if serializer.is_valid():
            serializer.save()
            student.refresh_from_db()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class NotificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            notification = serializer.save()
            notification.users.add(*User.objects.all())
            for student_detail in StudentProfile.objects.all():
                student_detail.notifications.add(notification)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        