# Generated by Django 3.0.5 on 2020-05-15 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microfinance', '0005_penalty_penalty_paid_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='penalty',
            name='Percent',
            field=models.FloatField(default=2),
        ),
    ]
