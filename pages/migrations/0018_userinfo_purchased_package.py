# Generated by Django 4.2.1 on 2023-07-04 10:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0016_remove_subscriptionmodel_company_id_and_more'),
        ('pages', '0017_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='purchased_package',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='company.subscriptionmodel'),
        ),
    ]
