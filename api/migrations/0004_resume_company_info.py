# Generated by Django 5.1.7 on 2025-03-19 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_rename_job_url_1_resume_recruitment_notice_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='company_info',
            field=models.TextField(blank=True, null=True),
        ),
    ]
