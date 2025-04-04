# Generated by Django 5.1.6 on 2025-03-17 00:51

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='student_profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('fullname', models.CharField(max_length=255)),
                ('nickname', models.CharField(max_length=50)),
                ('age', models.PositiveIntegerField()),
                ('phone_no', models.CharField(default='-', max_length=25)),
                ('course', models.CharField()),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('rank', models.CharField(default='Rookie I', max_length=50)),
                ('date_joined', models.DateField(default=django.utils.timezone.now)),
                ('is_graduated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='UploadMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.CharField(max_length=255)),
                ('material', models.FileField(upload_to='pdf_files/')),
                ('title', models.CharField(max_length=255)),
                ('uploaded_date', models.DateField(default=django.utils.timezone.now)),
                ('size', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExamScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Exam 1', max_length=50)),
                ('obj', models.PositiveIntegerField()),
                ('debug', models.PositiveIntegerField()),
                ('project', models.PositiveIntegerField()),
                ('overall', models.PositiveIntegerField(default=0)),
                ('grade', models.CharField(default='', max_length=10)),
                ('date_uploaded', models.DateField(default=django.utils.timezone.now)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='StudentReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField(default=0.0)),
                ('review', models.TextField(max_length=700)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.studentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read', models.BooleanField(default=False)),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.notification')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'notification')},
            },
        ),
        migrations.AddField(
            model_name='notification',
            name='recipients',
            field=models.ManyToManyField(through='accounts.UserNotification', to=settings.AUTH_USER_MODEL),
        ),
    ]
