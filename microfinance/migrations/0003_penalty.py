# Generated by Django 3.0.5 on 2020-05-07 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('microfinance', '0002_auto_20200504_2133'),
    ]

    operations = [
        migrations.CreateModel(
            name='Penalty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date_Started', models.DateField(default=None)),
                ('Date_Ended', models.DateField(default=None, null=True)),
                ('Amount', models.FloatField(default=0)),
                ('Percent', models.FloatField(default=5)),
                ('Penalty_Calc', models.FloatField(default=0)),
                ('Status', models.BooleanField(default=False)),
                ('Installment', models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, to='microfinance.Installments')),
                ('Loan', models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, to='microfinance.Loans')),
            ],
        ),
    ]
