# Generated by Django 4.2.16 on 2024-12-17 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_user_auto_recommended_alter_coin_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userstrategy',
            options={'ordering': ['strategy_id__order']},
        ),
        migrations.AddField(
            model_name='strategy',
            name='order',
            field=models.IntegerField(null=True),
        ),
    ]
