from rest_framework import serializers
from django.contrib.auth.admin import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.core.validators import validate_email as ve
from .models import StudentProfile, ExamScore, UploadMaterial, Notification, UserNotification, StudentReview
import logging


logger = logging.getLogger(__name__)



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'created_at']
        read_only_fields = ['created_at']

class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = ['id', 'notification', 'read']

        

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['user_id', 'fullname', 'nickname', 'age', 'phone_no', 'course', 'profile_pic', 'rank', 'date_joined', 'is_graduated']

        def to_representation(self, instance):
            data = super().to_representation(instance)
            notifications = instance.notifications.order_by('-created_at')[:5]
            data['notifications'] = NotificationSerializer(notifications, many=True)
            return data
        

class StudentReviewSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)

    class Meta:
        model = StudentReview
        fields = ['id', 'student', 'rating', 'review', 'created_at']
        

class StudentRegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(max_length=255)
    nickname = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    phone_no = serializers.CharField()
    course = serializers.CharField()
    profile_pic = serializers.ImageField(required=False, allow_null=True)
    rank = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'fullname', 'nickname', 'age', 'phone_no', 'course', 'profile_pic', 'rank']

    def validate_email(self, value):
        try:
            ve(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Invalid email format.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email address already exists")
        return value

    def create(self, validated_data):
        request_id = self.context.get('request').headers.get("X-Request-ID", "unknown")
        fullname = validated_data.pop('fullname')
        nickname = validated_data.pop('nickname')
        age = validated_data.pop('age')
        phone_no = validated_data.pop('phone_no')
        course = validated_data.pop('course')
        profile_pic = None
        rank = validated_data.pop('rank')
        request = self.context.get('request')
        if request and hasattr(request, 'FILES') and 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']
            logger.info(f"Profile pic file recieved: {profile_pic.name}")
        with transaction.atomic():
            email = validated_data['email']
            password = make_password(validated_data['password'])
            user = User(
                username=email,
                email=email,
                password=password
            )
            user.save()
            if not user.username or user.username != email:
                logger.error(f"Username assignment failed: expected: {email} got: {user.username}, RequestID: {request_id}")
                user.delete()
                raise serializers.ValidationError("Username assignment failed")
            student_profile = StudentProfile.objects.create(
                user=user,
                fullname=fullname,
                nickname=nickname,
                age=age,
                phone_no=phone_no,
                course=course,
                profile_pic=profile_pic,
                rank=rank
            )
            if student_profile.profile_pic:
                logger.info(f"Profile oic saved as: {student_profile.profile_pic.name}, Request ID: {request_id}")
            else:
                logger.warning(f'Warm eba: {request_id}')
        logger.info(f"Profile pic saves as: {student_profile.profile_pic}")
        return user

class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model=StudentProfile
        fields = ['user_id', 'rank']
        read_only_fields = ['user_id']
    
class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'is_staff', 'profile']

    def get_profile(self, obj):
        try:
            student_profile = obj.student_profile
            return StudentProfileSerializer(student_profile, context=self.context).data
        except StudentProfile.DoesNotExist:
            logger.warning(f"User {obj.id} ({obj.email} has no StudentProfile)")
            return None
        
        


class ExamScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamScore
        fields = ['id', 'student', 'title', 'obj', 'debug', 'project', 'overall', 'grade', 'date_uploaded']
        read_only_fields = ['id', 'date_uploaded']


class StudentGraduationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['user_id','is_graduated']
        read_only_fields = ['user_id']

class UploadMaterialSerializer(serializers.ModelSerializer):
    uploaded_date = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UploadMaterial
        fields = ['id', 'course', 'material', 'title', 'uploaded_date', 'size']
        read_only_fields = ['uploaded_date']

    def get_uploaded_date(self, obj):
        return obj.uploaded_date
    
    def get_size(self, obj):
        return round(obj.size / (1024 * 1024), 3)

    


