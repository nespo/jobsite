# Generated by Django 4.2 on 2023-06-23 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0014_user_is_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='is_company',
            field=models.BooleanField(default=False),
        ),
    ]
