# Generated by Django 3.2.25 on 2024-07-21 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategy',
            name='rsi_time',
            field=models.CharField(default='1m', max_length=10),
        ),
        migrations.AddField(
            model_name='userstrategy',
            name='amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='rsi_type',
            field=models.IntegerField(),
        ),
    ]
