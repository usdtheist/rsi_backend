# Generated by Django 5.1.6 on 2025-03-06 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_contactus_alter_coin_name_alter_strategy_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstrategy',
            name='amount',
            field=models.FloatField(default=10.0),
        ),
    ]
