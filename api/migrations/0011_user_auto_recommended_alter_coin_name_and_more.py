# Generated by Django 4.2.16 on 2024-12-12 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20241123_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auto_recommended',
            field=models.BooleanField(default=False),
        ),
    ]
