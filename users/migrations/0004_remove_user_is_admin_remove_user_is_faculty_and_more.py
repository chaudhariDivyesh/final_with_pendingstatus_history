# Generated by Django 5.1.6 on 2025-03-19 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_authority_remove_user_authority_userauthority_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_admin',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_faculty',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_student',
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('faculty', 'Faculty'), ('student', 'Student')], default='student', max_length=10),
        ),
    ]
