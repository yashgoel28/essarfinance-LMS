# Generated by Django 3.0.5 on 2020-05-21 17:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('microfinance', '0008_remove_installments_penalty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installments',
            name='Date_Due',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
