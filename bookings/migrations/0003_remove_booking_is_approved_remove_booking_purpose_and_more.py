# Generated by Django 5.1.6 on 2025-03-18 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='is_approved',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='purpose',
        ),
        migrations.AddField(
            model_name='booking',
            name='approvals_pending',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=20),
        ),
    ]
