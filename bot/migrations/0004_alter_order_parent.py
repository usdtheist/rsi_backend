# Generated by Django 3.2.25 on 2024-08-19 05:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_order_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sell_order', to='bot.order'),
        ),
    ]
