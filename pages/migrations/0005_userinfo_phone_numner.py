# Generated by Django 4.2 on 2023-06-19 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_userinfo_profession_alter_userinfo_cv_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='phone_numner',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
