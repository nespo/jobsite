# Generated by Django 4.2.1 on 2023-06-26 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0013_jobcategory_pricingplan'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
