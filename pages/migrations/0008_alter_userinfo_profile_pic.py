# Generated by Django 4.2 on 2023-06-19 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_remove_userinfo_account_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='profile_pic',
            field=models.FileField(blank=True, null=True, upload_to='static/profile/'),
        ),
    ]
