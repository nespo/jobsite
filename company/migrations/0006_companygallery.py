# Generated by Django 4.2.1 on 2023-06-24 09:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0005_job'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('companies_gallery', models.FileField(blank=True, null=True, upload_to='static/companies_gallery')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.companyinfo')),
            ],
        ),
    ]
