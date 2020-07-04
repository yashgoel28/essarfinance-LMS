# Generated by Django 3.0.5 on 2020-05-29 14:06

from django.db import migrations, models
import phone_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('microfinance', '0014_auto_20200528_1904'),
    ]

    operations = [
        migrations.AddField(
            model_name='clients',
            name='Knowns_Name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='clients',
            name='Knowns_No',
            field=phone_field.models.PhoneField(blank=True, max_length=31, null=True),
        ),
    ]
