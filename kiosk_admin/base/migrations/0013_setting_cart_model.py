# Generated by Django 5.1.2 on 2024-10-31 14:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_setting_cart_prompt_setting_prompt'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='cart_model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='settings_cart_model', to='base.llmmodel'),
        ),
    ]
