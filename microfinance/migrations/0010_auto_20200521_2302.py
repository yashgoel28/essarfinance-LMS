# Generated by Django 3.0.5 on 2020-05-21 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microfinance', '0009_auto_20200521_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='penalty',
            name='Date_Ended',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='penalty',
            name='Date_Started',
            field=models.DateTimeField(default=None),
        ),
    ]
