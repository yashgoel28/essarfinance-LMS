# Generated by Django 3.0.5 on 2020-05-21 17:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microfinance', '0006_auto_20200515_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clients',
            name='Image',
            field=models.ImageField(default='pics/avatar.png', upload_to='pics'),
        ),
        migrations.AlterField(
            model_name='installments',
            name='Date_Due',
            field=models.DateField(default=datetime.date(2020, 5, 21)),
        ),
    ]
