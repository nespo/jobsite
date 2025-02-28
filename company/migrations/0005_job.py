# Generated by Django 4.2.1 on 2023-06-24 08:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0004_alter_companyinfo_company_website_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(max_length=100)),
                ('job_description', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=20)),
                ('categories', models.CharField(max_length=100)),
                ('job_type', models.CharField(max_length=100)),
                ('designation', models.CharField(max_length=100)),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('qualification', models.CharField(max_length=100)),
                ('job_skills', models.CharField(max_length=100)),
                ('last_date', models.DateField()),
                ('country', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('zipcode', models.CharField(max_length=20)),
                ('posted_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
