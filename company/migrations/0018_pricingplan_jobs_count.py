# Generated by Django 4.2.1 on 2023-07-04 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0017_companyinfo_purchased_package'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricingplan',
            name='jobs_count',
            field=models.IntegerField(null=True),
        ),
    ]
