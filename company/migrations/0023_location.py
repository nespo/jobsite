# Generated by Django 4.2.3 on 2023-07-19 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0022_remove_pricingplan_user_type_pricingplan_for_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=100)),
            ],
        ),
    ]
