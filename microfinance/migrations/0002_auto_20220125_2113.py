# Generated by Django 3.0.5 on 2022-01-25 15:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microfinance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intrestloans',
            name='reminder',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 1, 25, 21, 13, 52, 75859), null=True),
        ),
        migrations.AlterField(
            model_name='loans',
            name='reminder',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 1, 25, 21, 13, 52, 75859), null=True),
        ),
    ]
